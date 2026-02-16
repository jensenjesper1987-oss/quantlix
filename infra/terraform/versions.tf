terraform {
  required_version = ">= 1.5"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }

  # Uncomment for remote state (S3, GCS, etc.)
  # backend "s3" {
  #   bucket = "quantlix-tfstate"
  #   key    = "terraform.tfstate"
  #   region = "eu-central-1"
  # }
}
