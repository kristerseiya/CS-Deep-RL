import scipy.linalg as linalg
import numpy as np
import os
import glob
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import Dataset, DataLoader
from PIL import Image


class A_transform:
    def __init__(self, A):
        self.A = torch.tensor(A, dtype=torch.float)

    def __call__(self, image):
        x = torch.flatten(image, start_dim=0, end_dim=-1)
        x = torch.unsqueeze(x, dim=-1)
        y = torch.matmul(self.A, x)
        return y
    

class MyCSDataset(Dataset):
    def __init__(self, data_dir, A, transform=None):
        self.image_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
        self.A_transform = A_transform(A)
        self.transform = transform

    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx):
        image = Image.open(self.image_files[idx])
        image_x = self.transform(image) if self.transform else image
        flat_y = self.A_transform(image_x)
        flat_x = torch.flatten(image_x, start_dim=0, end_dim=-1).unsqueeze(-1)

        return image_x, flat_x, flat_y


def generate_A(m, n):
    assert m <= n, "m should be less than equal to n"

    dft_mat = linalg.dft(n) / np.sqrt(n)
    random_select_row = np.random.permutation(n)
    A = dft_mat[random_select_row[:m], :].real

    return A


def get_transform(image_size):
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((int(1.1 * image_size), int(1.1 * image_size))),
        transforms.RandomCrop(image_size),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ])

    return transform


def get_cs_dataloader(dataset, batch_size, num_workers):
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    return dataloader