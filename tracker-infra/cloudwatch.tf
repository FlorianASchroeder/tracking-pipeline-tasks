resource "aws_cloudwatch_log_group" "firehose_log_group" {
  name = "/aws/kinesisfirehose/${var.stream_base_name}-delivery"

  tags = var.tag
}

resource "aws_cloudwatch_log_stream" "firehose_log_stream" {
  count          = length(var.event_types)
  name           = "stream-errors-${var.event_types[count.index]}"
  log_group_name = aws_cloudwatch_log_group.firehose_log_group.name
}
