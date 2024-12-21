import argparse
import sys

from kfp import dsl

from src.components.operator.multiply.component import multiply
from src.env import (
    ENABLE_CACHING,
    LOCATION,
    NETWORK,
    PROJECT_ID,
    SERVICE_ACCOUNT,
    STAGING_BUCKET,
)
from src.logics.gcloud.vertex import PipelineClient

PIPELINE_NAME = "calcuration2"


@dsl.pipeline(name=PIPELINE_NAME)
def pipeline(
    v1: str = "0.0",
) -> None:
    multiply_task = multiply(v1=v1, v2=v1)
    multiply(v1=multiply_task.outputs["product"], v2=v1)


def _parse_pipeline_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1", default="0.0")
    parser.add_argument("-s", "--schedule", action="store_true")
    parser.add_argument("--pause", action="store_true")
    parser.add_argument("-j", "--job", action="store_true")
    parsed_args, _ = parser.parse_known_args(args)
    return parsed_args


def main(argv: list[str]) -> None:
    if PROJECT_ID is None or STAGING_BUCKET is None:
        raise ValueError("`PROJECT_ID` and `STAGING_BUCKET` must be set.")

    args = _parse_pipeline_args(argv)
    client = PipelineClient(
        project_id=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
        pipeline_name=PIPELINE_NAME,
        pipeline_func=pipeline,
        enable_caching=ENABLE_CACHING,
        service_account=SERVICE_ACCOUNT,
        network=NETWORK,
        parameter_values={"v1": args.v1},
    )

    if args.schedule:
        client.create_schedule(cron="TZ=Asia/Tokyo 0 1 * * *", pause=args.pause)
    if args.job:
        client.submit_job()


if __name__ == "__main__":
    main(sys.argv[1:])
