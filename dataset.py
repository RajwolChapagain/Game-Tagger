import torch
import sqlite3
from PIL import Image
from pathlib import Path
from torchvision import transforms
from torch.utils.data import Dataset

class CustomDataset(Dataset):
    def __init__(self, data_path: Path, db_file: str, table: str, transform=transforms.Compose([transforms.ToTensor()])) -> None:
        self.data_path = data_path
        self.db_path = data_path/db_file
        self.table = table
        self.classes = CustomDataset.get_classes(self.db_path) 
        self.transform = transform

    def __len__(self) -> int:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        result = cursor.execute(
                f'''
                SELECT count(*) from {self.table};
                '''
        )

        length = result.fetchone()[0]
        connection.close()
        return length

    def __getitem__(self, index: int) -> tuple[torch.Tensor, list[int]]:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        result = cursor.execute(
                f'''
                SELECT * from {self.table} LIMIT 1 OFFSET {index};
                '''
        )

        row = result.fetchone()
        app_id = row[0]
        tag_info = list(row[1:])

        img = Image.open(self.data_path/f'{app_id}.jpeg')
        transformed_img = self.transform(img)

        connection.close()

        return (transformed_img, tag_info)

    def get_classes(db_file: Path) -> list[str]:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        result = cursor.execute(
                f'''
                PRAGMA table_info({self.table});
                '''
        )

        classes = []

        for item in result.fetchall():
            tag = item[1]
            if tag != 'app_id':
                classes.append(tag)

        connection.close()

        return classes
