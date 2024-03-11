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
