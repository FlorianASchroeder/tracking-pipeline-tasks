# Tracking pipeline

## Initial considerations

The goal of this project is to track events coming from an HTTP microservice to track events coming from multiple applications and to submit them to a data lake.
The pipeline shall be able to handle a fluctuating rate of events, between 500 events per second to 4000 events per second.
The payload size is between 0.5KB - 4KB.
The payload is a flat structure of string key/value pairs with many common fields, but also custom fields depending on the application sending the events.
The data freshness required is a trailing 1hr window.

### Preliminary Questions 
* Shall the HTTP microservice be implemented as well? 
  * I guess the firehose client is meant to be used as a package and will be deployed on AWS lambda as part of the microservice
  * -> assumption: no
* What is the name of the stream to be created and used? 
  * -> define as config from env var
* What will be the destination?
  * assumption: S3 for now as that can support Redshift and Athena for subsequent analysis


### AWS Firehose assessment

* Advantages:
  * Auto-scaling (serverless)
  * Send to variety of destinations supported (e.g. S3, Redshift)
  * Internal batching is suitable to support 1hr freshness window
  * Up to 2000 delivery streams per region supported
  * Relatively easy to setup
  * Cost effective at low volumes
  * Additional data encryption possible

* Disadvantages
  * A single firehose delivery stream can only process (in EU): 100k records/s, 1k requests/s, 1 MiB/s
    -> not fully auto-scaling as event split across streams has to be managed at large volumes
  * records in batched S3 json deliveries are not newline-delimited. In order to process data in Athena, an additional lambda data transformation step needs to be added. (see: [firehose-transformations](firehose-transformations/README.md))
* Long-term critique
  * Vendor lock-in on AWS. This is a smaller problem, as long as the company strategy is to stay with AWS. Kafka would be a suitable alternative.
  * Cost scales with data volume and starts at 5KB min.:
    * Less cost-efficient for <1KB payloads especially at high rates
    * Can become increasingly expensive if payload increases > 5KB
  * Convenience features like `format conversion` and `dynamic partitioning` that would reduce engineering+operational efforts increase cost by 2-3x, reaching similar price-levels as Kafka
  * No fan-out possible, only 1 single destination allowed per delivery stream. If multiple destinations are required, the tracker would require to submit each event to multiple delivery streams. If instead the tracking message is inserted into a Kinesis data stream or Kafka topic (once), then the fan-out can be setup downstream, without making changes to the tracker.

* Pricing:
  * Volume-based in 5KB steps: $0.033/GB/month
    * Min: 5KB*500/s = 5Kb * 500 * 60*60*24*30 /month = 6.48TB/month -> $210/month
    * Max: 5KB*4000/s = 51.84 TB/month -> $1710/month
  * Format conversion to parquet (no 5KB steps): $0.02/GB
    * Min: 0.5KB*500/s = 648GB/mo -> $13/month
    * Max: 5KB*4000/s = 51.84TB/mo -> $1036/month
    * Depending on avg records size and traffic, this can be cheap or increase costs by 60% (in Max case)
    

* Monitoring:
  * CloudWatch logging for error logs
  * By default, error output will be sent to dedicated S3 prefix that can be queried via AWS Athena
  * Firehose delivery stream metrics can be used to setup alerts, e.g. alert when
    * throttled records reach certain max value
    * Incoming bytes/put requests / records hit the quota limit
    * S3 data freshness is lower than 1hr
    * S3 delivery success is below min threshold, e.g. 98%
  * AWS Lambda monitoring can be used to setup alerts, e.g. when
    * throttles reach a certain max value
    * Error rate is above a threshold
  * DBT freshness checks can be setup to detect interruptions in the tracking pipeline

