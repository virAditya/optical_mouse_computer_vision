# 🖱️ Optical Mouse Computer Vision

A real-time computer vision implementation that mimics the working principles of an optical computer mouse. This project uses OpenCV and Python to track surface movement through a camera feed and translates it into cursor movement, demonstrating the core technology behind optical mice.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Demo](#demo)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Phone Camera Setup](#phone-camera-setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

## 🎯 About the Project

This project recreates the fundamental motion detection principles used in optical computer mice using computer vision techniques. Instead of a specialized CMOS sensor, it uses a webcam or smartphone camera to capture surface images and track movement using optical flow algorithms or color-based tracking.

**Key Highlights:**
- Real-time motion tracking using Lucas-Kanade optical flow
- Dual-window visualization showing both camera feed and desktop cursor
- Support for both webcam and smartphone cameras via IP connection
- Customizable sensitivity and smoothing parameters
- Movement-only implementation (no clicking functionality)

## ✨ Features

### Core Functionality
- **Optical Flow Tracking**: Uses Lucas-Kanade pyramidal optical flow for precise motion detection
- **Color-Based Tracking**: Alternative tracking method using HSV color space filtering
- **Dual Window Display**: 
  - Camera feed window with tracking overlays
  - Desktop capture window with cursor highlighting
- **Real-Time Performance Metrics**: FPS, latency, and tracking point visualization

### Advanced Features
- **Coordinate Transformation**: Maps camera space to screen space with calibration
- **Movement Smoothing**: Exponential moving average and Kalman filtering options
- **Configurable Sensitivity**: Adjustable cursor speed and movement parameters
- **Phone Camera Support**: Connect via IP camera apps for wireless operation
- **Modular Architecture**: Clean, maintainable code structure with 7 modules

## 🎥 Demo

The system displays two side-by-side windows:

**Left Window (Camera Feed):**
- Shows tracked feature points (green circles for successful tracking)
- Displays motion trails and tracking overlays
- Real-time FPS and performance metrics

**Right Window (Desktop View):**
- Captures screen region with cursor movement
- Highlights cursor position with crosshairs and circles
- Visual feedback of tracking results

## 🛠️ Technologies Used

### Core Libraries
- **OpenCV** (4.8+) - Computer vision processing
- **NumPy** (1.24+) - Numerical computations
- **PyAutoGUI** (0.9.54+) - Cursor control
- **MSS** (9.0+) - Fast screen capture
- **PyYAML** (6.0+) - Configuration management

### Algorithms
- **Lucas-Kanade Optical Flow** - Motion vector calculation
- **Shi-Tomasi Corner Detection** - Feature point detection
- **HSV Color Filtering** - Color-based object tracking
- **Exponential Moving Average** - Movement smoothing

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam or smartphone with camera
- Operating System: Windows, macOS, or Linux

### Installation

1. **Clone the repository**
