import cv2
import os

INPUT_DIR = "images"
CSV_FILE = "labels.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("filename,x1,y1,x2,y2,label\n")

boxes = []
current_box = []
drawing = False
image = None

def print_instructions():
    print("\n--- Annotation Tool ---")
    print("Click twice to draw a box\n")
    print("Controls:")
    print("  n = save current box")
    print("  u = undo last box")
    print("  r = reset all boxes")
    print("  d = done (next image)")
    print("  q = quit program\n")

def draw_ui(temp, image_name):
    y = 20
    for line in [
        f"Image: {image_name}",
        f"Boxes: {len(boxes)}",
        "",
        "Click x2 = draw",
        "n = save",
        "u = undo",
        "r = reset",
        "d = next",
        "q = quit"
    ]:
        cv2.putText(temp, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        y += 20

def click_event(event, x, y, flags, param):
    global drawing, current_box

    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing:
            current_box = [(x, y)]
            drawing = True
        else:
            current_box.append((x, y))
            drawing = False

def annotate_image(image_path):
    global image, boxes, current_box, drawing

    image = cv2.imread(image_path)
    boxes = []
    current_box = []
    drawing = False

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_event)

    while True:
        temp = image.copy()

        for (p1, p2, label) in boxes:
            cv2.rectangle(temp, p1, p2, (0, 255, 0), 2)
            cv2.putText(temp, label, (p1[0], p1[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        if len(current_box) == 2:
            cv2.rectangle(temp, current_box[0], current_box[1], (255, 0, 0), 2)

        draw_ui(temp, os.path.basename(image_path))

        cv2.imshow("image", temp)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("n"):
            if len(current_box) == 2:
                label = input("Label: ")
                boxes.append((current_box[0], current_box[1], label))
                print(f"Saved: {label}")
                current_box = []

        elif key == ord("u"):
            if boxes:
                removed = boxes.pop()
                print(f"Removed: {removed[2]}")

        elif key == ord("r"):
            boxes = []
            current_box = []
            print("Reset")

        elif key == ord("d"):
            with open(CSV_FILE, "a") as f:
                for (p1, p2, label) in boxes:
                    f.write(f"{os.path.basename(image_path)},{p1[0]},{p1[1]},{p2[0]},{p2[1]},{label}\n")

            print(f"Saved {len(boxes)} boxes")
            break

        elif key == ord("q"):
            return False

    cv2.destroyAllWindows()
    return True

def main():
    print_instructions()

    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".jpg",".png",".jpeg"))]

    for img in images:
        print(f"\nProcessing: {img}")
        if not annotate_image(os.path.join(INPUT_DIR, img)):
            break

if __name__ == "__main__":
    main()