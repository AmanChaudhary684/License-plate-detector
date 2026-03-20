from ultralytics import YOLO
import os
import shutil

print("="*70)
print(" " * 15 + "LICENSE PLATE DETECTOR TRAINING")
print("="*70)

# Check if dataset exists
dataset_path = None
possible_paths = [
    'License-Plate-Detection-1',
    'license-plate-detection-n9ped-1',
    'License-Plate-Detection-1'
]

for path in possible_paths:
    if os.path.exists(path):
        dataset_path = path
        break

if not dataset_path:
    print("\n❌ ERROR: Dataset not found!")
    print("\nPlease download the dataset first using:")
    print("  python download_dataset.py")
    print("\nOr manually place your dataset folder in the backend directory")
    exit(1)

print(f"\n✓ Dataset found: {dataset_path}")

# Check for data.yaml
yaml_path = os.path.join(dataset_path, 'data.yaml')
if not os.path.exists(yaml_path):
    print(f"\n❌ ERROR: data.yaml not found in {dataset_path}")
    exit(1)

print(f"✓ Configuration file: {yaml_path}")

# Count images
train_images = os.path.join(dataset_path, 'train', 'images')
valid_images = os.path.join(dataset_path, 'valid', 'images')

if os.path.exists(train_images):
    train_count = len([f for f in os.listdir(train_images) if f.endswith(('.jpg', '.png'))])
    print(f"✓ Training images: {train_count}")

if os.path.exists(valid_images):
    valid_count = len([f for f in os.listdir(valid_images) if f.endswith(('.jpg', '.png'))])
    print(f"✓ Validation images: {valid_count}")

print("\n" + "="*70)
print("TRAINING CONFIGURATION")
print("="*70)
print("Model: YOLOv8 Nano (fastest, good accuracy)")
print("Epochs: 50 (with early stopping)")
print("Image Size: 640x640")
print("Batch Size: 8")
print("Device: CPU (change to 'cuda' if you have GPU)")
print("Estimated Time: 20-40 minutes on CPU, 5-10 minutes on GPU")
print("="*70)

# Ask for confirmation
response = input("\nStart training? (y/n): ")
if response.lower() != 'y':
    print("Training cancelled.")
    exit(0)

print("\n🚀 Starting training...\n")

# Load pretrained YOLOv8 nano model
print("Loading base YOLOv8 model...")
model = YOLO('yolov8n.pt')  # Will auto-download if not present

# Train the model
print("\nTraining in progress...")
print("You can monitor progress below:")
print("-"*70)

try:
    results = model.train(
        data=yaml_path,
        epochs=50,              # Number of training cycles
        imgsz=640,              # Image size
        batch=8,                # Batch size (reduce to 4 if out of memory)
        name='license_plate_detector',
        patience=10,            # Stop early if no improvement for 10 epochs
        save=True,              # Save checkpoints
        device='cpu',           # Change to 'cuda' if you have NVIDIA GPU
        verbose=True,           # Show detailed output
        project='runs/detect',  # Where to save results
        exist_ok=True,          # Overwrite existing project
        pretrained=True,        # Use pretrained weights
        optimizer='Adam',       # Optimizer
        lr0=0.01,              # Initial learning rate
        cos_lr=True,           # Use cosine learning rate scheduler
        plots=True,            # Generate training plots
        save_period=10,        # Save checkpoint every 10 epochs
    )
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    # Show results
    best_model_path = 'runs/detect/license_plate_detector/weights/best.pt'
    last_model_path = 'runs/detect/license_plate_detector/weights/last.pt'
    
    print(f"\n📊 Results:")
    print(f"   Best model: {best_model_path}")
    print(f"   Last model: {last_model_path}")
    print(f"   Training plots: runs/detect/license_plate_detector/")
    
    # Copy best model to main folder
    print("\n📦 Copying best model to main folder...")
    if os.path.exists(best_model_path):
        shutil.copy(best_model_path, 'license_plate_best.pt')
        print("✓ Model saved as: license_plate_best.pt")
    
    print("\n" + "="*70)
    print("🎉 ALL DONE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart your Flask server: python app.py")
    print("2. The new model will be loaded automatically")
    print("3. Test with your images - you should see better detection!")
    
    print("\n💡 Tips:")
    print("   - Check training plots in: runs/detect/license_plate_detector/")
    print("   - If accuracy is low, try training for more epochs")
    print("   - Add more training images for better results")
    
except KeyboardInterrupt:
    print("\n\n⚠️  Training interrupted by user")
    print("Partial results saved in: runs/detect/license_plate_detector/")
    
except Exception as e:
    print(f"\n\n❌ ERROR during training: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("1. Check if data.yaml path is correct")
    print("2. Verify images are in the correct folders")
    print("3. Try reducing batch size to 4 if out of memory")