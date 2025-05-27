import os
import torch
import random
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from model import MultiLabelClassifier

def show_image(img_array) -> None:
    plt.title(f'Size: {len(img_array[0])} x {len(img_array)}')
    plt.axis('off')
    plt.imshow(img_array)
    plt.show()

data_path = Path('data')
device = 'cuda' if torch.cuda.is_available() else 'cpu'

data_transform = transforms.Compose([
                    transforms.Resize(size=(128,128)),
                    transforms.ToTensor()
                ])

train_data_path = data_path / 'train'
test_data_path = data_path / 'test'

train_data = datasets.ImageFolder(root=train_data_path,
                                  transform=data_transform,
                                  target_transform=None)

test_data = datasets.ImageFolder(root=test_data_path,
                                 transform=data_transform)

BATCH_SIZE = 32

train_dataloader = DataLoader(dataset = train_data,
                              batch_size = BATCH_SIZE,
                              num_workers = os.cpu_count(),
                              shuffle = True)

test_dataloader = DataLoader(dataset = test_data,
                             batch_size = BATCH_SIZE,
                             num_workers = os.cpu_count())

model = MultiLabelClassifier(in_count = 3, hidden_count = 10, out_count = len(train_data.classes))

loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

epochs = 20

model.to(device)

train_losses = []
test_losses = []

for epoch in range(epochs):
    model.train()

    train_loss_per_batch = 0

    for batch in train_dataloader:
        inputs = batch[0]
        labels_truth = batch[1]

        inputs = inputs.to(device)
        labels_truth = labels_truth.to(device)

        labels_pred = model(inputs)

        train_loss = loss_fn(labels_pred, labels_truth)

        optimizer.zero_grad()

        train_loss.backward()

        optimizer.step()

        train_loss_per_batch += train_loss / 32

    ### Evaluation
    model.eval()

    test_loss_per_batch = 0

    with torch.inference_mode():
        for batch in test_dataloader:
            inputs = batch[0]
            labels_truth = batch[1]

            inputs = inputs.to(device)
            labels_truth = labels_truth.to(device)

            labels_pred = model(inputs)

            test_loss = loss_fn(labels_pred, labels_truth)
            test_loss_per_batch += test_loss / 32

    print(f'Epoch {epoch}: Training Loss: {train_loss_per_batch} | Testing Loss: {test_loss_per_batch}')
    train_losses.append(train_loss_per_batch.cpu().detach().numpy())
    test_losses.append(test_loss_per_batch.cpu().detach().numpy())

plt.plot(train_losses)
plt.plot(test_losses)
plt.show()
