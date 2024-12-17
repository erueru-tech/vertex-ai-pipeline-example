# 使用するTerraformのバージョンやプロバイダのバージョンを定義
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.14.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "6.14.0"
    }
  }
  required_version = "1.10.3"
}
