locals {
  # TODO 自身のリポジトリの情報に置き換える必要がある
  github_account_name = "erueru-tech"
  github_repo_name    = "vertex-ai-pipeline-example"
  project_id          = join("-", [var.service, var.env])
  terraform_bucket    = "${local.project_id}-terraform"
}

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
    "cloudbuild.googleapis.com"
  ]
  # terraform destroy実行時に上記APIが全て無効化されないようにする設定
  disable_services_on_destroy = false
}

#
# Vertex AI Pipelines用リソース
#

resource "google_storage_bucket" "pipeline" {
  name     = "${local.project_id}-pipeline"
  location = var.region
}

resource "google_service_account" "pipeline" {
  project    = local.project_id
  account_id = "pipeline"
}

resource "google_project_iam_member" "pipeline" {
  project = local.project_id
  member  = "serviceAccount:${google_service_account.pipeline.email}"
  role    = each.value
  for_each = toset([
    "roles/artifactregistry.reader",
    "roles/aiplatform.user",
  ])
}

resource "google_storage_bucket_iam_member" "pipeline" {
  bucket = google_storage_bucket.pipeline.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_artifact_registry_repository" "app" {
  location      = var.region
  repository_id = "app"
  format        = "DOCKER"
}

resource "google_artifact_registry_repository" "pipeline_template" {
  location      = var.region
  repository_id = "pipeline-template"
  format        = "KFP"
}

#
# Github Actions用リソース
# 

resource "google_service_account" "github_actions" {
  project    = local.project_id
  account_id = "github-actions"
}

resource "google_project_iam_member" "github_actions" {
  project = local.project_id
  member  = "serviceAccount:${google_service_account.github_actions.email}"
  role    = each.value
  for_each = toset([
    "roles/cloudbuild.builds.builder",
    "roles/aiplatform.user",
    "roles/iam.serviceAccountUser",
  ])
}

#
# Networkリソース
#

