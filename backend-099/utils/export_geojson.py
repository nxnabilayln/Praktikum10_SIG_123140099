import json

# Koordinat referensi Bandar Lampung
BASE_LAT = -5.360000
BASE_LNG = 105.300000


def export_geojson(data):

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for idx, obj in enumerate(data):

        x1, y1, x2, y2 = obj["bbox"]

        # Titik tengah bounding box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Simulasi konversi pixel ke koordinat
        # (karena sample.jpg tidak memiliki georeferensi)
        lat = BASE_LAT - (center_y * 0.00001)
        lng = BASE_LNG + (center_x * 0.00001)

        feature = {

            "type": "Feature",

            "geometry": {
                "type": "Point",
                "coordinates": [
                    lng,
                    lat
                ]
            },

            "properties": {

                "detection_id": idx + 1,

                "confidence": round(
                    obj["conf"],
                    3
                ),

                "source":
                "YOLOv8 + Tiling",

                "type":
                "Object Detection"

            }
        }

        geojson["features"].append(
            feature
        )

    with open(
        "outputs/detections.geojson",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            geojson,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"GeoJSON berhasil dibuat ({len(geojson['features'])} objek)"
    )

    return geojson