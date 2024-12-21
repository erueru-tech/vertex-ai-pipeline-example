# リソース定義で共通で参照されるリテラル値を定義
locals {
  project_id       = join("-", [var.service, var.env])
  terraform_bucket = "${local.project_id}-terraform"
}

###########################################
# Google Cloudプロジェクト設定               #
###########################################

# Google Cloudプロジェクトで使用するサービスを有効化する
# なおBigQueryなど、このソースコードプロジェクトのパイプラインを実行するのに必要最低限以上のサービスを有効化している点に注意
module "project_services" {
  source     = "terraform-google-modules/project-factory/google//modules/project_services"
  version    = "17.1.0"
  project_id = local.project_id
  activate_apis = [
    "bigquery.googleapis.com",
    "bigquerystorage.googleapis.com",
    "cloudapis.googleapis.com",
    "cloudasset.googleapis.com",
    "cloudbilling.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "networksecurity.googleapis.com",
    "servicemanagement.googleapis.com",
    "serviceusage.googleapis.com",
    "storage-api.googleapis.com",
    "storage-component.googleapis.com",
    "storage.googleapis.com",
    "servicenetworking.googleapis.com",
    "compute.googleapis.com",
    "sts.googleapis.com",
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "notebooks.googleapis.com"
  ]
  # terraform destroy実行時に上記APIが全て無効化されないようにする設定
  # このGoogle Cloudプロジェクトではそこまで大きな意味を持たないが、Terraformのテストコードを実装する際には必須となる設定
  disable_services_on_destroy = false
}

###########################################
# Vertex AI Pipelines用リソース             #
###########################################

# パイプライン実行中の中間成果物などを出力したり、アプリケーションビルドの際に使用するCloud Storageバケット
resource "google_storage_bucket" "pipeline" {
  name     = "${local.project_id}-pipeline"
  location = var.region
}

# パイプライン実行時に使用するサービスアカウント
resource "google_service_account" "pipeline" {
  project    = local.project_id
  account_id = "pipeline"
}

# サービスアカウントに付与するロール
resource "google_project_iam_member" "pipeline" {
  project = local.project_id
  member  = "serviceAccount:${google_service_account.pipeline.email}"
  role    = each.value
  for_each = toset([
    "roles/artifactregistry.reader",
    "roles/aiplatform.user",
  ])
}

# パイプライン実行中に中間成果物をCloud Storageバケットに出力するために必要なロール
resource "google_storage_bucket_iam_member" "pipeline" {
  bucket = google_storage_bucket.pipeline.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}

# このソースコードプロジェクトのコードをDockerコンテナ化したものを格納するArtifact Registryリポジトリ
resource "google_artifact_registry_repository" "pipeline" {
  location      = var.region
  repository_id = "pipeline"
  format        = "DOCKER"
}

# Vertex AI Pipelinesのテンプレートを格納するArtifact Registryリポジトリ
# (このソースコードプロジェクトでは使用していない)
resource "google_artifact_registry_repository" "pipeline_template" {
  location      = var.region
  repository_id = "pipeline-template"
  format        = "KFP"
}

###########################################
# Network関連リソース                       #
###########################################

# VPCネットワークとサブネット
# 以下のVPC内にWorkbench用インスタンスを作成できることだけは一応確認済み
# https://cloud.google.com/vertex-ai/docs/general/vpc-standalone?hl=ja
# なおパイプラインジョブ実行時に指定するネットワークとしてはVPCピアリングの設定等が不足しているため以下の設定では使用できない
# とはいえパイプラインからVPC内のリソースに接続するなどの要件が個人的に無く、実際にそのような課題が発生するまで面倒なので対応しない
# 要は以下の定義は無くてもパイプラインは動く
module "vpc" {
  source       = "terraform-google-modules/network/google"
  version      = "10.0.0"
  project_id   = local.project_id
  network_name = "vpc"
  subnets = [
    {
      subnet_name           = "subnet-1"
      subnet_ip             = var.subnet_ip
      subnet_region         = var.region
      subnet_private_access = "true"
    }
  ]
}

###########################################
# Github Actions用リソース                  #
###########################################

# Github ActionsからGoogle Cloudプロジェクトに対して認証を行うために必要なリソース
# Github Actionsから操作するGoogle Cloudプロジェクトはtest環境のものを使用する前提
module "gh_oidc" {
  source      = "terraform-google-modules/github-actions-runners/google//modules/gh-oidc"
  version     = "4.0.0"
  project_id  = local.project_id
  pool_id     = "github-pool"
  provider_id = "github-provider"
  attribute_mapping = {
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.aud"        = "assertion.aud"
    "google.subject"       = "assertion.sub"
    "attribute.email"      = "assertion.email"
  }
  attribute_condition = "assertion.repository==\"${var.github_account_name}/${var.github_repo_name}\""
}

# Github ActionsからGoogle CloudのWorload Identity Providerプールに接続する際に必要なロール
resource "google_service_account_iam_member" "github" {
  service_account_id = google_service_account.pipeline.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${module.gh_oidc.pool_name}/attribute.repository/${var.github_account_name}/${var.github_repo_name}"
}

# Github Actionsからパイプラインスケジュールを作成する際に必要なロール
resource "google_project_iam_member" "github" {
  project = local.project_id
  member  = "serviceAccount:${google_service_account.pipeline.email}"
  role    = each.value
  for_each = toset([
    "roles/cloudbuild.builds.builder",
    "roles/iam.serviceAccountUser",
  ])
}
