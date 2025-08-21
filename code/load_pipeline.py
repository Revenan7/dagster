import torch
from dagster import asset
from torchvision import datasets, transforms

@asset(required_resource_keys={"minio"})
def load_images(context):
    transform = transforms.ToTensor()
    train_dataset = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root="./data", train=False, download=True, transform=transform)

    import io
    s3 = context.resources.minio["s3"]
    bucket = context.resources.minio["bucket"]
    keys = {}

    for name, dataset in [("train", train_dataset), ("test", test_dataset)]:
        buffer = io.BytesIO()
        torch.save(dataset, buffer)
        buffer.seek(0)
        key = f"datasets/{name}.pt"
        s3.put_object(Bucket=bucket, Key=key, Body=buffer)
        keys[name] = key

    return keys
