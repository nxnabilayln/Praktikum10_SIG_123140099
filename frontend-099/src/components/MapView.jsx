import { useEffect, useState } from "react";

import { MapContainer, TileLayer, GeoJSON, useMapEvents } from "react-leaflet";

import api from "../config/api";

import L from "leaflet";

import "leaflet/dist/leaflet.css";

function MapView() {
  const [data, setData] = useState(null);

  const [detections, setDetections] = useState(null);

  const [showForm, setShowForm] = useState(false);

  const [editId, setEditId] = useState(null);

  const [nama, setNama] = useState("");

  const [jenis, setJenis] = useState("");

  const [alamat, setAlamat] = useState("");

  const [latitude, setLatitude] = useState("");

  const [longitude, setLongitude] = useState("");

  const colors = {
    Kesehatan: "#ff0000",
    Sekolah: "#0066ff",
    Publik: "#00aa00",
    Masjid: "#8000ff",
    "Perguruan Tinggi": "#ff8800",
    "Kantor Polisi": "#111111",
    "Pusat Perbelanjaan": "#ff1493",
  };

  const fetchData = async () => {
    try {
      const res = await api.get("/api/fasilitas/geojson");

      setData(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  const fetchDetections = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/detections");

      const geojson = await res.json();

      setDetections(geojson);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    fetchData();

    fetchDetections();
  }, []);

  const resetForm = () => {
    setNama("");

    setJenis("");

    setAlamat("");

    setLatitude("");

    setLongitude("");

    setEditId(null);
  };

  const handleAdd = async () => {
    try {
      await api.post("/api/fasilitas/", {
        nama,
        jenis,
        alamat,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
      });

      fetchData();

      setShowForm(false);

      resetForm();

      alert("Data berhasil ditambahkan");
    } catch {
      alert("Gagal tambah data");
    }
  };

  const handleEdit = async () => {
    try {
      await api.put(
        `/api/fasilitas/${editId}`,

        {
          nama,

          jenis,

          alamat,

          latitude: parseFloat(latitude),

          longitude: parseFloat(longitude),
        },
      );

      fetchData();

      setShowForm(false);

      resetForm();

      alert("Data berhasil diupdate");
    } catch {
      alert("Gagal update");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Yakin ingin menghapus?")) return;

    try {
      await api.delete(`/api/fasilitas/${id}`);

      fetchData();
    } catch (err) {
      console.log(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");

    window.location.reload();
  };

  function AddMarkerByClick() {
    useMapEvents({
      click(e) {
        if (showForm) return;

        const target = e.originalEvent.target;

        const popup = target.closest(".leaflet-popup");

        if (popup) return;

        setLatitude(e.latlng.lat.toFixed(6));

        setLongitude(e.latlng.lng.toFixed(6));

        setEditId(null);

        setNama("");

        setJenis("");

        setAlamat("");

        setShowForm(true);
      },
    });

    return null;
  }

  return (
    <div className="map-wrapper">
      <div className="header">
        <h1>WebGIS Bandar Lampung</h1>

        <div className="header-buttons">
          <button
            className="add-btn"
            onClick={() => {
              resetForm();

              setShowForm(true);
            }}
          >
            + Tambah
          </button>

          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <MapContainer center={[-5.36, 105.3]} zoom={13} className="map">
        <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" />

        <AddMarkerByClick />
        {data && (
          <GeoJSON
            data={data}
            pointToLayer={(feature, latlng) =>
              L.circleMarker(latlng, {
                radius: 9,
                fillColor: colors[feature.properties.jenis] || "#00bfff",

                color: "white",

                weight: 2,

                fillOpacity: 1,
              })
            }
            onEachFeature={(feature, layer) => {
              const p = feature.properties;

              const [lng, lat] = feature.geometry.coordinates;

              layer.bindPopup(`

        <div style="min-width:230px">

          <h3>
            📍 ${p.nama}
          </h3>

          <hr/>

          <p>
            <b>🏷️ Jenis:</b>
            ${p.jenis}
          </p>

          <p>
            <b>📌 Alamat:</b>
            ${p.alamat || "-"}
          </p>

          <p>
            <b>🌐 Latitude:</b>
            ${lat}
          </p>

          <p>
            <b>🌐 Longitude:</b>
            ${lng}
          </p>

          <button
            id="edit-${p.id}"

            style="
              background:#2f6ea5;
              color:white;
              border:none;
              padding:8px;
              border-radius:8px;
              cursor:pointer;
              width:100%;
              margin-bottom:8px;
            "
          >
            Edit
          </button>

          <button
            id="delete-${p.id}"

            style="
              background:red;
              color:white;
              border:none;
              padding:8px;
              border-radius:8px;
              cursor:pointer;
              width:100%;
            "
          >
            Delete
          </button>

        </div>

      `);

              layer.on("popupopen", () => {
                const editBtn = document.getElementById(`edit-${p.id}`);

                if (editBtn) {
                  editBtn.onclick = () => {
                    setEditId(p.id);

                    setNama(p.nama);

                    setJenis(p.jenis);

                    setAlamat(p.alamat || "");

                    setLatitude(lat);

                    setLongitude(lng);

                    setShowForm(true);
                  };
                }

                const deleteBtn = document.getElementById(`delete-${p.id}`);

                if (deleteBtn) {
                  deleteBtn.onclick = () => {
                    handleDelete(p.id);
                  };
                }
              });
            }}
          />
        )}

        {detections && (
          <GeoJSON
            data={detections}
            pointToLayer={(feature, latlng) =>
              L.circleMarker(latlng, {
                radius: 10,
                fillColor: "#00d084",
                color: "#ffffff",
                weight: 2,
                fillOpacity: 0.9,
              })
            }
            onEachFeature={(feature, layer) => {
              layer.bindPopup(`

        <div style="min-width:240px">

          <h3>
            🤖 Spatial AI Detection
          </h3>

          <hr/>

          <p>
            <b>Detection ID:</b>
            ${feature.properties.detection_id}
          </p>

          <p>
            <b>Confidence:</b>
            ${(feature.properties.confidence * 100).toFixed(1)}%
          </p>

          <p>
            <b>Source:</b>
            ${feature.properties.source}
          </p>

          <p>
            <b>Type:</b>
            ${feature.properties.type}
          </p>

        </div>

      `);
            }}
          />
        )}
      </MapContainer>

      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editId ? "Edit Fasilitas" : "Tambah Fasilitas"}</h2>

            <input
              placeholder="Nama"
              value={nama}
              onChange={(e) => setNama(e.target.value)}
            />

            <input
              placeholder="Jenis"
              value={jenis}
              onChange={(e) => setJenis(e.target.value)}
            />

            <input
              placeholder="Alamat"
              value={alamat}
              onChange={(e) => setAlamat(e.target.value)}
            />

            <input
              placeholder="Latitude"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
            />

            <input
              placeholder="Longitude"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
            />

            <button onClick={editId ? handleEdit : handleAdd}>
              {editId ? "Update" : "Simpan"}
            </button>

            <button
              onClick={() => {
                setShowForm(false);

                resetForm();
              }}
            >
              Tutup
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default MapView;
