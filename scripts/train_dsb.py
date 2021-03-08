import argparse
import os

import torch
import torch_em
from torch_em.model import UNet2d
from torch_em.trainer.wandb_logger import WandbLogger

parser = argparse.ArgumentParser()
parser.add_argument('root', type=str,
                    help="Path to dsb2018 folder with train and test subfolders")
parser.add_argument('--iterations', '-i', type=int, default=51)
args = parser.parse_args()
root = args.root

model = UNet2d(in_channels=1, out_channels=2, initial_features=16)

# transform to go from instance segmentation labels
# to foreground/background and boundary channel
label_transform = torch_em.transform.BoundaryTransform(
    add_binary_target=True, ndim=2
)

batch_size = 4
train_loader = torch_em.default_segmentation_loader(
    os.path.join(root, "train/images"), "*.tif",
    os.path.join(root, "train/masks"), "*.tif",
    batch_size=batch_size, patch_shape=(1, 256, 256),
    label_transform=label_transform,
    n_samples=10*batch_size
)
val_loader = torch_em.default_segmentation_loader(
    os.path.join(root, "test/images"), "*.tif",
    os.path.join(root, "test/masks"), "*.tif",
    batch_size=batch_size, patch_shape=(1, 256, 256),
    label_transform=label_transform,
    n_samples=1*batch_size
)

# the trainer object that handles the training details
# the model checkpoints will be saved in "checkpoints/dsb-boundary-model"
# the tensorboard logs will be saved in "logs/dsb-boundary-model"
trainer = torch_em.default_segmentation_trainer(
    name="dsb-boundary-model",
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    learning_rate=1e-4,
    device=torch.device("cpu"),
    mixed_precision=False,
    logger=WandbLogger,
    log_image_interval=10
)
trainer.fit(iterations=args.iterations)