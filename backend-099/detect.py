import cv2
import json
from ultralytics import YOLO
from utils.tile import create_tiles

model = YOLO("yolov8n.pt")

img = cv2.imread("sample.jpg")

if img is None:
    raise Exception("sample.jpg tidak ditemukan")

# membagi jadi tiles
tiles = create_tiles(img)


results = []


for tile, x, y in tiles:

    output = model(
        tile,
        verbose=False
    )

    for box in output[0].boxes:

        x1, y1, x2, y2 = (
            box.xyxy[0]
            .tolist()
        )

        results.append({

            "bbox":[
                x1+x,
                y1+y,
                x2+x,
                y2+y
            ],

            "class":
            int(box.cls[0]),

            "conf":
            float(box.conf[0])

        })


print(
    "Jumlah objek:",
    len(results)
)


with open(
    "outputs/temp.json",
    "w"
) as f:

    json.dump(
        results,
        f,
        indent=2
    )
    
from utils.export_geojson import export_geojson

export_geojson(
    results
)

print("Deteksi selesai")