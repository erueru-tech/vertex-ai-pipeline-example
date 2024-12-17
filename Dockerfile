# 使用頻度が低いパッケージを削除して軽量化されたpython:3.11イメージがベース
FROM python:3.11-slim

# 具体的に現実的なセキュリティの問題が起きるパターンを考えたが思いつかない、基本的に記述が冗長になるのでrootユーザーで実行

# 標準出力(stdout)と標準エラー出力(stderr)がリアルタイムで出力される
# 正直鉄板設定扱いだから入れている感が強い
ENV PYTHONUNBUFFERED=1 \
    # Pythonの実行時にバイトコードファイル(.pycファイル)を生成しないようにする
    # 正直鉄板設定扱いだから入れている感が強い
    PYTHONDONTWRITEBYTECODE=1 \
    # Poetryのバージョンを指定(後続のPoetryのインストーラ実行時に自動的に読み込まれる環境変数)
    POETRY_VERSION=1.8.4 \
    # Poetryの仮想環境作成を無効化して、直接依存関係をインストールするための設定
    POETRY_VIRTUALENVS_CREATE=false \
    # poetryコマンドインストール先(予定)に事前にパスを通しておく
    PATH="${PATH}:/root/.local/bin"

# 以後のコマンドが実行されるワーキングディレクトリを指定
WORKDIR /app

# 使用パッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Poetryのインストール
# pip install poetry==$POETRY_VERSION を使わないのは /usr/local/lib/python3.11/site-packages/ 内で
# Poetryの依存とアプリケーションの依存が混在するため
RUN curl -sSL https://install.python-poetry.org | python3 -

# アプリケーションで使用する依存関係を定義したファイルをワーキングディレクトリにコピー
# なお以降の定義はPoetryの公式ドキュメントを多少参考にしている
# https://python-poetry.org/docs/faq/#poetry-busts-my-docker-cache-because-it-requires-me-to-copy-my-source-files-in-before-installing-3rd-party-dependencies
COPY pyproject.toml poetry.lock ./

# poetry.lockあるいはpyproject.tomlの定義をもとに依存関係をインストール
#
# 以下、使用オプションの説明
# --without dev ... 昔の--no-devオプションと同等、開発用の依存関係をインストールしない
# --no-root ... (Dockerのキャッシュ対策のためにこの時点でソースコードをコピーしていないこともあり)アプリケーションのルートパッケージをインストールしない
# --no-directory ... ソースコードなしで依存関係をインストールするために必要なオプション
# --no-interaction ... 対話形式のプロンプトを無効化
# --no-ansi ... カラー出力を無効化
RUN poetry install --without dev --no-root --no-directory --no-interaction --no-ansi

# アプリケーションのコードをワーキングディレクトリにコピー
COPY ./src ./src

# アプリケーションコードをパッケージング(しなくてもこのプロジェクトの用途では動くのでコメントアウト)
#　RUN poetry install --without dev --no-interaction --no-ansi
