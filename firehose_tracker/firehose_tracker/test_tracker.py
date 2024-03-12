from .tracker import Tracker


class TestTracker:
    """Tests for the Tracker class.
    Theses tests perform actual calls to AWS services and take longer to run.
    Only execute these tests when necessary, against development or staging environments.
    """

    def test_tracker_singleton(self):
        tracker_1 = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-1",
        )
        tracker_2 = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-1",
        )
        tracker_3 = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-2",
        )
        assert tracker_1 is tracker_2
        assert tracker_3 is not tracker_2

    def test_get_delivery_stream_status(self):
        tracker = Tracker("firehose-tracker", "checkout")
        status = tracker.get_delivery_stream_status()
        assert status == "ACTIVE"

    def test_put_record(self):
        tracker = Tracker(
            "firehose-tracker",
            "page_view",
        )
        response = tracker.put_record({"test": "data"})
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_put_records(self):
        tracker = Tracker(
            "firehose-tracker",
            "page_view",
        )
        response = tracker.put_records([{"test": "data"}])
        assert response["FailedPutCount"] == 0

    def test_ensure_active(self):
        tracker = Tracker(
            delivery_stream_base_name="test-tracking-stream",
            stream_suffix="suffix-1",
        )
        tracker.ensure_active()
        assert tracker.active

        tracker.delete_delivery_stream()
