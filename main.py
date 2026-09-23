from ultralytics import YOLO
import os

model = YOLO("yolov8x.pt")
folder_path = "images"

for filename in os.listdir(folder_path):
    image_path = os.path.join(folder_path, filename)

    results = model(image_path)
    results[0].show()