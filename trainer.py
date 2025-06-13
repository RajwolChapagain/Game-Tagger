import os
import torch
import random
import sqlite3
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

def get_weights(db: Path) -> list[float]:
    connection = sqlite3.connect(db);
    cursor = connection.cursor();

    columns = cursor.execute(
        '''
        PRAGMA table_info(train);
        '''
    )

    labels = [item[1] for item in columns.fetchall()][1:] # First column is app_id
    
    result = []

    for label in labels:
        num_positive = cursor.execute(
            f'''
            SELECT count(*) FROM train WHERE {label}=1;
            '''
        ).fetchone()[0]

        num_negative = cursor.execute(
            f'''
            SELECT count(*) FROM train WHERE {label}=0;
            '''
        ).fetchone()[0]

        result.append(float(num_negative) / float(num_positive))

    connection.close()
    return result

data_path = Path('data')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
db_file = 'tag_info.db'

data_transform = transforms.Compose([
                    transforms.Lambda(lambda img: img.convert("RGB")),
                    transforms.Resize(size=(256,256)),
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

BATCH_SIZE = 8

train_dataloader = DataLoader(dataset = train_data,
                              batch_size = BATCH_SIZE,
                              num_workers = os.cpu_count(),
                              shuffle = True)

test_dataloader = DataLoader(dataset = test_data,
                             batch_size = BATCH_SIZE,
                             num_workers = os.cpu_count())

label_count = len(train_data.classes)

model = MultiLabelClassifier(in_count = 3, hidden_count = 128, out_count = label_count)

loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=torch.Tensor(get_weights(data_path/db_file)).to(device))
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

epochs = 15

model.to(device)

train_losses = []
test_losses = []

for epoch in range(1, epochs+1):
    print(f'Started training in epoch {epoch}')
    model.train()

    train_loss = 0

    for i, (inputs, labels_truth) in enumerate(train_dataloader, 1):
        if i % 100 == 0:
            print(f'Training batch {i}/{len(train_dataloader)}')
        inputs = inputs.to(device)
        labels_truth = labels_truth.to(device)

        labels_pred = model(inputs)

        loss = loss_fn(labels_pred, labels_truth)
        train_loss += loss.item()

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()
        
    print('Training complete\n')

    train_loss /= len(train_dataloader)
    train_losses.append(train_loss)

    test_loss = 0

    threshold = 0.5
    metric_acc = MultilabelAccuracy(num_labels=label_count, threshold=threshold, average=None).to(device)
    metric_prec = MultilabelPrecision(num_labels=label_count, threshold=threshold, average=None).to(device)
    metric_rec = MultilabelRecall(num_labels=label_count, threshold=threshold, average=None).to(device)
    metric_f1 = MultilabelF1Score(num_labels=label_count, threshold=threshold, average=None).to(device)

    for i, (inputs, labels_truth) in enumerate(test_dataloader, 1):
        if i % 50 == 0:
            print(f'Testing batch {i}/{len(test_dataloader)}')
        inputs = inputs.to(device)
        labels_truth = labels_truth.to(device)

        labels_pred = model(inputs)
        if i == 0:
            print(f'Sample prediction    : {(torch.sigmoid(labels_pred[0]) > threshold).float().cpu().tolist()}')
            print(f'Corresponding truth : {labels_truth[0].cpu().tolist()}')

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
    print(f'\tAccuracy: {accuracy.cpu().tolist()}')
    print(f'\tPrecision: {precision.cpu().tolist()}')
    print(f'\tRecall: {recall.cpu().tolist()}')
    print(f'\tF1 Score: {f1_score.cpu().tolist()}')
    print()


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
