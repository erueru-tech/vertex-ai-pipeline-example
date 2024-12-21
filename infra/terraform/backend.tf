terraform {
  backend "gcs" {
    # オープンソースであるため、自分のGoogle Cloudプロジェクトの名前がバレないように適当な名前を設定している
    # なお、terraform initコマンド実行の際は、以下のように動的にstate管理用GCSバケット名を指定すればよい
    # $ terraform init -backend-config="bucket=your-terraform-bucket-name"
    bucket = "your-terraform-bucket-name"
    prefix = "terraform/state"
  }
}
