import os
import shutil
import random

ALL_LABELS = "dataset/labels/all"
IMAGE_BASE = "images_raw"

TRAIN_IMG = "dataset/images/train"
VAL_IMG = "dataset/images/val"
TRAIN_LBL = "dataset/labels/train"
VAL_LBL = "dataset/labels/val"

for p in [TRAIN_IMG, VAL_IMG, TRAIN_LBL, VAL_LBL]:
    os.makedirs(p, exist_ok=True)

images = []

for folder in ["clean", "dirty"]:
    path = os.path.join(IMAGE_BASE, folder)
    for f in os.listdir(path):
        if f.endswith((".png",".jpg",".jpeg")):
            images.append((folder, f))

random.shuffle(images)

split = int(len(images) * 0.8)
train = images[:split]
val = images[split:]

def move(data, img_dest, lbl_dest):
    for folder, filename in data:

        src_img = os.path.join(IMAGE_BASE, folder, filename)
        dst_img = os.path.join(img_dest, filename)

        shutil.copy(src_img, dst_img)

        label_name = os.path.splitext(filename)[0] + ".txt"
        src_lbl = os.path.join(ALL_LABELS, label_name)
        dst_lbl = os.path.join(lbl_dest, label_name)

        if os.path.exists(src_lbl):
            shutil.copy(src_lbl, dst_lbl)
        else:
            open(dst_lbl, "w").close()

move(train, TRAIN_IMG, TRAIN_LBL)
move(val, VAL_IMG, VAL_LBL)

print("Split complete")