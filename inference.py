import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import numpy as np
from models import FCN, RewardConv
from config import Args, ActionSpace
from utils import get_device, get_min_max_data, rescale_tensor_01
from data import *


def reconstruct(model, reward_conv, Q_init, min_val, max_val, tmax, dataloader, actions, device, out_dir):
    model = model.to(device)
    reward_conv = reward_conv.to(device)
    model.eval()
    reward_conv.eval()

    # just get 1 image from dataloader
    for target_state, _, state_y in dataloader:
        curr_state = torch.matmul(Q_init, state_y).reshape(-1, 1, args.image_size, args.image_size)
        curr_state = rescale_tensor_01(curr_state, min_val, max_val)

        for _ in range(tmax):
            curr_state = curr_state.to(device)

            # feed through network
            policy, _ = model(curr_state)

            # sample and get action
            action_idx = policy.sample()
            action = action_idx.clone().detach().cpu().float()
            action.apply_(lambda x: actions[int(x)])
            action = torch.unsqueeze(action, dim=1)

            # get next_state
            next_state = curr_state.detach().cpu() * action
            curr_state = next_state

        # save images
        original = target_state.detach().cpu().numpy().squeeze()
        reconstructed = curr_state.detach().cpu().numpy().squeeze()

        print(f"original shape: {original.shape}")
        print(f"reconstructed shape: {reconstructed.shape}")
        print(f"original min: {original.min()}, max: {original.max()}")
        print(f"reconstructed min: {reconstructed.min()}, max: {reconstructed.max()}")
        break

    print("DONE")


if __name__ == "__main__":
    args = Args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = get_device()

    # data related stuff
    A = generate_A(args.m, args.n)
    transform = get_transform(args.image_size)
    dataset = MyCSDataset(args.data_dir, A, transform=transform)
    qinit_dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2)

    # calc Qinit
    print("calculating Qinit...")
    Q_init = calc_Qinit(qinit_dataloader, device=device)
    print(f"Qinit shape: {Q_init.shape}")

    # get min and max
    min_val, max_val = get_min_max_data(Q_init, qinit_dataloader)

    # define models
    actions = ActionSpace().action_space
    model = FCN(action_size=len(actions)).to(device)
    reward_conv = RewardConv(args.w_filter_size).to(device)

    # load state dicts from trained models
    model.load_state_dict(torch.load(os.path.join(args.out_dir, "model.pth")))
    reward_conv.load_state_dict(torch.load(os.path.join(args.out_dir, "reward_conv.pth")))

    # reconstruct
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True, num_workers=2)

    # call reconstruction
    reconstruct(model, reward_conv, Q_init, min_val, max_val, args.tmax, dataloader, actions, device, args.out_dir)
