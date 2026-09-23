import os
import csv
import cv2

CSV_FILE = "labels.csv"
BASE_IMAGE_DIR = "images_raw"
OUTPUT_LABEL_DIR = "dataset/labels/all"

CLASS_MAP = {
    "dishes": 0,
    "stain": 1,
    "clothes": 2,
    "garbage": 3,
    "food": 4,
    "full_garbage": 5,
    "misplaced_items": 6
}

os.makedirs(OUTPUT_LABEL_DIR, exist_ok=True)

data = {}

with open(CSV_FILE, "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        path = row["filename"].strip()
        label = row["label"].strip().lower()

        if label not in CLASS_MAP:
            continue

        if path not in data:
            data[path] = []

        data[path].append(row)

for path, rows in data.items():

    folder, filename = path.split("/")
    image_path = os.path.join(BASE_IMAGE_DIR, folder, filename)

    img = cv2.imread(image_path)
    if img is None:
        continue

    h, w = img.shape[:2]

    txt_name = os.path.splitext(filename)[0] + ".txt"
    txt_path = os.path.join(OUTPUT_LABEL_DIR, txt_name)

    with open(txt_path, "w") as f:

        for row in rows:
            x1 = float(row["x1"])
            y1 = float(row["y1"])
            x2 = float(row["x2"])
            y2 = float(row["y2"])

            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            x1 = max(0, min(x1, w))
            x2 = max(0, min(x2, w))
            y1 = max(0, min(y1, h))
            y2 = max(0, min(y2, h))

            if x2 <= x1 or y2 <= y1:
                continue

            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h
            width = (x2 - x1) / w
            height = (y2 - y1) / h

            class_id = CLASS_MAP[row["label"].lower()]

            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

print("Conversion complete")