# Pdom

> **Privacy Detection On-device Model (PDOM)**  
> An open-source, on-device AI privacy assistant that detects sensitive objects, faces, text, and QR codes in real time using computer vision.

---

## Problem Statement

Many AI-powered vision applications process camera data in the cloud, creating privacy concerns and requiring an internet connection.

Users need a lightweight solution that can detect sensitive information while keeping all processing local to their device.

---

## Solution Overview

Pdom is a desktop application that performs real-time privacy analysis using on-device AI.

It combines object detection, face detection, OCR, and QR code detection to identify privacy-sensitive information from a live webcam feed.

All processing happens locally without sending images or videos to external servers.

---

## On-Device AI

Pdom performs AI inference entirely on the user's computer.

Benefits include:

- Offline functionality
- Low latency
- Better privacy
- No cloud dependency
- Faster processing

---

## Features

### Current

- Live webcam feed
- YOLO object detection
- MediaPipe face detection
- Face blurring
- Desktop dashboard
- SQLite logging

### Planned

- OCR text detection
- QR code detection
- Privacy alerts
- Detection history
- Configurable privacy rules

---

## Tech Stack

- Python 3.11
- OpenCV
- Ultralytics YOLOv8
- Google MediaPipe
- EasyOCR
- PySide6
- SQLite
- NumPy
- Git & GitHub

---

## Project Structure

```
Pdom/

├── assets/
├── database/
├── docs/
├── logs/
├── models/
├── ocr/
├── ui/
├── utils/
├── vision/
│
├── config.py
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/padmanabhparanjape-ops/OMPD.git
```

### Enter the project directory

```bash
cd OMPD
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

#### Windows

```bash
.\.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

```bash
python main.py
```

---

## Workflow

```
Webcam
   │
   ▼
YOLO Object Detection
   │
   ▼
MediaPipe Face Detection
   │
   ▼
Face Blur
   │
   ▼
OCR
   │
   ▼
QR Detection
   │
   ▼
SQLite Logging
   │
   ▼
Dashboard
```

---

## Team Responsibilities

### AI Lead

- YOLO
- MediaPipe
- OCR
- OpenCV
- Camera Pipeline

### Project Lead

- PySide6 UI
- SQLite Database
- Integration
- GitHub
- Documentation
- Packaging

---

## Demo

Demo video will be added before the final submission.

---

## Screenshots

Screenshots will be added as development progresses.

---

## Current Status

| Module | Status |
|---------|--------|
| Repository | ✅ |
| Environment | ✅ |
| YOLO | 🚧 |
| MediaPipe | 🚧 |
| Dashboard | 🚧 |
| SQLite | 🚧 |
| OCR | ⏳ |
| QR Detection | ⏳ |

---

## Future Scope

- Custom-trained privacy detection model
- Multi-camera support
- Cross-platform desktop application
- Advanced privacy analytics
- User-defined privacy rules

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- Ultralytics
- Google MediaPipe
- OpenCV
- EasyOCR
- Qt / PySide6
- Python Software Foundation

---

**Pdom** is being developed as an open-source project for **OSDHack 2026**, with a focus on demonstrating practical, privacy-first AI that runs entirely on-device.