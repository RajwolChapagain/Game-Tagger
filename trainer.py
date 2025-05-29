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
from dataset import CustomDataset
from torchmetrics.classification import MultilabelAccuracy, MultilabelPrecision, MultilabelRecall, MultilabelF1Score

def show_image(img_array) -> None:
    plt.title(f'Size: {len(img_array[0])} x {len(img_array)}')
    plt.axis('off')
    plt.imshow(img_array)
    plt.show()

data_path = Path('data')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
db_file = 'tag_info.db'

data_transform = transforms.Compose([
                    transforms.Resize(size=(128,128)),
                    transforms.ToTensor()
                ])

train_data = CustomDataset(data_path=data_path,
                           db_file=db_file,
                           table='train',
                           transform=data_transform)

test_data = CustomDataset(data_path=data_path,
                           db_file=db_file,
                           table='test',
                           transform=data_transform)

BATCH_SIZE = 64

train_dataloader = DataLoader(dataset = train_data,
                              batch_size = BATCH_SIZE,
                              num_workers = os.cpu_count(),
                              shuffle = True)

test_dataloader = DataLoader(dataset = test_data,
                             batch_size = BATCH_SIZE,
                             num_workers = os.cpu_count())

model = MultiLabelClassifier(in_count = 3, hidden_count = 10, out_count = len(train_data.classes))

loss_fn = torch.nn.BCEWithLogitsLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

epochs = 5

model.to(device)

train_losses = []
test_losses = []

for epoch in range(epochs):
    model.train()

    train_loss = 0

    for batch in train_dataloader:
        inputs = batch[0]
        labels_truth = batch[1]

        inputs = inputs.to(device)
        labels_truth = labels_truth.to(device)

        labels_pred = model(inputs)

        loss = loss_fn(labels_pred, labels_truth)
        train_loss += loss.item()

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()
        
    train_loss /= len(train_dataloader)
    train_losses.append(train_loss)

    test_loss = 0

    metric_acc = MultilabelAccuracy(num_labels=12, threshold=0.4).to(device)
    metric_prec = MultilabelPrecision(num_labels=12, threshold=0.4).to(device)
    metric_rec = MultilabelRecall(num_labels=12, threshold=0.4).to(device)
    metric_f1 = MultilabelF1Score(num_labels=12, threshold=0.4).to(device)

    for i in range (len(test_dataloader)):
        batch = next(iter(test_dataloader))
        inputs = batch[0]
        labels_truth = batch[1]

        inputs = inputs.to(device)
        labels_truth = labels_truth.to(device)

        labels_pred = model(inputs)

        loss = loss_fn(labels_pred, labels_truth)
        test_loss += loss.item()
        
        accuracy = metric_acc(labels_pred, labels_truth)
        precision = metric_prec(labels_pred, labels_truth)
        recall = metric_rec(labels_pred, labels_truth)
        f1_score = metric_f1(labels_pred, labels_truth)

    accuracy = metric_acc.compute()
    precision = metric_prec.compute()
    recall = metric_rec.compute()
    f1_score = metric_f1.compute()

    test_loss /= len(test_dataloader)
    test_losses.append(test_loss)

    print(f'Epoch {epoch}: Train Loss: {train_loss} | Test Loss: {test_loss}')
    print(f'\t Accuracy: {accuracy} | Precision: {precision} | Recall: {recall} | F1 Score: {f1_score}')

plt.plot(train_losses, label='train_loss')
plt.plot(test_losses, label='test_loss')
plt.legend()
plt.show()

save = input('Do you want to save this model? [y/n] ')

if save.lower() == 'y' or save.lower() == 'yes':
    model_name = input('Enter model name: ')

    model_path = Path('models')
    model_path.mkdir(parents=True, exist_ok=True)

    model_save_path = model_path/model_name

    torch.save(model.state_dict(), model_save_path)
