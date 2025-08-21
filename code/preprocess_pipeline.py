from dagster import asset
import torch
from torchvision import transforms

@asset(required_resource_keys={"minio"})
def preprocess_images(context, load_images):
    import io
    s3 = context.resources.minio["s3"]
    bucket = context.resources.minio["bucket"]
    preprocessed_keys = {}

    for name, key in load_images.items():
        buffer = io.BytesIO()
        s3.download_fileobj(bucket, key, buffer)
        buffer.seek(0)
        dataset = torch.load(buffer)

        # пример: нормализация (если dataset.transform уже ToTensor, можно оставить)
        dataset.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])

        buffer2 = io.BytesIO()
        torch.save(dataset, buffer2)
        buffer2.seek(0)
        preprocessed_key = f"datasets/{name}_preprocessed.pt"
        s3.put_object(Bucket=bucket, Key=preprocessed_key, Body=buffer2)
        preprocessed_keys[name] = preprocessed_key

    return preprocessed_keys
