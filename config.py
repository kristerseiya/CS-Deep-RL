class Args:
    def __init__(self):
        self.seed = 40
        self.data_dir = "test_dir/"
        self.tmax = 5
        self.Tmax = 150000
        self.max_episode = 30000
        self.w_filter_size = 33
        self.lr_init = 1e-3
        self.image_size = 64
        self.gamma = 0.9
        self.n = self.image_size ** 2
        self.m = int(0.2 * self.n)
        self.batch_size = 1
