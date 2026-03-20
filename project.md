# License Plate Detection System - PRODUCTION READY

## 🎯 Project Overview
AI-powered license plate detection system with fog removal, real-time detection, and OCR.

## 📊 Final Performance
- **Dataset**: 1,273 images
- **Precision**: 95%+
- **Recall**: 90%+
- **mAP50**: 94%+

## 🏗️ Architecture
```
┌─────────────┐
│   Frontend  │ React (http://localhost:3000)
│   (React)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │ Flask (http://localhost:5000)
│   (Flask)   │
└──────┬──────┘
       │
       ├──► Image Enhancement (OpenCV)
       │    └─ Dark Channel Prior Dehazing
       │
       ├──► Object Detection (YOLOv8)
       │    └─ Custom trained on 1273 images
       │
       └──► OCR (EasyOCR)
            └─ Text extraction with confidence
```

## 🚀 Quick Start

##Before##
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
## After##
# Just double-click start.bat
# Everything starts automatically
# Browser opens automatically
# One command to stop everything

### Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api/health

## 📁 Key Files
- `license_plate_best.pt` - Production model (1273 images)
- `app.py` - Flask backend server
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
November 2025          //can be changed as per requirements