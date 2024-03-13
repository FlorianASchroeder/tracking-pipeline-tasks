from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the firehose tracker.
    The settings are loaded from environment variables, prefixed with "FIREHOSE_TRACKER_".
    E.g. "FIREHOSE_TRACKER_ROLE_ARN" will be loaded into the ROLE_ARN attribute.

    Attributes:
        REGION_NAME (str): The default AWS region for firehose delivery.
        ROLE_ARN (str): The ARN of the IAM role for firehose delivery.
        BUCKET_ARN (str): The ARN of the S3 bucket for firehose tracking.
        FIX_NEWLINE_LAMBDA_ARN (str): The ARN of the lambda function for adding newlines to records exported to S3. Required for AWS Athena.
        SIZE_IN_MBS (int): The size of each firehose tracking object in megabytes.
        INTERVAL_IN_SECONDS (int): The interval in seconds for sending firehose tracking data.
        COMPRESSION_FORMAT (str): The compression format for the firehose tracking data.
        CLOUDWATCH_LOGGING_ENABLED (bool): Whether to enable cloudwatch logging for the firehose delivery stream.
        LOG_GROUP_NAME (str): The name of the cloudwatch log group for the firehose delivery stream.
        STREAM_CREATION_TIMEOUT (int): The timeout in seconds for creating the firehose delivery stream.
    """

    model_config = SettingsConfigDict(env_prefix="FIREHOSE_TRACKER_")

    REGION_NAME: str = "eu-central-1"
    ROLE_ARN: str = "arn:aws:iam::339712828249:role/FirehoseAssumeRole"
    BUCKET_ARN: str = "arn:aws:s3:::firehose-tracker-data"
    FIX_NEWLINE_LAMBDA_ARN: str = (
        "arn:aws:lambda:eu-central-1:339712828249:function:firehose-transformations-dev-fix-newline:1"
    )
    # PREFIX: str = "app_name/!{timestamp:yyyy/MM/dd}/"
    # ERROR_OUTPUT_PREFIX: str = (
    #     "app_name_errors/!{firehose:error-output-type}/!{timestamp:yyyy/MM/dd}/"
    # )
    SIZE_IN_MBS: int = 128
    INTERVAL_IN_SECONDS: int = 300
    COMPRESSION_FORMAT: str = "UNCOMPRESSED"
    CLOUDWATCH_LOGGING_ENABLED: bool = True
    LOG_GROUP_NAME: str = "/aws/kinesisfirehose/firehose-tracker-delivery"
    STREAM_CREATION_TIMEOUT: int = 60
