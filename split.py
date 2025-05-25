import os
import argparse
import random
from pathlib import Path
from multiprocessing import Pool

def split_dir(dir: str):
    shuffled_image_files = os.listdir(dir)
    random.shuffle(shuffled_image_files)
    num_images = len(shuffled_image_files)
    num_train = int(split_ratio * num_images)
    train_image_files = shuffled_image_files[:num_train]
    test_image_files = shuffled_image_files[num_train:]

    split_train_dir = Path(f'./train/{dir}')
    split_test_dir = Path(f'./test/{dir}')

    if not split_train_dir.exists():
        os.mkdir(split_train_dir)

    if not split_test_dir.exists():
        os.mkdir(split_test_dir)

    for file in train_image_files:
        os.system(f'cp {dir}/{file} {split_train_dir}')

    for file in test_image_files:
        os.system(f'cp {dir}/{file} {split_test_dir}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', nargs='+', help='List of directories to split')

    args = parser.parse_args()

    train_dir = Path('./train')
    test_dir = Path('./test')

    if not train_dir.exists():
        os.mkdir(train_dir)
    
    if not test_dir.exists():
        os.mkdir(test_dir)
    
    split_ratio = 0.75

    valid_dirs = [ dir for dir in args.dirs if dir != train_dir and dir != test_dir and os.path.isdir(dir) ]

    with Pool(len(valid_dirs)) as p:
        p.map(split_dir, valid_dirs)
