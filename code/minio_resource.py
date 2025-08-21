from dagster import resource
import boto3

@resource(config_schema={"endpoint": str, "access_key": str, "secret_key": str, "bucket": str})
def minio_resource(init_context):
    s3 = boto3.client(
        "s3",
        endpoint_url=init_context.resource_config["endpoint"],
        aws_access_key_id=init_context.resource_config["access_key"],
        aws_secret_access_key=init_context.resource_config["secret_key"],
    )
    return {"s3": s3, "bucket": init_context.resource_config["bucket"]}
