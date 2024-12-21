import os


def strtobool(value: str | None) -> bool | None:
    return (
        value.lower() == "true" if value in ["True", "true", "False", "false"] else None
    )


PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
LOCATION = os.getenv("LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")
SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT")
VPC_NAME = os.getenv("VPC_NAME")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ENABLE_CACHING = strtobool(os.getenv("ENABLE_CACHING"))
COMPONENTS_IMAGE_VERSION = os.getenv("COMPONENTS_IMAGE_VERSION", "latest")

# NETWORK = (
#     f"projects/{PROJECT_NUMBER}/global/networks/{VPC_NAME}"
#     if PROJECT_NUMBER and VPC_NAME
#     else None
# )
NETWORK = None
COMPONENTS_IMAGE_TAG = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/pipeline/components:{COMPONENTS_IMAGE_VERSION}"
