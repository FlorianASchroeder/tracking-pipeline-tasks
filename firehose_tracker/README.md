# How to start

### Prerequisites

To setup the python venv execute:
```sh
# From repo root
cd firehose_tracker
poetry install
```

### How to use

This tracker package can be used in other applications as:
```py
from firehose_tracker.tracker import Tracker

data = {"event_type": "page_view", "user_id": 1}

tracker = Tracker("firehose-tracker", data["event_type"])
tracker.ensure_active()
tracker.put_record(data)
```

The settings defined in `firehose_tracker.config` can be adjusted by environment variables.
These are the options:

| Option                     | ENV Variable                                | default                                                                                      | Info                                                                                                   |
|----------------------------|---------------------------------------------|----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| REGION_NAME                | FIREHOSE_TRACKER_REGION_NAME                | eu-central-1                                                                                 | The default AWS region for firehose delivery.                                                          |
| ROLE_ARN                   | FIREHOSE_TRACKER_ROLE_ARN                   | arn:aws:iam::339712828249:role/FirehoseAssumeRole                                            | The ARN of the IAM role for firehose delivery.                                                         |
| BUCKET_ARN                 | FIREHOSE_TRACKER_BUCKET_ARN                 | arn:aws:s3:::firehose-tracker-data                                                           | The ARN of the S3 bucket for firehose tracking.                                                        |
| FIX_NEWLINE_LAMBDA_ARN     | FIREHOSE_TRACKER_FIX_NEWLINE_LAMBDA_ARN     | arn:aws:lambda:eu-central-1:339712828249:function:firehose-transformations-dev-fix-newline:1 | The ARN of the lambda function for adding newlines to records exported to S3. Required for AWS Athena. |
| SIZE_IN_MBS                | FIREHOSE_TRACKER_SIZE_IN_MBS                | 128                                                                                          | The size of each firehose tracking object in megabytes.                                                |
| INTERVAL_IN_SECONDS        | FIREHOSE_TRACKER_INTERVAL_IN_SECONDS        | 300                                                                                          | The interval in seconds for sending firehose tracking data.                                            |
| COMPRESSION_FORMAT         | FIREHOSE_TRACKER_COMPRESSION_FORMAT         | UNCOMPRESSED                                                                                 | The compression format for the firehose tracking data.                                                 |
| CLOUDWATCH_LOGGING_ENABLED | FIREHOSE_TRACKER_CLOUDWATCH_LOGGING_ENABLED | True                                                                                         | Whether to enable cloudwatch logging for the firehose delivery stream.                                 |
| LOG_GROUP_NAME             | FIREHOSE_TRACKER_LOG_GROUP_NAME             | /aws/kinesisfirehose/firehose-tracker-delivery                                               | The name of the cloudwatch log group for the firehose delivery stream.                                 |
| STREAM_CREATION_TIMEOUT    | FIREHOSE_TRACKER_STREAM_CREATION_TIMEOUT    | 60                                                                                           | The timeout in seconds for creating the firehose delivery stream.                                      |
