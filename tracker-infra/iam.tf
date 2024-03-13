data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_iam_role" "firehose" {
  name = "FirehoseAssumeRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  tags = var.tag
}

resource "aws_iam_policy" "firehose_s3" {
  name_prefix = var.iam_name_prefix
  policy      = <<-EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Sid": "",
        "Effect": "Allow",
        "Action": [
            "s3:AbortMultipartUpload",
            "s3:GetBucketLocation",
            "s3:GetObject",
            "s3:ListBucket",
            "s3:ListBucketMultipartUploads",
            "s3:PutObject"
        ],
        "Resource": [
            "${aws_s3_bucket.destination.arn}",
            "${aws_s3_bucket.destination.arn}/*"
        ]
    }
  ]
}
EOF
  tags        = var.tag
}

resource "aws_iam_role_policy_attachment" "firehose_s3" {
  role       = aws_iam_role.firehose.name
  policy_arn = aws_iam_policy.firehose_s3.arn
}

resource "aws_iam_policy" "put_record" {
  name_prefix = var.iam_name_prefix
  policy      = <<-EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "firehose:PutRecord",
                "firehose:PutRecordBatch"
            ],
            "Resource": [
                "arn:aws:firehose:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:deliverystream/${var.stream_base_name}-*"
            ]
        }
    ]
}
EOF
  tags        = var.tag
}

resource "aws_iam_role_policy_attachment" "put_record" {
  role       = aws_iam_role.firehose.name
  policy_arn = aws_iam_policy.put_record.arn
}

resource "aws_iam_policy" "firehose_cloudwatch" {
  name_prefix = var.iam_name_prefix

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Sid": "",
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ],
        "Resource": [
            "${aws_cloudwatch_log_group.firehose_log_group.arn}"
        ]
    }
  ]
}
EOF
  tags   = var.tag
}

resource "aws_iam_role_policy_attachment" "firehose_cloudwatch" {
  role       = aws_iam_role.firehose.name
  policy_arn = aws_iam_policy.firehose_cloudwatch.arn
}

# allow invocation of the lambda function
resource "aws_iam_policy" "firehose_lambda" {
  name_prefix = var.iam_name_prefix

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "${var.firehose_transformations_fix_newline_arn}"
    }
  ]
}
EOF
  tags   = var.tag
}

resource "aws_iam_role_policy_attachment" "firehose_lambda" {
  role       = aws_iam_role.firehose.name
  policy_arn = aws_iam_policy.firehose_lambda.arn
}
