from flask import Flask, request, jsonify, send_from_directory
import os
import csv
import shutil

app = Flask(__name__, static_folder="../frontend", static_url_path="")

BASE_DIR = "../images_raw"
CSV_FILE = "../labels.csv"

OUTPUT_DIR = "../dataset_classification"
CLEAN_OUT = os.path.join(OUTPUT_DIR, "clean")
DIRTY_OUT = os.path.join(OUTPUT_DIR, "dirty")

os.makedirs(CLEAN_OUT, exist_ok=True)
os.makedirs(DIRTY_OUT, exist_ok=True)

VALID_CLASSES = {"dishes", "stain", "clothes", "garbage", "food", "full_garbage","misplaced_items"}

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("filename,x1,y1,x2,y2,label\n")

images = []

for folder in ["clean", "dirty"]:
    folder_path = os.path.join(BASE_DIR, folder)
    for f in os.listdir(folder_path):
        if f.lower().endswith((".jpg",".png",".jpeg")):
            images.append({
                "folder": folder,
                "filename": f
            })

current_index = 0
clean_count = 0
dirty_count = 0

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/next-image")
def next_image():
    global current_index

    if current_index >= len(images):
        return jsonify({"done": True})

    item = images[current_index]
    current_index += 1

    return jsonify({
        "filename": item["filename"],
        "folder": item["folder"],
        "url": f"/image/{item['folder']}/{item['filename']}"
    })

@app.route("/image/<folder>/<filename>")
def serve_image(folder, filename):
    return send_from_directory(os.path.join(BASE_DIR, folder), filename)

@app.route("/save", methods=["POST"])
def save():
    global clean_count, dirty_count

    data = request.json
    filename = data["filename"]
    folder = data["folder"]
    boxes = data["boxes"]

    is_dirty = (folder == "dirty")

    with open(CSV_FILE, "a") as f:
        writer = csv.writer(f)

        if is_dirty:
            for box in boxes:
                label = box["label"].strip().lower()

                if label not in VALID_CLASSES:
                    continue

                writer.writerow([
                    f"{folder}/{filename}",
                    box["x1"],
                    box["y1"],
                    box["x2"],
                    box["y2"],
                    label
                ])

    src = os.path.join(BASE_DIR, folder, filename)
    name, ext = os.path.splitext(filename)

    if is_dirty:
        new_name = f"dirty_{dirty_count}{ext}"
        dst = os.path.join(DIRTY_OUT, new_name)
        dirty_count += 1
    else:
        new_name = f"clean_{clean_count}{ext}"
        dst = os.path.join(CLEAN_OUT, new_name)
        clean_count += 1

    shutil.copy(src, dst)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True, use_reloader=False)