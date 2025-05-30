import torch
import requests
from torchvision import transforms
from model import MultiLabelClassifier
from pathlib import Path
from PIL import Image
from scraper import tag_dict
from fastapi import FastAPI, UploadFile, File
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

model_path = Path('models/')
model_name = 'default'

model_save_path = model_path/model_name

num_labels = 5
model = MultiLabelClassifier(in_count = 3, hidden_count = 10, out_count = num_labels)

model.load_state_dict(torch.load(model_save_path))

def get_pred(img: Image) -> list[str]:
    data_transform = transforms.Compose([
        transforms.Resize(size=(128, 128)),
        transforms.ToTensor()
    ])

    transformed_img = data_transform(img)

    predicted_labels = []

    model.eval()
    with torch.inference_mode():
        threshold = 0.35
        pred_logits = model(transformed_img.unsqueeze(0)) # Have to insert a dimension at start representing batch size of 1
        pred_labels = torch.round(torch.sigmoid(pred_logits))# >= threshold).int()
        keys = list(tag_dict.keys())

        pred_labels = pred_labels.flatten().tolist()
        for pred, label in zip(pred_labels, keys):
            if pred == 1:
                predicted_labels.append(label)

    return predicted_labels

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/predict')
async def predict(img: UploadFile = File(...)):
    contents = await img.read()
    img = Image.open(BytesIO(contents))
    return {'tags': get_pred(img)}
