# 🚘 License Plate Recognition API (Germany)

This FastAPI project detects and extracts German license plate numbers from uploaded vehicle images using OCR (EasyOCR). It's designed for integration into parking systems, traffic monitoring, or vehicle access control.

---

## ⚙️ Features

- 📷 Upload image files of vehicles (JPG, PNG, etc.)
- 🔍 Extracts text using [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- 🇩🇪 Supports German license plate formats (e.g. "H-AB1234")
- 🧠 Handles OCR noise and joins separate text segments intelligently
- 🛡️ Validates image types and size (max 10MB)

---

## 🧰 Tech Stack

- **FastAPI** – Web framework for building the REST API
- **EasyOCR** – Optical Character Recognition engine
- **Pillow (PIL)** – Image handling
- **Regex** – Pattern matching for license plates
- **Uvicorn** – ASGI server for running the app

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/license-plate-recognition.git
cd license-plate-recognition
