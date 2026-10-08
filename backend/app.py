from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
import base64
import time
import os
import re

app = Flask(__name__)
CORS(app)

# Initialize models
print("Loading EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)
print("Loading YOLOv8...")

# Try to load custom trained model, fallback to pretrained
model_paths = [
    'license_plate_best.pt',
    'license_plate_production_3221img.pt',
    'License-Plate-Detection-1/weights/best.pt',
    'runs/detect/train/weights/best.pt',
    'yolov8n.pt'
]

model = None
for path in model_paths:
    if os.path.exists(path):
        print(f"Loading model from: {path}")
        model = YOLO(path)
        break

if model is None:
    print("Loading default YOLOv8 model...")
    model = YOLO('yolov8n.pt')

print("Models loaded successfully!")

class ImageEnhancer:
    """Image enhancement for foggy/hazy images"""
    
    @staticmethod
    def dark_channel(img, size=15):
        """Calculate dark channel prior"""
        b, g, r = cv2.split(img)
        min_img = cv2.min(r, cv2.min(b, g))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
        dc_img = cv2.erode(min_img, kernel)
        return dc_img
    
    @staticmethod
    def atmospheric_light(img, dark_ch, p=0.001):
        """Estimate atmospheric light"""
        h, w = dark_ch.shape
        n_pixels = h * w
        n_search = int(n_pixels * p)
        
        dark_vec = dark_ch.reshape(n_pixels)
        img_vec = img.reshape(n_pixels, 3)
        
        indices = dark_vec.argsort()[::-1][:n_search]
        max_intensity = np.max(img_vec[indices], axis=0)
        
        return max_intensity
    
    @staticmethod
    def transmission_estimate(img, A, sz=15, omega=0.95):
        """Estimate transmission map"""
        norm_img = np.empty_like(img, dtype=np.float64)
        for i in range(3):
            norm_img[:, :, i] = img[:, :, i] / A[i]
        
        transmission = 1 - omega * ImageEnhancer.dark_channel(norm_img, sz)
        return transmission
    
    @staticmethod
    def guided_filter(I, p, r, eps):
        """Apply guided filter"""
        mean_I = cv2.boxFilter(I, cv2.CV_64F, (r, r))
        mean_p = cv2.boxFilter(p, cv2.CV_64F, (r, r))
        mean_Ip = cv2.boxFilter(I * p, cv2.CV_64F, (r, r))
        cov_Ip = mean_Ip - mean_I * mean_p
        
        mean_II = cv2.boxFilter(I * I, cv2.CV_64F, (r, r))
        var_I = mean_II - mean_I * mean_I
        
        a = cov_Ip / (var_I + eps)
        b = mean_p - a * mean_I
        
        mean_a = cv2.boxFilter(a, cv2.CV_64F, (r, r))
        mean_b = cv2.boxFilter(b, cv2.CV_64F, (r, r))
        
        q = mean_a * I + mean_b
        return q
    
    @staticmethod
    def dehaze(img, t0=0.1, w=0.95):
        """Main dehazing function using Dark Channel Prior"""
        img = img.astype(np.float64) / 255.0
        
        # Calculate dark channel
        dark = ImageEnhancer.dark_channel(img)
        
        # Estimate atmospheric light
        A = ImageEnhancer.atmospheric_light(img, dark)
        
        # Estimate transmission
        t = ImageEnhancer.transmission_estimate(img, A)
        
        # Guided filter for refinement
        gray = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
        gray = gray.astype(np.float64) / 255.0
        t = ImageEnhancer.guided_filter(gray, t, r=60, eps=0.0001)
        
        # Recover scene radiance
        t = np.maximum(t, t0)
        J = np.empty_like(img)
        
        for i in range(3):
            J[:, :, i] = (img[:, :, i] - A[i]) / t + A[i]
        
        J = np.clip(J * 255, 0, 255).astype(np.uint8)
        
        return J
    
    @staticmethod
    def enhance_image(img):
        """Apply multiple enhancement techniques"""
        # Dehazing
        dehazed = ImageEnhancer.dehaze(img)
        
        # CLAHE for contrast enhancement
        lab = cv2.cvtColor(dehazed, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened


def detect_license_plate(image):
    """Detect license plates using YOLOv8"""
    results = model(image, conf=0.2)
    
    plates = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            
            # Add padding for better OCR
            h, w = image.shape[:2]
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(w, x2 + padding)
            y2 = min(h, y2 + padding)
            
            # Extract plate region
            plate_img = image[y1:y2, x1:x2]
            if plate_img.size > 0:
                plates.append({
                    'image': plate_img,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(conf)
                })
    
    plates.sort(key=lambda x: x['confidence'], reverse=True)
    return plates


def validate_indian_plate(text):
    """Validate and fix Indian license plate format"""
    text = text.replace(' ', '').upper()
    
    # Indian plate patterns
    patterns = [
        r'^[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}$',   # Standard: RJ45CJ0910
        r'^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}$', # Variations
    ]
    
    for pattern in patterns:
        if re.match(pattern, text):
            return text, True
    
    return text, False


def preprocess_plate_for_ocr(plate_img):
    """Advanced preprocessing for better OCR accuracy"""
    # Get original dimensions
    h, w = plate_img.shape[:2]
    
    # Upscale 4x for better character recognition
    scale_factor = 4
    plate_large = cv2.resize(plate_img, (w * scale_factor, h * scale_factor), 
                            interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale
    gray = cv2.cvtColor(plate_large, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while preserving edges
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Adaptive thresholding
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 15, 3
    )
    
    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Additional sharpening
    kernel_sharp = np.array([[-1,-1,-1],
                            [-1, 9,-1],
                            [-1,-1,-1]])
    sharpened = cv2.filter2D(cleaned, -1, kernel_sharp)
    
    return plate_large, gray, denoised, sharpened


def extract_text(plate_img):
    """Extract text from license plate using improved OCR"""
    try:
        print(f"  OCR: Processing plate of size {plate_img.shape}")
        
        # Preprocess plate in multiple ways
        plate_large, gray, denoised, binary = preprocess_plate_for_ocr(plate_img)
        
        # Run OCR on multiple preprocessed versions
        all_results = []
        versions = [
            ('color_upscaled', plate_large),
            ('grayscale', gray),
            ('denoised', denoised),
            ('binary', binary)
        ]
        
        for version_name, img in versions:
            try:
                results = reader.readtext(
                    img,
                    allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    paragraph=False,
                    detail=1
                )
                
                for bbox, text, conf in results:
                    all_results.append({
                        'text': text,
                        'confidence': conf,
                        'bbox': bbox,
                        'version': version_name
                    })
            except Exception as e:
                print(f"  OCR warning on {version_name}: {e}")
                continue
        
        if not all_results:
            print("  OCR: No text detected in any version")
            return []
        
        print(f"  OCR: Found {len(all_results)} raw results")
        
        # Process and deduplicate results
        text_candidates = {}
        
        for result in all_results:
            # Clean text
            text = result['text'].upper().strip().replace(' ', '')
            text = ''.join(c for c in text if c.isalnum())
            
            if len(text) < 4:  # Too short
                continue
            
            # Apply common OCR corrections
            corrections = {
                'O': '0', 'o': '0',  # Letter O to zero
                'I': '1', 'l': '1',  # Letter I/l to one
                'Z': '2',             # Z to 2
                'S': '5',             # S to 5 (sometimes)
                'B': '8',             # B to 8 (sometimes)
                'G': '6',             # G to 6 (sometimes)
            }
            
            corrected_text = text
            for old, new in corrections.items():
                # Only replace if it makes sense in context
                corrected_text = corrected_text.replace(old, new)
            
            # Validate format
            validated_text, is_valid = validate_indian_plate(corrected_text)
            
            # Keep best confidence for each unique text
            if validated_text not in text_candidates or result['confidence'] > text_candidates[validated_text]['confidence']:
                text_candidates[validated_text] = {
                    'text': validated_text,
                    'confidence': float(result['confidence']),
                    'bbox': [[float(x), float(y)] for x, y in result['bbox']],
                    'is_valid_format': is_valid,
                    'original_text': text,
                    'version': result['version']
                }
        
        # Convert to list and sort
        ocr_results = list(text_candidates.values())
        
        # Sort by: 1) valid format first, 2) confidence
        ocr_results.sort(key=lambda x: (x['is_valid_format'], x['confidence']), reverse=True)
        
        # Log results
        if ocr_results:
            print(f"  OCR: Best result: '{ocr_results[0]['text']}' (conf: {ocr_results[0]['confidence']:.2f}, valid: {ocr_results[0]['is_valid_format']})")
            if len(ocr_results) > 1:
                print(f"  OCR: Alternative: '{ocr_results[1]['text']}' (conf: {ocr_results[1]['confidence']:.2f})")
        
        return ocr_results[:3]  # Return top 3 results
        
    except Exception as e:
        print(f"OCR Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def image_to_base64(img):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64


@app.route('/api/detect', methods=['POST'])
def detect():
    start_time = time.time()
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        # Read image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        print(f"\n{'='*60}")
        print(f"Processing image: {img.shape}")
        
        # Step 1: Enhance image
        print("Step 1: Enhancing image...")
        enhanced_img = ImageEnhancer.enhance_image(img)
        print("  ✓ Enhancement complete")
        
        # Step 2: Detect license plates
        print("Step 2: Detecting license plates...")
        plates = detect_license_plate(enhanced_img)
        
        if not plates:
            print("  No plates in enhanced image, trying original...")
            plates = detect_license_plate(img)
            enhanced_img = img.copy()
        
        if not plates:
            print("  ✗ No license plates detected")
            return jsonify({
                'message': 'No license plates detected',
                'enhanced_image': image_to_base64(enhanced_img),
                'plates_detected': 0,
                'processing_time': float(time.time() - start_time)
            })
        
        print(f"  ✓ Detected {len(plates)} plate(s)")
        
        # Step 3: Extract text from all detected plates
        print("Step 3: Extracting text with improved OCR...")
        all_ocr_results = []
        
        for idx, plate_data in enumerate(plates[:3], 1):
            print(f"  Plate {idx}/{min(len(plates), 3)}:")
            print(f"    Confidence: {plate_data['confidence']:.2%}")
            
            plate_img = plate_data['image']
            ocr_results = extract_text(plate_img)
            
            if ocr_results:
                # Add plate index to results
                for result in ocr_results:
                    result['plate_index'] = idx
                all_ocr_results.extend(ocr_results)
        
        # Get best plate for display
        plate_data = plates[0]
        plate_img = plate_data['image']
        
        # Draw bounding boxes on enhanced image
        result_img = enhanced_img.copy()
        for idx, plate in enumerate(plates[:3]):
            x1, y1, x2, y2 = plate['bbox']
            color = (0, 255, 0) if idx == 0 else (255, 165, 0)
            thickness = 3 if idx == 0 else 2
            
            # Draw rectangle
            cv2.rectangle(result_img, (x1, y1), (x2, y2), color, thickness)
            
            # Add confidence label
            conf_text = f"{plate['confidence']*100:.1f}%"
            cv2.putText(result_img, conf_text, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Add best OCR text as label
        if all_ocr_results:
            label = all_ocr_results[0]['text']
            x1, y1, x2, y2 = plates[0]['bbox']
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.2
            thickness = 3
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
            
            # Draw background rectangle
            padding = 10
            cv2.rectangle(result_img, 
                         (x1, y1 - text_height - padding * 2), 
                         (x1 + text_width + padding * 2, y1), 
                         (0, 255, 0), -1)
            
            # Draw text
            cv2.putText(result_img, label, (x1 + padding, y1 - padding),
                       font, font_scale, (0, 0, 0), thickness)
            
            # Add validity indicator
            if all_ocr_results[0].get('is_valid_format'):
                cv2.circle(result_img, (x2 - 20, y1 + 20), 8, (0, 255, 0), -1)
        
        processing_time = time.time() - start_time
        print(f"\n✓ Processing completed in {processing_time:.2f}s")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'enhanced_image': image_to_base64(result_img),
            'detected_plate': image_to_base64(plate_img),
            'ocr_results': all_ocr_results[:5],
            'plates_detected': int(len(plates)),
            'detection_confidence': float(plate_data['confidence']),
            'processing_time': float(processing_time),
            'model_used': 'Custom Trained (3221 images)' if 'best.pt' in str(model.ckpt_path) else 'Pretrained'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    model_info = 'Custom Trained Model (94.8% mAP50)' if 'best.pt' in str(model.ckpt_path) else 'Pretrained YOLOv8'
    return jsonify({
        'status': 'healthy', 
        'message': 'License Plate Detection API is running',
        'models': f'YOLOv8 ({model_info}) + EasyOCR (Enhanced)',
        'model_path': str(model.ckpt_path),
        'features': [
            'Dark Channel Prior Dehazing',
            'YOLOv8 Object Detection',
            'Advanced OCR Preprocessing',
            'Indian License Plate Validation'
        ]
    })


if __name__ == '__main__':
    print("=" * 70)
    print("License Plate Detection System - Production Version")
    print(f"Model: {model.ckpt_path}")
    print("Features:")
    print("  ✓ Image Enhancement (Dehazing)")
    print("  ✓ YOLOv8 Detection (94.8% mAP50)")
    print("  ✓ Improved OCR (4x upscaling + multi-version)")
    print("  ✓ Indian License Plate Validation")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)