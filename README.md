# Cleanliness Tracker

I'm trying to train a model that can look at a picture of a room and tell how clean it is. It uses YOLOv8 to find the things that make a room messy (dishes, clothes on the floor, trash, etc.), and the plan is to turn what it finds into a score.

This is early. The whole pipeline works from labeling to training, but I've only labeled a handful of images so far, so the model doesn't really work yet. The first training run got an mAP@50 of about 0.09, which is basically a baseline. Labeling more images is the next step.

## Classes

`dishes`, `stain`, `clothes`, `garbage`, `food`, `full_garbage`, `misplaced_items`

These are in `data.yaml` (for training) and in `CLASS_MAP` / `VALID_CLASSES` in the scripts. If I add one it has to be added in all of those places.

## How the pieces fit

1. Put photos in `Image_annotator/images_raw/clean/` and `images_raw/dirty/`
2. Label them with the browser tool (`backend/` + `frontend/`), which appends boxes to `labels.csv`
3. `convert_to_yolo.py` turns `labels.csv` into YOLO label files
4. `split_dataset.py` splits the images and labels 80/20 into train and val
5. `train.py` trains
6. `main.py` runs a model on some pictures so I can look at the results

## Files

### main.py

Loads `yolov8x.pt`, runs it on every image in `images/`, and pops up each result with the boxes drawn on it. Right now it's using the stock pretrained model, not mine. To use mine, change it to `runs/detect/train/weights/best.pt`.

### Image_annotator/backend/app.py

A small Flask server for the labeling tool. When it starts it lists every image in `images_raw/clean` and `images_raw/dirty` and creates the output folders.

- `index()` - `/` serves the labeling page
- `next_image()` - `/next-image` gives the next image's filename, folder, and URL, or `{done: true}` when there's nothing left. It keeps track of where it is with a global counter, so restarting the server starts over from the first image.
- `serve_image(folder, filename)` - `/image/<folder>/<filename>` sends the actual image file
- `save()` - `/save` gets the boxes for one image. For dirty images it writes each box with a valid label to `labels.csv` as `folder/filename,x1,y1,x2,y2,label`. Boxes on clean images aren't saved, since a clean image isn't supposed to have anything in it. It also copies the image into `dataset_classification/clean` or `/dirty` renamed to `clean_N` / `dirty_N`, so I get a clean/dirty classification dataset out of the same labeling pass.

Runs on port 5050: `cd Image_annotator/backend && python app.py`, then go to `http://localhost:5050`.

### Image_annotator/frontend/script.js

The labeling page. The image shows with a canvas on top of it that you draw on.

- `resizeCanvas()` - makes the canvas the same size as the image on screen, runs whenever a new image loads
- `getMousePos(e)` / `getTouchPos(e)` - pointer position relative to the canvas. There are two so it works on my phone too.
- `draw()` - redraws the saved boxes in green with their labels and the one you're drawing in blue
- mouse and touch listeners - press to start a box, drag to size it, let go to finish
- `saveBox()` - takes the label from the dropdown (or the text box if you pick "other") and adds the box to the list
- `nextImage()` - POSTs this image's boxes to `/save` and loads the next one
- `loadNext()` - gets the next image from `/next-image`. Clean images get skipped automatically after 200ms since there's nothing to label in them.

### Image_annotator/Anotator.py

The first version of the labeling tool, before the browser one. It's desktop only using OpenCV. You click twice to draw a box and type the label in the terminal.

- `print_instructions()` - prints the keyboard controls
- `draw_ui(temp, image_name)` - draws the filename, box count, and controls on the image
- `click_event(...)` - first click starts a box, second click finishes it
- `annotate_image(image_path)` - the loop for one image. `n` saves the box you drew (asks for a label), `u` undoes, `r` resets, `d` writes the boxes to `labels.csv` and goes to the next image, `q` quits.
- `main()` - goes through every image in `images/`

The browser tool replaced this. It also writes just the filename without the `clean/` or `dirty/` folder in front, so its rows don't work with `convert_to_yolo.py`.

### Image_annotator/convert_to_yolo.py

Turns `labels.csv` into YOLO format, one `.txt` per image in `dataset/labels/all/`, where each line is `class x_center y_center width height` with everything as a fraction of the image size.

It groups the rows by image and opens each image to get its real size. Then for each box it:
- sorts x1/x2 and y1/y2, since if you drag a box up or left the "start" corner isn't the top left
- clamps it to the image edges
- throws it out if it ends up with zero width or height
- converts to YOLO numbers

Rows with a label that isn't in `CLASS_MAP` get skipped.

### Image_annotator/split_dataset.py

Shuffles every image in `images_raw/clean` and `/dirty` and copies 80% to `dataset/images/train` and 20% to `dataset/images/val`, with their label files going to the matching `labels/` folders.

- `move(data, img_dest, lbl_dest)` - copies each image and its label file. If an image has no label file (every clean image) it makes an empty one. YOLO reads an empty label file as "nothing in this picture", which is what I want for clean rooms.

The shuffle isn't seeded, so every run gives a different split.

### Image_annotator/train.py

Fine-tunes `yolov8n.pt` (the small one) on `data.yaml` for 50 epochs at 640px. Results go to `runs/detect/train/`.

### Image_annotator/data.yaml

Where the dataset is and the class names, for YOLO.

## Setup

```
pip install ultralytics opencv-python flask
```

Photos, the datasets, training runs, and `.pt` files aren't in the repo. They're either too big (`yolov8x.pt` is over GitHub's 100MB limit) or they're pictures of real rooms. Ultralytics downloads the base models on its own the first time.

## Things to fix

- Label more images. This is the big one.
- The browser tool saves box coordinates in screen pixels, but `convert_to_yolo.py` divides by the image's real size. If the image is shown smaller or bigger than its actual resolution, the boxes will be off. I need to check this, it could be part of why the first run was so bad.
- Actually turn detections into a cleanliness score.
