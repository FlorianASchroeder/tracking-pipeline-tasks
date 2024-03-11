variable "kinesis_stream_name" {
  description = "Kinesis Data Stream Name"
  default     = "firehose-tracker"
}

variable "iam_name_prefix" {
  description = "Prefix used for all created IAM roles and policies"
  type        = string
  nullable    = false
  default     = "firehose-tracker-"
}

variable "tag" {
  description = "Tag to be applied to all resources"
  type        = map(string)
  default = {
    app = "firehose-tracker"
  }
}
