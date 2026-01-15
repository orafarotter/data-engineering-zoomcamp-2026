variable "credentials" {
  description = "My Credentials"
  default     = "./keys/project-c547a08c-a25e-4ad3-bcf-48b8b380b82e.json"
  #ex: if you have a directory where this file is called keys with your service account json file
  #saved there as my-creds.json you could use default = "./keys/my-creds.json"
}


variable "project" {
  description = "Project"
  default     = "project-c547a08c-a25e-4ad3-bcf"
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
