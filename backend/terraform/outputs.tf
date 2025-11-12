output "server_ip" {
  description = "Public IP address of the server"
  value       = hcloud_server.app_server.ipv4_address
}

output "server_status" {
  description = "Status of the server"
  value       = hcloud_server.app_server.status
}

output "hetzner_s3_bucket_name" {
  description = "Name of the the S3 bucket for application media files"
  value       = minio_s3_bucket.app_media.bucket
}
output "hetzner_s3_endpoint_url" {
  description = "Endpoint URL for the S3 bucket for application media files"
  value       = minio_s3_bucket.app_media.bucket_domain_name
}
