"""Vertex AI Pipelinesの操作に関する処理をまとめたモジュール。"""

import tempfile
from typing import Any

import google.cloud.aiplatform as aip
from google.cloud.aiplatform.metadata import experiment_resources
from kfp import compiler
from kfp.dsl import base_component
from kfp.registry import ApiAuth, RegistryClient


class PipelineClient:
    """Vertex AI Pipelinesに対して操作を行うクライアント。"""

    def __init__(
        self,
        project_id: str,
        location: str,
        staging_bucket: str,
        pipeline_name: str,
        pipeline_func: base_component.BaseComponent,
        enable_caching: bool | None = None,
        parameter_values: dict[str, Any] | None = None,
        network: str | None = None,
        service_account: str | None = None,
    ) -> None:
        """Vertex AI Pipelinesの操作に必要な値を受け取り、接続の初期化、パイプラインテンプレートの生成を行う。

        Args:
            project_id: Google CloudのプロジェクトID。
            location: us-central1、asia-northeast1など。
            staging_bucket: Vertex AI Pipelinesの操作時に使用するバケット。
            pipeline_name: 操作を行うパイプラインの名前。
            pipeline_func: 実行されるパイプライン。
            enable_caching: パイプラン実行時にキャッシュを有効にするかどうか。
            parameter_values: ``aiplatform.PipelineJob``インスタンス生成時に渡すパラメータ。
            network: パイプラインが実行されるVPCネットワーク。
            service_account: パイプライン実行で使用するサービスアカウント。
        """
        self.project_id = project_id
        self.location = location
        self.staging_bucket = staging_bucket
        self.pipeline_name = pipeline_name
        self.pipeline_func = pipeline_func
        self.enable_caching = enable_caching
        self.parameter_values = parameter_values
        self.network = network
        self.service_account = service_account

        # Vertex AIへの接続を初期化
        aip.init(project=project_id, location=location, staging_bucket=staging_bucket)

        # パイプラインのコンパイルはVertex AI Pipelinesに対する全ての操作で共通で実行する必要があるため、コンストラクタ内で実行
        # ref. https://cloud.google.com/vertex-ai/docs/pipelines/create-pipeline-template?hl=ja
        self.template_path = f"{tempfile.gettempdir()}/{self.pipeline_name}.yaml"
        compiler.Compiler().compile(self.pipeline_func, self.template_path)

        self.pipeline_root = f"{self.staging_bucket}/pipeline_root"

    def submit_job(
        self,
        reserved_ip_ranges: list[str] | None = None,
        create_request_timeout: float | None = None,
        experiment: str | experiment_resources.Experiment | None = None,
        enable_preflight_validations: bool | None = False,
    ) -> aip.PipelineJob:
        """パイプラインジョブを実行。

        Args:
            reserved_ip_ranges: パイプラインが起動するVPCネットワークのIPアドレス範囲。
            create_request_timeout: パイプラインジョブの作成リクエストのタイムアウト時間。
            experiment: パイプラインジョブに関連付けるVertex AI Experimentsの名前またはインスタンス。
            enable_preflight_validations: パイプラインの事前検証を有効にするかどうか。

        Returns:
            実行中のパイプラインジョブ。
        """
        job = self._get_job()
        job.submit(
            service_account=self.service_account,
            network=self.network,
            reserved_ip_ranges=reserved_ip_ranges,
            create_request_timeout=create_request_timeout,
            experiment=experiment,
            enable_preflight_validations=enable_preflight_validations,
        )
        return job

    def upload_template(
        self,
        template_repository_name: str,
        access_tken: str | None = None,
        tags: str | list[str] | None = None,
        extra_headers: dict[Any, Any] | None = None,
    ) -> tuple[str, str]:
        """Artifact Registryにパイプラインテンプレートをアップロード。

        Args:
            template_repository_name: テンプレートのアップロード先のArtifact Registryリポジトリ名。
            access_tken: Artifact Registryに接続する際に使用するアクセストークン(Workload Identity Poolによる認証後にArtifact Registryを操作する場合に必要)。
            tags: テンプレートに適用するタグ(バージョンなど)。
            extra_headers: アップロード時に適用する追加のヘッダー。

        Returns:
            package_name: アップロードされたテンプレートの名前。
            version: アップロードされたテンプレートのバージョン。

        Note:
            テンプレート経由でのパイプライン実行は環境変数の値を参照できなくなるため、このプロジェクトの設計では出番がない。
        """
        registry_client = RegistryClient(
            host=f"https://{self.location}-kfp.pkg.dev/{self.project_id}/{template_repository_name}",
            auth=ApiAuth(access_tken) if access_tken is not None else None,
        )
        package_name, version = registry_client.upload_pipeline(
            file_name=self.template_path, tags=tags, extra_headers=extra_headers
        )
        return (package_name, version)

    def create_schedule(
        self,
        cron: str,
        start_time: str | None = None,
        end_time: str | None = None,
        allow_queueing: bool = False,
        max_run_count: int | None = None,
        max_concurrent_run_count: int = 1,
        create_request_timeout: int = 10,
        pause: bool = False,
    ) -> aip.PipelineJobSchedule:
        """パイプラインの定期実行スケジュールを作成。

        Args:
            cron: 定期実行のスケジュール。
            start_time: スケジュールの有効時刻。
            end_time: スケジュールの有効時刻。
            allow_queueing: max_concurrent_runs_count制限に達した時に新しくスケジュールされたジョブをキューに入れるか。
            max_run_count: スケジュールの最大実行可能数。
            max_concurrent_run_count: スケジュールの最大並列実行可能数。
            create_request_timeout: スケジュール作成リクエストのタイムアウト時間(秒)。
            pause: スケジュール作成後に一時停止状態に変更するか。

        Returns:
            パイプラインの定期実行スケジュール。
        """
        schedule_name = self._get_schedule_name()

        # スケジュールは実行した回数だけ作成される
        # よって同じdisplay_nameのスケジュールがすでに存在する場合、事前に削除
        for schedule in aip.PipelineJobSchedule.list(
            filter=f'display_name="{schedule_name}"',
        ):
            schedule.delete()

        # スケジュールの作成
        schedule = self._get_job().create_schedule(
            cron=cron,
            display_name=schedule_name,
            start_time=start_time,
            end_time=end_time,
            allow_queueing=allow_queueing,
            max_run_count=max_run_count,
            max_concurrent_run_count=max_concurrent_run_count,
            service_account=self.service_account,
            network=self.network,
            create_request_timeout=create_request_timeout,
        )

        # 個人の環境でパイプラインの定期実行を行うとかなりの請求金額になるため一時停止推奨
        # またパイプラインを定期実行ではなくアドホックに実行したい場合もスケジュール経由での実行を想定していて、その際も一時停止にしておく
        if pause:
            schedule.pause()

        return schedule

    def _get_job(self) -> aip.PipelineJob:
        """パイプラインジョブインスタンスを生成。

        Returns:
            パイプラインジョブインスタンス。
        """
        return aip.PipelineJob(
            display_name=self.pipeline_name,
            template_path=self.template_path,
            enable_caching=self.enable_caching,
            project=self.project_id,
            pipeline_root=self.pipeline_root,
            failure_policy="fast",
            parameter_values=self.parameter_values,
        )

    def _get_schedule_name(self) -> str:
        """パイプラインの定期実行スケジュールの名前を生成。

        Returns:
            パイプラインの定期実行スケジュールの名前。
        """
        return f"{self.pipeline_name}-schedule"
