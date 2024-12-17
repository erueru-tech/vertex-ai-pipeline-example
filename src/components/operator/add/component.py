from kfp import dsl
from kfp.dsl import container_component

from src import env


@container_component
def add(
    v1: str,
    v2: str,
    sum: dsl.OutputPath(str),  # type: ignore[valid-type]
) -> dsl.ContainerSpec:
    return dsl.ContainerSpec(
        image=f"{env.COMPONENTS_IMAGE_TAG}",
        command=[
            "python",
            "-u",
            "-m",
            "src.containers.operator.add.launcher",
        ],
        args=[
            "--v1",
            v1,
            "--v2",
            v2,
            "--sum",
            sum,
        ],
    )