* Alternatives:
  * Kinesis Streams:
    * Added flexibilit: Will allow stream processing (e.g. session attribution fix) and fan-out of destinations
    * but: near real-time processing not required (1hr trailing window sufficient)
    * but: manual control of sharding required to ensure throughput (eg at least 16 shards in this case to support peak)
    * but: scale-up/-down takes 30 seconds per shard (eg from 2 to 16 shards will take 7 minutes) -> better for slowly changing event rates

  * Kafka Connect:
    * Easy to setup: only configure the connector, no code required
    * ksqlDB allows stream processing (e.g. session attribution fix)
    * Kafka topics enable fan-out
    * but: requires AWS MSK and Kafka topic, incurring costs
    * can handle throughput of at least 40MB/s (10k events/s) using m5.4xlarge priced at $550/month
    * Including broker and storage charges ($0.10/GB/month), costs are way above Firehose
  
  * Snowplow:
    * well-matured ecosystem with variety of trackers, pipeline options (on Kinesis, Kafka, Pub-Sub) and pre-defined dbt models available
    * Vendor lock-in only on protocol-level, not infrastructure!
    * reduce engineering time spent on developing an own, proprietary tracking solution
    * instead spend engineering time configuring, operating, monitoring all components. Yet, a lot of that time is also required for proprietary solution.
    * easy to deploy with terraform, but surely requires tweaking for high-throughput scenarios
    * can cost up to $4500/mo at 3000 events/s avg rate ([reference](https://discourse.snowplow.io/t/recent-cost-information-for-snowplow/2694/2)) as it employs more infrastructure components to support a wider set of processing use cases.


## Main Considerations

* At peak, this needs to support a throughput of 16 MB/s, so at least 16 delivery streams would be required.
  There are several ways how to support the maximum throughput:
  * Use **dynamic partitioning** which supports up to 1GB/s throughput
    * Advantage: lower engineering complexity, less effort in long-term maintenance
    * Downside: increases cost by 60% ($0.02 per GB)
    * Avoid this as cost-sensitivity was mentioned during interviews.
  * split into separate **streams by event type** (and by app?)
    * Requires more than 16 event types and a relatively even distribution of events onto event types.
    * Requires `#event_types < 2000` due to quota of maximum firehose delivery streams per region (should not be a problem).
    * In this case all streams can be created before deployment using TF
    * Addition of new event types can be done quick and easy via PR + Release
  * split into dedicated **streams by lambda worker**.
    * inherent rate limit based on the microservice performance.
      * Does not work if performance > 1k requests/s.
      * Does not work if performance < 2 requests/s as limited by #delivery streams.
    * Requires creating delivery streams on demand whenever a new lambda worker is being started.
    * Requires removing delivery streams when lambda function shuts down (requires Python 3.12)
    * Avoid this for now, as it will cause a large cold start time of 10-40 seconds. This can be compensated by optimising lambda scaling behaviour but is out of scope here.
  -> for now, choose: **streams by event type**
* Throughput can be increased and cost can be reduced by micro-batching events in a write buffer in the tracker into 5KB chunks before inserting them into the delivery stream.
  * e.g. at 0.5KB payload size per event, this would reduce costs by factor 10.
  * increased complexity to avoid losing un-committed tracking data or delayed delivery: the write buffer needs to be flushed before application shutdown and on regular intervals to ensure data is timely and complete.
  * assume this is out of scope here.
* This tracker will be used in a single microservice to push event data, but could also be integrated in several services
* Each microservice or application defines a list of event types that it will track
* For each event_type I will use:
  * a dedicated delivery stream to ensure that the firehose quota limits are not reached
  * a dedicated log stream
* To keep it simple:
  * 1 S3 bucket will receive all tracking data. Folder pattern will be default for now.
  * 1 cloudwatch log group
* As output file format I choose `jsonl` as this provides the largest freedom in terms of varying schema with custom fields between different event types.
  * alternatively `parquet` is a better option, as its columnar storage format and advanced partitioning allows for better reduction of scanned data during Athena queries, improving query speed and reducing costs. I did not use it yet, as it would incur further costs
  * If tracking payload is specified more precisely, yet with unspecified custom field, one could use instead a delimited storage format where all custom fields are nested in a dedicated string field, while all shared fields are stored in a well-defined and delimited order. This allows omitting the keys which would in turn save data volume. For this, an appropriate delimiter would need to be defined.
    Since the ingestion is priced at 5KB steps, there is no advantage in reducing the payload futher (unless parquet storage is chosen). Thus choose `jsonl` as storage format instead.
* Creation of AWS resources performed via terraform to reduce click-pain and support long-term maintenance. Some base delivery streams are also created here for convenience

## Components
* [tracker-infra](./tracker-infra/README.md): Terraform scripts to setup AWS resources
* [firehose_tracker](./firehose_tracker/README.md): Python package containing the implementation of the AWS Firehose tracker
* [firehose-transformation](./firehose-transformations/README.md): JS serverless.com data transformation to create proper newline-separated `.jsonl` output
* [tracker-app](./tracker-app/README.md): Simple FastAPI tracker application for quick testing
* [session_attribution_fix](./session_attribution_fix/README.md): dbt project to fix session attribution in the DWH

### How to run
1. Setup AWS credentials, e.g. in `.env` with admin rights
2. Deploy `firehose-transformation`
3. Provision `tracker-infra`
4. Deploy `tracker-app`
5. Send traffic
