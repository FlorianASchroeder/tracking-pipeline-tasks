resource "aws_s3_bucket" "destination" {
  bucket = "${var.kinesis_stream_name}-data"

  tags = var.tag
}

resource "aws_s3_bucket_ownership_controls" "ownership_controls" {
  bucket = aws_s3_bucket.destination.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.ownership_controls]
  bucket     = aws_s3_bucket.destination.id
  acl        = "private"
}
