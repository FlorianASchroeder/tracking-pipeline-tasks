# create 1 delivery stream for each event type
# write loop over var.event_types

resource "aws_kinesis_firehose_delivery_stream" "delivery_stream" {
  count       = length(var.event_types)
  name        = "${var.stream_base_name}-delivery-stream-${var.event_types[count.index]}"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.destination.arn

    buffering_size     = 128
    buffering_interval = 300

    processing_configuration {
      enabled = "true"
      processors {
        type = "Lambda"
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = var.firehose_transformations_fix_newline_arn
        }
      }
    }

    cloudwatch_logging_options {
      enabled        = "true"
      log_group_name = aws_cloudwatch_log_group.firehose_log_group.name

      # needs to be identical to the log stream name defined in cloudwatch.tf
      log_stream_name = "stream-errors-${var.event_types[count.index]}"
    }

    file_extension = ".jsonl"
  }

  tags = var.tag
}
