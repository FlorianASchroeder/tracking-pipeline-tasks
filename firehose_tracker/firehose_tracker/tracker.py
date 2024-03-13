import json
import logging
from time import sleep
from typing import Dict, Optional

import boto3
import botocore
from firehose_tracker.config import Settings

logger = logging.getLogger(__name__)
config = Settings()


class SingletonMeta(type):
    """
    A metaclass for creating singleton classes.
    """

    _instances: Dict[str, type] = {}

    def __call__(cls, *args, **kwargs):
        signature = f"{cls.__name__}{args}{kwargs}"
        if signature not in cls._instances:
            cls._instances[signature] = super(SingletonMeta, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[signature]


class Tracker(metaclass=SingletonMeta):
    """
    A class to interact with AWS Kinesis Firehose.

    Example usage:
    ```
    tracker = Tracker("test-tracking-stream", "suffix-1", "eu-central-1")
    tracker.ensure_active()
    response = tracker.put_record({"test": "data"})
    response = tracker.delete_delivery_stream()
    ```
    """

    def __init__(
        self,
        delivery_stream_base_name: str,
        stream_suffix: str,
        region_name: str = config.REGION_NAME,
    ):
        self.stream_suffix = stream_suffix
        self.region_name = region_name
        self.delivery_stream_base_name = delivery_stream_base_name
        self.firehose_client = boto3.client(
            "firehose",
            region_name=self.region_name,
        )
        self.active = False

    def get_delivery_stream_status(self):
        try:
            response = self.firehose_client.describe_delivery_stream(
                DeliveryStreamName=self.get_delivery_stream_name()
            )
            return response["DeliveryStreamDescription"]["DeliveryStreamStatus"]
        except botocore.exceptions.ClientError as e:
            logger.info(e)
            return "NOT_FOUND"

    def ensure_active(
        self, retry_wait: int = 5, max_retry_override: Optional[int] = None
    ):
        """Ensure the delivery stream is active.

        If the delivery stream does not exist, it will be created.
        If a previous delivery stream failed to be created, it will be deleted and recreated.

        STREAM_CREATION_TIMEOUT is the maximum time to wait for the delivery stream to become active.

        Raises:
            Exception: If the delivery stream status is "DELETION_FAILED".
        """
        max_retries = max_retry_override or config.STREAM_CREATION_TIMEOUT // retry_wait
        retries = 0
        while not self.active and retries < max_retries:
            retries += 1
            status = self.get_delivery_stream_status()
            logger.info(
                f"Checking delivery stream status... {retries}/{max_retries}: {status}"
            )
            if status == "NOT_FOUND":
                self.create_delivery_stream()
                logger.debug("Creating delivery stream...")
            elif status == "ACTIVE":
                self.active = True
                logger.debug("Delivery stream is active.")
                return
            elif status == "CREATE_FAILED":
                self.delete_delivery_stream()
                logger.debug("Deleting delivery stream...")
            elif status == "DELETION_FAILED":
                raise Exception(
                    "Delivery stream deletion failed."
                )  # TODO: add custom exception
            elif status in ["CREATING", "DELETING"]:
                pass
            sleep(retry_wait)

    def create_delivery_stream(self):
        response = self.firehose_client.create_delivery_stream(
            DeliveryStreamName=self.get_delivery_stream_name(),
            DeliveryStreamType="DirectPut",
            ExtendedS3DestinationConfiguration={
                "RoleARN": config.ROLE_ARN,
                "BucketARN": config.BUCKET_ARN,
                # TODO: add prefix config if required.
                # "Prefix": config.PREFIX,
                # "ErrorOutputPrefix": config.ERROR_OUTPUT_PREFIX,
                "BufferingHints": {
                    "SizeInMBs": config.SIZE_IN_MBS,
                    "IntervalInSeconds": config.INTERVAL_IN_SECONDS,
                },
                "ProcessingConfiguration": {
                    "Enabled": True,
                    "Processors": [
                        {
                            "Type": "Lambda",
                            "Parameters": [
                                {
                                    "ParameterName": "LambdaArn",
                                    "ParameterValue": config.FIX_NEWLINE_LAMBDA_ARN,
                                },
                            ],
                        },
                    ],
                },
                "CompressionFormat": config.COMPRESSION_FORMAT,
                "CloudWatchLoggingOptions": {
                    "Enabled": config.CLOUDWATCH_LOGGING_ENABLED,
                    "LogGroupName": config.LOG_GROUP_NAME,
                    "LogStreamName": self.get_log_stream_name(),
                },
                "FileExtension": ".jsonl",
            },
        )
        return response

    def delete_delivery_stream(self):
        response = self.firehose_client.delete_delivery_stream(
            DeliveryStreamName=self.get_delivery_stream_name()
        )
        return response

    def get_delivery_stream_name(self):
        return f"{self.delivery_stream_base_name}-delivery-stream-{self.stream_suffix}"

    def get_log_stream_name(self):
        return f"stream-errors-{self.stream_suffix}"

    def put_record(self, record):
        self.ensure_active()
        response = self.firehose_client.put_record(
            DeliveryStreamName=self.get_delivery_stream_name(),
            Record={"Data": json.dumps(record)},
        )
        return response

    def put_records(self, records: list):
        self.ensure_active()
        response = self.firehose_client.put_record_batch(
            DeliveryStreamName=self.get_delivery_stream_name(),
            Records=[{"Data": json.dumps(record)} for record in records],
        )
        return response
