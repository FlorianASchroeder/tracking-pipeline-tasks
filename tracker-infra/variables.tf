variable "stream_base_name" {
  description = "Firehose Delivery Stream Base Name"
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

variable "event_types" {
  description = "Event types tracked by the application. Used to create delivery streams and log streams."
  type        = list(string)
  default     = ["session_started", "page_view", "checkout", "purchase"]
}

variable "firehose_transformations_fix_newline_arn" {
  description = "ARN (including version) of the Lambda function used to add newlines to the end of each record. Deploy the function before deploying the infrastructure."
  type        = string
  default     = "arn:aws:lambda:eu-central-1:339712828249:function:firehose-transformations-dev-fix-newline:3"
}
