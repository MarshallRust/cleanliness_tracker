let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let image = document.getElementById("image");

let labelSelect = document.getElementById("labelSelect");
let customLabelInput = document.getElementById("customLabel");

let boxes = [];
let currentBox = null;
let drawing = false;
let currentImage = "";
let currentFolder = "";

function resizeCanvas() {
    canvas.width = image.clientWidth;
    canvas.height = image.clientHeight;
}

image.onload = resizeCanvas;

function getMousePos(e) {
    let rect = canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

function getTouchPos(e) {
    let rect = canvas.getBoundingClientRect();
    let touch = e.touches[0] || e.changedTouches[0];
    return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top
    };
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    boxes.forEach(b => {
        ctx.strokeStyle = "green";
        ctx.lineWidth = 2;
        ctx.strokeRect(b.x1, b.y1, b.x2 - b.x1, b.y2 - b.y1);
        ctx.fillText(b.label, b.x1, b.y1 - 5);
    });

    if (currentBox) {
        ctx.strokeStyle = "blue";
        ctx.lineWidth = 2;
        ctx.strokeRect(
            currentBox.x1,
            currentBox.y1,
            currentBox.x2 - currentBox.x1,
            currentBox.y2 - currentBox.y1
        );
    }
}

canvas.addEventListener("mousedown", (e) => {
    drawing = true;
    let pos = getMousePos(e);
    currentBox = { x1: pos.x, y1: pos.y, x2: pos.x, y2: pos.y };
});

canvas.addEventListener("mousemove", (e) => {
    if (!drawing) return;
    let pos = getMousePos(e);
    currentBox.x2 = pos.x;
    currentBox.y2 = pos.y;
    draw();
});

canvas.addEventListener("mouseup", (e) => {
    drawing = false;
    let pos = getMousePos(e);
    currentBox.x2 = pos.x;
    currentBox.y2 = pos.y;
    draw();
});

canvas.addEventListener("touchstart", (e) => {
    e.preventDefault();
    drawing = true;
    let pos = getTouchPos(e);
    currentBox = { x1: pos.x, y1: pos.y, x2: pos.x, y2: pos.y };
}, { passive: false });

canvas.addEventListener("touchmove", (e) => {
    e.preventDefault();
    if (!drawing) return;
    let pos = getTouchPos(e);
    currentBox.x2 = pos.x;
    currentBox.y2 = pos.y;
    draw();
}, { passive: false });

canvas.addEventListener("touchend", (e) => {
    e.preventDefault();
    drawing = false;
}, { passive: false });

labelSelect.addEventListener("change", () => {
    if (labelSelect.value === "other") {
        customLabelInput.style.display = "inline-block";
    } else {
        customLabelInput.style.display = "none";
    }
});

function saveBox() {
    if (!currentBox) return;

    let selected = labelSelect.value;
    let label = "";

    if (!selected) {
        alert("Select a label");
        return;
    }

    if (selected === "other") {
        label = customLabelInput.value.trim().toLowerCase();

        if (!label) {
            alert("Enter custom label");
            return;
        }
    } else {
        label = selected;
    }

    currentBox.label = label;
    boxes.push(currentBox);

    currentBox = null;

    labelSelect.value = "";
    customLabelInput.value = "";
    customLabelInput.style.display = "none";

    draw();
}

function nextImage() {
    fetch("/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            filename: currentImage,
            folder: currentFolder,
            boxes: boxes
        })
    });

    boxes = [];
    currentBox = null;

    loadNext();
}

function loadNext() {
    fetch("/next-image")
        .then(res => res.json())
        .then(data => {
            if (data.done) {
                alert("Done!");
                return;
            }

            currentImage = data.filename;
            currentFolder = data.folder;

            document.getElementById("imageName").innerText =
                data.folder + "/" + data.filename;

            image.src = data.url;

            if (currentFolder === "clean") {
                setTimeout(() => {
                    nextImage();
                }, 200);
            }
        });
}

loadNext();