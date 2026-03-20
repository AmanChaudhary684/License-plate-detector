from ultralytics import YOLO
import os
import shutil

print("="*70)
print("FINAL PRODUCTION MODEL - 1273 IMAGES")
print("="*70)

# Verify dataset
train_imgs = 'License-Plate-Detection-1/train/images'
valid_imgs = 'License-Plate-Detection-1/valid/images'

train_count = len([f for f in os.listdir(train_imgs) if f.endswith(('.jpg', '.png'))])
valid_count = len([f for f in os.listdir(valid_imgs) if f.endswith(('.jpg', '.png'))])

print(f"\nDataset verified:")
print(f"  Training: {train_count} images")
print(f"  Validation: {valid_count} images")
print(f"  Total: {train_count + valid_count} images")

input("\nPress Enter to start training (10-12 hours)...")

# Load and train
model = YOLO('yolov8n.pt')

results = model.train(
    data='License-Plate-Detection-1/data.yaml',
    epochs=150,
    batch=16,
    imgsz=640,
    patience=35,
    name='final_production',
    device='cpu',  # Change to 'cuda' for GPU
    optimizer='AdamW',
    lr0=0.01,
    cos_lr=True,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=10,
    translate=0.1,
    scale=0.5,
    flipud=0.0,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.1,
    plots=True,
    save_period=15,
    verbose=True,
)

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)

# Validate
best_model = YOLO('runs/detect/final_production/weights/best.pt')
val_results = best_model.val()

precision = val_results.results_dict['metrics/precision(B)']
recall = val_results.results_dict['metrics/recall(B)']
map50 = val_results.results_dict['metrics/mAP50(B)']
map50_95 = val_results.results_dict['metrics/mAP50-95(B)']

print(f"\n🎯 FINAL METRICS:")
print(f"   Precision:  {precision:.1%}")
print(f"   Recall:     {recall:.1%}")
print(f"   mAP50:      {map50:.1%}")
print(f"   mAP50-95:   {map50_95:.1%}")

# Save production model
shutil.copy('runs/detect/final_production/weights/best.pt', 'license_plate_production_1273.pt')
shutil.copy('runs/detect/final_production/weights/best.pt', 'license_plate_best.pt')

print("\n✓ Production model saved as: license_plate_production_1273.pt")
print("✓ Active model updated: license_plate_best.pt")
print("\n🎉 Ready for deployment!")