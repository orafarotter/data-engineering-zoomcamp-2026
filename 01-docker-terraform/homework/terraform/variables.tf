variable "credentials" {
  description = "My Credentials"
  default     = "./keys/<key>.json"
}

variable "project" {
  description = "Project"
  default     = "<your_project_id>"
}

variable "region" {
  description = "Region"
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  default     = "US"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "terraform_gcs_bucket_20260115"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "terraform_bq_dataset_20260115"
}
