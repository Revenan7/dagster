from dagster import asset
import torch
from train_pipeline import SimpleMLP

@asset(required_resource_keys={"minio"})
def evaluate_model(context, preprocess_images, train_model):
    import io
    s3 = context.resources.minio["s3"]
    bucket = context.resources.minio["bucket"]

    # загрузка модели
    buffer = io.BytesIO()
    s3.download_fileobj(bucket, train_model, buffer)
    buffer.seek(0)
    model = SimpleMLP()
    model.load_state_dict(torch.load(buffer))
    model.eval()

    # загрузка test
    buffer2 = io.BytesIO()
    s3.download_fileobj(bucket, preprocess_images["test"], buffer2)
    buffer2.seek(0)
    test_dataset = torch.load(buffer2)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=64, shuffle=False)

    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = correct / total
    return accuracy
