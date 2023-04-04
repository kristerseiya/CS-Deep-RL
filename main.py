import pfrl
import torch
from models import FCN


if __name__ == '__main__':
    x = torch.randn(1, 1, 64, 64)
    model = FCN(action_size=6)
    policy, value = model(x)

    print(policy.shape)
    print(value.shape)
