"""vertexモジュール内のVertex AIに対する操作を行うクラスや関数に対してテストを行う。

[テストに必要なリソース]
以下のテストを実行するためには、Artifact Registry上にテンプレート用のリポジトリを作成する必要がある。
リポジトリはTerraformなどIaCツールでの作成を推奨するが、以下のコマンドで手動で作成することも出来る。

$ gcloud artifacts repositories create vertex-test-pipeline-kfp \
    --repository-format=KFP \
    --project your-gcp-project \
    --location your-location(e.g. us-central1)

[テスト実行]
実行が遅い、テストがflakyになる、実行に必要な環境変数が大量にある、一度成功が確認できれば問題ないなどの理由により、以下のテストにはmanualマーカーが付与されている。
つまりpytest.iniのaddoptsの設定に従い、pytestコマンド実行時にデフォルトではテストされない。
vertexモジュールのテストを行いたい場合、以下のようなコマンドで明示的にテストを実行する必要がある。

$ cd /path/to/project_root
$ PROJECT_ID=${Google Cloudプロジェクト名} \
    PROJECT_NUMBER=${oogle Cloudプロジェクトの12桁の番号}\
    STAGING_BUCKET=gs://${パイプラインが使用するバケット} \
    SERVICE_ACCOUNT=${パイプラインの実行サービスアカウント(任意)} \
    VPC_NAME=sample-${パイプラインを実行するVPCネットワーク名(任意)} \
    poetry run pytest tests/logics/gcloud/vertex_test.py -m "manual"
"""

import google.cloud.aiplatform as aip
import pytest
from google.cloud.aiplatform.compat.types import pipeline_state
from kfp import dsl

from src.env import (
    LOCATION,
    NETWORK,
    PROJECT_ID,
    SERVICE_ACCOUNT,
    STAGING_BUCKET,
)
from src.logics.gcloud.vertex import PipelineClient
from tests.env import PYTHON_BASE_IMAGE

PIPELINE_NAME = "vertex-test-pipeline"
TEMPLATE_REPOSITORY_NAME = f"{PIPELINE_NAME}-kfp"
ENABLE_CACHING = False


@dsl.component(base_image=PYTHON_BASE_IMAGE)
def hello_world() -> None:
    print("Hello, World!")


@dsl.pipeline(name=PIPELINE_NAME)
def pipeline() -> None:
    hello_world()


def _pipeline_client() -> PipelineClient:
    """Vertex AI Pipelines操作クライアントを生成。"""
    if PROJECT_ID is None or STAGING_BUCKET is None:
        raise ValueError("`PROJECT_ID` and `STAGING_BUCKET` must be set.")
    return PipelineClient(
        project_id=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
        pipeline_name=PIPELINE_NAME,
        pipeline_func=pipeline,
        enable_caching=ENABLE_CACHING,
        service_account=SERVICE_ACCOUNT,
        network=NETWORK,
    )


@pytest.mark.manual
def test_upload_template1() -> None:
    """パイプラインテンプレートが作成されることを確認。"""
    package_name, version = _pipeline_client().upload_template(
        template_repository_name=TEMPLATE_REPOSITORY_NAME,
    )
    assert package_name == PIPELINE_NAME
    assert version.startswith("sha256:")


@pytest.mark.manual
def test_create_schedule1() -> None:
    """パイプライン実行スケジュールが生成されることを確認。"""
    _assert_schedule_num(0)
    schedule = _pipeline_client().create_schedule(
        cron="TZ=Asia/Tokyo 59 23 31 12 0", pause=True
    )
    _assert_schedule_num(1)
    schedule.delete()


def _assert_schedule_num(num: int) -> None:
    """Vertex AI上に存在するスケジュール数がnumであることを確認。

    Args:
        num: 想定されるスケジュール数
    """
    assert (
        len(
            aip.PipelineJobSchedule.list(
                filter=f'display_name="{_pipeline_client()._get_schedule_name()}"',
            )
        )
        == num
    )


@pytest.mark.manual
def test_submit_job1() -> None:
    """パイプラインジョブが正常終了することを確認するテスト(実行に2分以上かかる)。"""
    job = _pipeline_client().submit_job()
    job.wait()
    assert (
        job.done()
        and job.state == pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
    )
