from dagster import asset
import torch
import torch.nn as nn
import torch.optim as optim

class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28*28, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
    def forward(self, x):
        return self.model(x)

@asset(required_resource_keys={"minio"})
def train_model(context, preprocess_images):
    import io
    s3 = context.resources.minio["s3"]
    bucket = context.resources.minio["bucket"]

    # загрузка preprocessed train
    buffer = io.BytesIO()
    s3.download_fileobj(bucket, preprocess_images["train"], buffer)
    buffer.seek(0)
    train_dataset = torch.load(buffer)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

    model = SimpleMLP()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(2):
        for images, labels in train_loader:
            optimizer.zero_grad()
            output = model(images)
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()

    # сохраняем модель в MinIO
    buffer2 = io.BytesIO()
    torch.save(model.state_dict(), buffer2)
    buffer2.seek(0)
    model_key = "models/model.pth"
    s3.put_object(Bucket=bucket, Key=model_key, Body=buffer2)

    return model_key
