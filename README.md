# vertex-ai-pipeline-example

## 環境

TBW
Mac zsh

## プロジェクト初期化

### 1. pipxのインストール

```zsh
$ brew install pipx
$ vi ~/.zshrc
path=( ... )に ~/.local/bin を追加

$ source ~/.zshrc
```

### 2. Poetryのインストール

```zsh
$ pipx install poetry
$ poetry --version
Poetry (version 1.8.4)

# オートコンプリーションを追加
$ mkdir ~/.zfunc/
$ poetry completions zsh > ~/.zfunc/_poetry
```

### 3. 他、開発に必要なCLIのインストール

```zsh
$ pipx install ruff==0.8.1 mypy==1.13.0 poetry==1.8.4
```

pre-commitのインストールも


### 4. プロジェクトの作成

```zsh
# vertex-ai-pipeline-exampleプロジェクトをすでにGithub上で作成している前提
$ cd /path/to/workspace-dir/vertex-ai-pipeline-example
$ poetry init

# 以下の内容で入力
# Pythonのバージョンはgoogle-cloud-pipeline-componentsが3.12以降に対応していないため3.11を使用
This command will guide you through creating your pyproject.toml config.

Package name [vertex-ai-pipeline-example]:
Version [0.1.0]:
Description []:
Author [your-name <your-name@your-org.com>, n to skip]:
License []:  MIT
Compatible Python versions [^3.13]:  >=3.11.0, <3.12

Would you like to define your main dependencies interactively? (yes/no) [yes] no
Would you like to define your development dependencies interactively? (yes/no) [yes] no
Generated file

[tool.poetry]
name = "vertex-ai-pipeline-example"
version = "0.1.0"
description = ""
authors = ["your-name <your-name@your-org.com>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = ">=3.11.0, <3.12"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"


Do you confirm generation? (yes/no) [yes]
```

### 5. pyenvのインストールおよびプロジェクトのPythonバージョンの設定

```zsh
$ brew install pyenv
$ vi ~/.zshrc
# ファイル末尾に以下の設定を追加
eval "$(pyenv init -)"

$ source ~/.zshrc

$ pyenv install 3.11.10
$ pyenv local 3.11.10
$ python -V
Python 3.11.10
```

### 6. プロジェクトに必要なフォルダおよびファイルの作成

```zsh
$ mkdir src tests notebooks terraform
$ touch src/__init__.py tests/__init__.py
```

### 7. パッケージのインストール

```zsh
$ poetry add kfp==2.7.0 \
google-cloud-pipeline-components==2.17.0 \
google-cloud-aiplatform==1.71.1

$ poetry add --group dev \
pytest==8.3.3 \
pytest-mock==3.14.0
```

### 8. .gitignoreに定義を追加

```zsh
$ vi .gitignore
# 以下をコメントアウト
.python-version

# 以下をコメントアウト
.idea/

# 以下を追加
# Ruff
.ruff_cache

# 以下を追加
# kfp
local_outputs
```

## ファイル、フォルダ構成

TBW

## Google Cloudプロジェクト作成

TBW


### x. 組織、プロジェクトを作成

TBW

請求先アカウントにリンクはプロジェクトを作成するだけで自動で行われていた。
ロール: リーエンの変更 を忘れずに。
久しぶりに実行したらRATE_LIMIT_EXCEEDEDが発生した。
```
ERROR: (gcloud.projects.add-iam-policy-binding) RESOURCE_EXHAUSTED: Quota exceeded for quota metric 'Write requests' and limit 'Write requests per minute' of service 'cloudresourcemanager.googleapis.com' for consumer 'project_number:00000000000'.
Request a higher quota limit.
```



### x. gcloudコマンドのインストール

```zsh
$ brew install --cask google-cloud-sdk
$ gcloud --version
Google Cloud SDK 504.0.0
bq 2.1.11
core 2024.12.13
gcloud-crc32c 1.0.0
gsutil 5.33
Updates are available for some Google Cloud CLI components.  To install them,
```

以降、504.0.0 で動作確認

### x. _config.shにGoogle Cloudプロジェクトの情報を作成

TBW
```zsh
$ cd /path/to/vertex-i-pipeline-example/infra
```

### x. Google Cloudプロジェクトの初期セットアップを実行

```zsh
$ ./scripts/setup_gcp_project.sh
```

上記手順を本番プロジェクト作成でも行う。


main.tfの設定を自分のリポジトリのものに置き換える必要がある。

### tfenvのインストール

詳細は記事参照。

```zsh
$ brew install tfenv
$ tfenv install 1.10.3
$ tfenv use 1.10.3
$ terraform version
Terraform v1.10.3
...
```

### Google Cloudプロジェクト上にVertex AI Pipeline用のリソースを作成

```zsh
$ cd /path/to/vertex-ai-pipeline-example/infra/terraform/environments/test
$ SERVICE=your-service-name
$ ENV=test
$ PROJECT_ID=$SERVICE-$ENV
$ terraform init -backend-config="bucket=$PROJECT_ID-terraform"
$ TF_VAR_service=$SERVICE \
  TF_VAR_env=$ENV \
  terraform plan
$ TF_VAR_service=$SERVICE \
  TF_VAR_env=$ENV \
  terraform apply
  ...
  Enter a value: (yesと入力してEnter)

  ...

  Apply complete! Resources: xx added, 0 changed, 0 destroyed.
```

### x. Githubリポジトリ設定

TBW





## 各種コマンド

TBW

## 関連リンク

- Kubeflow
- Vertex AI Pipelines

## 免責事項

network
