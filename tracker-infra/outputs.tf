output "FIREHOSE_TRACKER_ROLE_ARN" {
  description = "value of the ARN of the IAM role used by the Kinesis Firehose Delivery Stream"
  value       = aws_iam_role.firehose.arn
}

output "FIREHOSE_TRACKER_BUCKET_ARN" {
  description = "The ARN of the destination S3 bucket"
  value       = aws_s3_bucket.destination.arn
}

output "FIREHOSE_TRACKER_LOG_GROUP_NAME" {
  description = "The name of the CloudWatch Logs log group"
  value       = aws_cloudwatch_log_group.firehose_log_group.name
}

output "FIREHOSE_TRACKER_FIX_NEWLINE_LAMBDA_ARN" {
  description = "The ARN of the Lambda function used to add newlines to the end of each record"
  value       = var.firehose_transformations_fix_newline_arn
}
