from dagster import Definitions, in_process_executor
from load_pipeline import load_images
from preprocess_pipeline import preprocess_images
from train_pipeline import train_model
from evaluate_pipeline import evaluate_model
from minio_resource import minio_resource

defs = Definitions(
    assets=[load_images, preprocess_images, train_model, evaluate_model],
    resources={
        "minio": minio_resource.configured({
            "endpoint": "http://89.169.15.20:1337",
            "access_key": "OPG",
            "secret_key": "NtdA5962", 
            "bucket": "mlops"
        })
    },
    executor=in_process_executor,  # Используем in-process executor
)
