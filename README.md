# Cleanliness Tracker

A computer-vision project that scores how clean a room is. A YOLOv8 object detector finds the things that make a room messy (dishes, clothes on the floor, garbage, stains, and so on), and the detections are rolled up into a clean/dirty judgment.

> **Status: early / in progress.** The labeling and training pipeline works end to end, but only a small part of the dataset is annotated so far. The first training run is a baseline, not a usable model yet (see [Results so far](#results-so-far)).

## Pipeline

```
photos (clean/ dirty/)
   │
   ├─ Image_annotator/backend + frontend   Flask + browser tool for drawing labeled boxes
   ├─ Image_annotator/Anotator.py          OpenCV desktop version of the same tool
   │        ▼
   │   labels.csv   (filename, x1, y1, x2, y2, label)
   │        ▼
   ├─ convert_to_yolo.py   normalizes boxes (handles boxes drawn in any direction and clamps to image bounds) → YOLO .txt labels
   ├─ split_dataset.py     80/20 train/val split
   ├─ train.py             fine-tunes YOLOv8n for 50 epochs at 640 px
   │        ▼
   └─ main.py              runs a model over a folder of images and shows the detections
```

### Classes

`dishes` · `stain` · `clothes` · `garbage` · `food` · `full_garbage` · `misplaced_items`

## Results so far

The first 50-epoch run on the handful of annotated images reached **mAP@50 ≈ 0.09**. That's expected with this little labeled data, and it mainly shows the pipeline runs end to end. Next steps:

1. Annotate the rest of the ~190 collected photos.
2. Retrain and compare against this baseline.
3. Turn per-image detections into a cleanliness score (weighted counts per class).

## Running it

```bash
pip install ultralytics opencv-python flask

# label images in the browser
cd Image_annotator/backend && python app.py      # then open http://localhost:5050

# build the dataset and train
cd Image_annotator
python convert_to_yolo.py
python split_dataset.py
python train.py
```

Photos, datasets, training runs and model weights (`*.pt`) are not in the repo because of size and privacy. Ultralytics downloads the base `yolov8n.pt` / `yolov8x.pt` weights automatically the first time you run it.

## Tech

Python, Ultralytics YOLOv8, OpenCV, Flask, vanilla JS
