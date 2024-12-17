# Terraform内で使用する変数を定義
# 変数への値の設定は基本的にterraformコマンド実行時に環境変数を使用して行う

# Google Cloudのプロジェクト名は"サービス名＋ハイフン＋環境名"を30文字以内に抑えなければいけないことを考えると、
# ハイフン＋環境名(-prod, -test)は5文字なので、サービス名は25文字以内でなければいけない
variable "service" {
  type    = string
  default = null
  validation {
    condition     = length(var.service) <= 25
    error_message = "The length of the var.service value must be less than or equal to 25."
  }
}

# 環境(prod, test)を指定する変数
variable "env" {
  type    = string
  default = null
  validation {
    condition     = contains(["prod", "test"], var.env)
    error_message = "The value of var.env must be 'prod' or 'test', but it is '${var.env}'."
  }
}

# 以下の定義ならlocalsでリテラルの値を定義したほうがいいが、将来的に許可リージョンを増やすことを想定
variable "region" {
  type    = string
  default = "us-central1"
  validation {
    condition     = var.region == "us-central1"
    error_message = "The var.region value must be 'us-central1', but it is '${var.region}'."
  }
}

# VPC内に作成するサブネットのIPアドレス範囲
variable "subnet_ip" {
  type    = string
  default = null
  validation {
    condition     = var.subnet_ip != null
    error_message = "The var.subnet_ip value is required."
  }
}

# Githubのアカウント名あるいは組織名(このプロジェクトでは"erueru-tech"になる)
variable "github_account_name" {
  type    = string
  default = null
  validation {
    condition     = var.github_account_name != null
    error_message = "The var.github_account_name value is required."
  }
}

# Githubのリポジトリ名(このプロジェクトでは"vertex-ai-pipeline-example"になる)
variable "github_repo_name" {
  type    = string
  default = null
  validation {
    condition     = var.github_repo_name != null
    error_message = "The var.github_repo_name value is required."
  }
}
