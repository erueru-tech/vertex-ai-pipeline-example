# Google Cloudプロジェクト上に作成するリソースを管理する場合、以下を定義
provider "google" {
  project = local.project_id
  region  = var.region
}

provider "google-beta" {
  project = local.project_id
  region  = var.region
}

