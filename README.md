# Tracking pipeline

## Initial considerations

The goal of this project is to track events coming from an HTTP microservice to track events coming from multiple applications and to submit them to a data lake.
The pipeline shall be able to handle a fluctuating rate of events, between 500 events per second to 4000 events per second.
The payload size is between 0.5KB - 4KB.
The payload is a flat structure of string key/value pairs with many common fields, but also custom fields depending on the application sending the events.
The data freshness required is a trailing 1hr window.
### Preliminary Questions to assess
* Shall the HTTP microservice be implemented as well? 
  * I guess the firehose client is meant to be used as a package and will be deployed on AWS lambda as part of the microservice
  * -> assumption: no
* What is the name of the stream to be created and used? 
  * -> define as config from env var
* what will be the destination?
  * assumption: S3 for now as that can support Redshift and Athena for subsequent analysis


### AWS Firehose assessment

* Advantages:
  * Auto-scaling
  * Send to multiple destination supported (e.g. S3, Redshift)
  * Internal batching is suitable to support 1hr freshness window
  * Up to 2000 delivery streams per region supported

* Disadvantages
  * A single firehose stream can only process (in EU): 100k records/s, 1k requests/s, 1 MiB/s
    -> not fully auto-scaling
  * records in batched S3 deliveries are not newline-delimited. In order to process data in Athena, an additional lambda data transformation step needs to be added.

* Pricing:
  * Volume-based in 5KB steps: $0.033/month
  * Min: 5KB*500/s = 5Kb * 500 * 60*60*24*30 /month = 6.48TB/month -> $210/month
  * Max: 5KB*4000/s = 51.84 TB/month -> $1710/month

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

* Alternatives:
  * Kinesis Streams:
    * but: near real-time processing not required (1hr trailing window sufficient)
    * but: manual control of sharding required to ensure throughput (eg at least 16 shards in this case to support peak)
    * but: scale-up/-down takes 30 seconds per shard (eg from 2 to 16 shards will take 7 minutes) -> better for slowly changing event rates

  * Kafka Connect:
    * Easy to setup
    * e.g. support streaming inserts into Google BigQuery -> allows real-time analytics
    * but: requires AWS MSK and Kafka topic, incurring costs
    * can handle throughput of at least 40MB/s (10k events/s) using m5.4xlarge priced at $550/month
    * Including broker and storage charges ($0.10/GB/month), costs are way above Firehose
  
  * Snowplow:
    * well-matured ecosystem with variety of trackers, pipeline options and pre-defined dbt models available
    * reduce engineering time spent on developing an own, proprietary tracking solution
    * easy to deploy with terraform, but surely requires tweaking for high-throughput scenarios
    * instead spend engineering time configuring, operating, monitoring all components. Yet, a lot of that time is also required for proprietary solution.
    * can cost up to $4500/mo at 3000 events/s avg rate ([reference](https://discourse.snowplow.io/t/recent-cost-information-for-snowplow/2694/2)).


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

* This tracker will be used in a single microservice to push event data, but could also be integrated in several services
* Each microservice or application defines a list of event types that it will track
* For each event_type I will use:
  * a dedicated delivery stream to ensure that the firehose quota limits are not reached
  * a dedicated log stream
* To keep it simple:
  * 1 S3 bucket will receive all tracking data. Folder pattern will be default for now.
  * 1 cloudwatch log group
