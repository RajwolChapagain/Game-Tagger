import os
import random
from pathlib import Path
from multiprocessing import Pool

def split_dir(dir: str, data_dir: Path = Path('./data')):
    shuffled_image_files = os.listdir(f'{data_dir}/{dir}')
    random.shuffle(shuffled_image_files)
    num_images = len(shuffled_image_files)
    num_train = int(split_ratio * num_images)
    train_image_files = shuffled_image_files[:num_train]
    test_image_files = shuffled_image_files[num_train:]

    split_train_dir = data_dir / 'train' / dir
    split_test_dir = data_dir / 'test' / dir

    if not split_train_dir.exists():
        os.mkdir(split_train_dir)

    if not split_test_dir.exists():
        os.mkdir(split_test_dir)

    for file in train_image_files:
        os.system(f'cp {data_dir}/{dir}/{file} {split_train_dir}')

    for file in test_image_files:
        os.system(f'cp {data_dir}/{dir}/{file} {split_test_dir}')

if __name__ == '__main__':
    data_dir = Path('./data')

    if not data_dir.exists():
        print(f'Error: {data_dir} directory doesn\'t exist in the current directory')
        exit()

    train_dir = data_dir / 'train'
    test_dir = data_dir / 'test'

    if not train_dir.exists():
        os.mkdir(train_dir)
    
    if not test_dir.exists():
        os.mkdir(test_dir)
    
    split_ratio = 0.75

    all_dirs = os.listdir(data_dir)

    valid_dirs = [ dir for dir in all_dirs if (data_dir / dir) != train_dir and (data_dir / dir) != test_dir ]

    with Pool(len(valid_dirs)) as p:
        p.map(split_dir, valid_dirs)
