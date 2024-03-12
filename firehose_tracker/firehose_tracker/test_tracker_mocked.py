from unittest.mock import patch

import moto

from .tracker import Tracker


class TestTrackerMocked:
    """A class to test the Tracker class with moto.
    All calls to AWS services are mocked.
    """

    @moto.mock_aws
    def test_create_delivery_stream(self):
        tracker = Tracker(
            "test-tracking-stream",
            "suffix-1",
            "eu-central-1",
        )
        response = tracker.create_delivery_stream()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @patch("boto3.client")
    def test_delete_delivery_stream(self, mock_boto_client):
        tracker = Tracker(
            "test-tracking-stream",
            "suffix-1",
            "eu-central-1",
        )
        _response = tracker.delete_delivery_stream()
        assert tracker.firehose_client.delete_delivery_stream.called

    @patch("boto3.client")
    def test_get_delivery_stream_status(self, mock_boto_client):
        tracker = Tracker("firehose-tracker", "checkout", "eu-central-1")
        _response = tracker.get_delivery_stream_status()
        assert tracker.firehose_client.describe_delivery_stream.called

    @patch("boto3.client")
    def test_ensure_active_active(self, mock_boto_client):
        mock_boto_client.return_value.describe_delivery_stream.return_value = {
            "DeliveryStreamDescription": {
                "DeliveryStreamStatus": "ACTIVE",
            }
        }
        tracker = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-1",
            region_name="eu-central-1",
        )
        tracker.ensure_active()
        assert tracker.active

    @patch("boto3.client")
    def test_ensure_active_creating(self, mock_boto_client):
        mock_boto_client.return_value.describe_delivery_stream.return_value = {
            "DeliveryStreamDescription": {
                "DeliveryStreamStatus": "CREATING",
            }
        }
        tracker = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-1",
            region_name="eu-central-1",
        )
        tracker.ensure_active(max_retry_override=1, retry_wait=0)
        assert not tracker.active

    @patch("boto3.client")
    def test_ensure_active_not_found(self, mock_boto_client):
        tracker = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-1",
            region_name="eu-central-1",
        )
        tracker.get_delivery_stream_status = lambda: "NOT_FOUND"
        tracker.ensure_active(max_retry_override=1, retry_wait=0)
        assert not tracker.active
        assert tracker.firehose_client.create_delivery_stream.called

    @patch("boto3.client")
    def test_put_record(self, mock_boto_client):
        mock_boto_client.return_value.put_record.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        mock_boto_client.return_value.describe_delivery_stream.return_value = {
            "DeliveryStreamDescription": {
                "DeliveryStreamStatus": "ACTIVE",
            }
        }
        tracker = Tracker(
            "test-tracking-stream",
            "suffix-1",
            "eu-central-1",
        )
        _response = tracker.ensure_active()
        _response = tracker.put_record({"test": "data"})
        assert tracker.firehose_client.put_record.called

    @patch("boto3.client")
    def test_put_records(self, mock_boto_client):
        mock_boto_client.return_value.put_record_batch.return_value = {
            "FailedPutCount": 0,
            "RequestResponses": [
                {"RecordId": "string"},
            ],
        }
        mock_boto_client.return_value.describe_delivery_stream.return_value = {
            "DeliveryStreamDescription": {
                "DeliveryStreamStatus": "ACTIVE",
            }
        }
        tracker = Tracker(
            "test-tracking-stream",
            "suffix-1",
            "eu-central-1",
        )
        _response = tracker.ensure_active()
        _response = tracker.put_records([{"test": "data"}])
        assert tracker.firehose_client.put_record_batch.called
