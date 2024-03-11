resource "aws_kinesis_firehose_delivery_stream" "delivery_stream" {
  name        = "${var.kinesis_stream_name}-delivery"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.destination.arn

    buffering_size     = 5
    buffering_interval = 60

    cloudwatch_logging_options {
      enabled         = "true"
      log_group_name  = aws_cloudwatch_log_group.firehose_log_group.name
      log_stream_name = aws_cloudwatch_log_stream.firehose_log_stream.name
    }

    file_extension = "json"
  }

  tags = var.tag
}
