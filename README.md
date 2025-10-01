# 🖱️ Optical Mouse Computer Vision

A real-time computer vision implementation that mimics the working principles of an optical computer mouse. This project uses OpenCV and Python to track surface movement through a camera feed and translates it into cursor movement, demonstrating the core technology behind optical mice.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🎯 About the Project

This project recreates the fundamental motion detection principles used in optical computer mice using computer vision techniques. Instead of a specialized CMOS sensor, it uses a webcam or smartphone camera to capture surface images and track movement using optical flow algorithms.

**Key Highlights:**
- Real-time motion tracking using Lucas-Kanade optical flow
- Dual-window visualization showing camera feed and desktop cursor
- Support for webcam and smartphone cameras via IP connection
- Customizable sensitivity and smoothing parameters
- Movement-only implementation (no clicking functionality)

## ✨ Features

### Core Functionality
- **Optical Flow Tracking**: Lucas-Kanade pyramidal optical flow for precise motion detection
- **Color-Based Tracking**: Alternative method using HSV color space filtering
- **Dual Window Display**: Camera feed and desktop capture windows
- **Real-Time Performance Metrics**: FPS, latency, and tracking point visualization

### Advanced Features
- **Coordinate Transformation**: Maps camera space to screen space
- **Movement Smoothing**: Exponential moving average filtering
- **Configurable Sensitivity**: Adjustable cursor speed
- **Phone Camera Support**: Wireless operation via IP camera apps
- **Modular Architecture**: Clean 7-module structure

## 🛠️ Technologies Used

- **OpenCV** (4.8+) - Computer vision processing
- **NumPy** (1.24+) - Numerical computations
- **PyAutoGUI** (0.9.54+) - Cursor control
- **MSS** (9.0+) - Fast screen capture
- **PyYAML** (6.0+) - Configuration management

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam or smartphone with camera
- Operating System: Windows, macOS, or Linux

### Installation

1. **Extract the project**
