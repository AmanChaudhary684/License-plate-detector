# License Plate Detection System - PRODUCTION READY

## 🌐 Live Demo

**[🚗 Open the Functional License Plate Detector](https://license-plate-detector-frontend.onrender.com)**

The frontend is hosted on Render and connected to the live Flask/YOLOv8/EasyOCR backend.

**Backend API:** https://license-plate-detector-api.onrender.com

## 🎯 Project Overview
AI-powered license plate detection system with fog removal, real-time detection, and OCR.

## 📊 Final Performance
- **Dataset**: 1,273 images
- **Precision**: 95%+
- **Recall**: 90%+
- **mAP50**: 94%+

## 🏗️ Architecture
```
┌──────────────────────┐
│   Render Frontend    │
│       React          │
└──────────┬───────────┘
           │ HTTPS
           ▼
┌──────────────────────┐
│    Render Backend    │
│ Flask + YOLOv8 + OCR │
└──────────────────────┘
```

## 🚀 Quick Start

### Start Backend
```bash
cd backend
python app.py
```

### Start Frontend
```bash
cd frontend
npm start
```

### Local Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api/health

## 📁 Key Files
- `backend/license_plate_best.pt` - Production model
- `backend/app.py` - Flask backend server
- `frontend/src/App.js` - React frontend

## 🎓 Training History
1. **v1**: 300 images (mAP: 89.6%)
2. **v2**: 630 images (mAP: 89.8%)
3. **v3**: 1273 images (mAP: 94%+) ✅ PRODUCTION

## 🔧 Technologies
- **Backend**: Flask, OpenCV, YOLOv8, EasyOCR
- **Frontend**: React, Lucide Icons
- **ML**: PyTorch, Ultralytics
- **Training**: Roboflow

## 📈 Future Enhancements
- [ ] Video processing
- [ ] Batch upload
- [ ] Database integration
- [ ] Multi-language OCR
- [ ] Mobile app

## 👨‍💻 Developer
Aman Chaudhary, Parth Rawat, Atul Chauhan

## 📅 Completion Date
November 2025
