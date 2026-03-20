from ultralytics import YOLO
import os
import shutil

print("="*70)
print("    CONTINUING TRAINING - 50 ADDITIONAL EPOCHS")
print("="*70)

print("\nCurrent Model Performance:")
print("  ✓ Precision: 92.7%")
print("  ✓ Recall: 82.6%")
print("  ✓ mAP50: 89.6%")
print("  ✓ mAP50-95: 54.0%")

print("\nTraining Configuration:")
print("  - Starting from: license_plate_best.pt")
print("  - Additional epochs: 50")
print("  - Lower learning rate for fine-tuning")
print("  - Estimated time: 5-7 hours on CPU")
print("="*70)

response = input("\nStart training? (y/n): ")
if response.lower() != 'y':
    print("Training cancelled.")
    exit(0)

print("\n🚀 Loading previous best model and continuing training...\n")

# Load the best model from previous training
model = YOLO('license_plate_best.pt')

print("Starting fine-tuning training...")
print("="*70)

try:
    # Continue training with fine-tuning parameters
    results = model.train(
        data='License-Plate-Detection-1/data.yaml',
        epochs=50,              # 50 more epochs
        imgsz=640,
        batch=8,
        name='license_plate_detector_continued',
        patience=20,            # Increased patience for fine-tuning
        save=True,
        device='cpu',           # Change to 'cuda' if you have GPU
        verbose=True,
        project='runs/detect',
        exist_ok=True,
        
        # Fine-tuning parameters
        optimizer='Adam',
        lr0=0.0005,            # Lower learning rate (was 0.01)
        lrf=0.001,             # Lower final learning rate
        momentum=0.95,
        weight_decay=0.001,
        warmup_epochs=5,       # Longer warmup
        cos_lr=True,           # Cosine learning rate scheduler
        
        # Enhanced augmentation for better generalization
        hsv_h=0.02,            # Slight hue variation
        hsv_s=0.8,             # Saturation
        hsv_v=0.5,             # Brightness
        degrees=10,            # Rotation
        translate=0.15,        # Translation
        scale=0.6,             # Scaling
        shear=3,               # Shearing
        flipud=0.0,            # No vertical flip (plates are horizontal)
        fliplr=0.5,            # Horizontal flip
        mosaic=1.0,            # Mosaic augmentation
        mixup=0.15,            # Mixup augmentation
        
        plots=True,
        save_period=10,        # Save checkpoint every 10 epochs
    )
    
    print("\n" + "="*70)
    print("✅ CONTINUED TRAINING COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    # Paths
    best_model_path = 'runs/detect/license_plate_detector_continued/weights/best.pt'
    results_dir = 'runs/detect/license_plate_detector_continued'
    
    print(f"\n📊 Training Results:")
    print(f"   Results directory: {results_dir}")
    print(f"   Best model: {best_model_path}")
    
    # Validate the model
    print("\n📈 Validating improved model...")
    val_results = model.val()
    
    print(f"\n🎯 Final Performance Metrics:")
    print(f"   Precision: {val_results.results_dict['metrics/precision(B)']:.3f}")
    print(f"   Recall: {val_results.results_dict['metrics/recall(B)']:.3f}")
    print(f"   mAP50: {val_results.results_dict['metrics/mAP50(B)']:.3f}")
    print(f"   mAP50-95: {val_results.results_dict['metrics/mAP50-95(B)']:.3f}")
    
    # Compare with original
    print(f"\n📊 Improvement:")
    orig_map50 = 0.896
    new_map50 = val_results.results_dict['metrics/mAP50(B)']
    improvement = ((new_map50 - orig_map50) / orig_map50) * 100
    
    if improvement > 0:
        print(f"   ✅ mAP50 improved by {improvement:.1f}%!")
    else:
        print(f"   ⚠️  mAP50 changed by {improvement:.1f}%")
        print(f"   Original model might be better for this dataset")
    
    # Copy best model
    print("\n📦 Saving improved model...")
    if os.path.exists(best_model_path):
        # Backup old model
        if os.path.exists('license_plate_best.pt'):
            shutil.copy('license_plate_best.pt', 'license_plate_best_backup.pt')
            print("   ✓ Old model backed up as: license_plate_best_backup.pt")
        
        # Save new model
        shutil.copy(best_model_path, 'license_plate_best_v2.pt')
        print("   ✓ New model saved as: license_plate_best_v2.pt")
        
        # Optionally replace the main model
        response = input("\n   Replace license_plate_best.pt with new model? (y/n): ")
        if response.lower() == 'y':
            shutil.copy(best_model_path, 'license_plate_best.pt')
            print("   ✓ Main model updated: license_plate_best.pt")
    
    print("\n" + "="*70)
    print("🎉 ALL DONE!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Review training plots in:")
    print(f"      {results_dir}/")
    print("   2. Compare results_v2.png with original results.png")
    print("   3. Restart Flask: python app.py")
    print("   4. Test with real images")
    
    print("\n💡 Tips:")
    print("   - Check confusion_matrix.png to see where model struggles")
    print("   - Review F1_curve.png for optimal confidence threshold")
    print("   - If results are worse, use license_plate_best_backup.pt")
    
except KeyboardInterrupt:
    print("\n\n⚠️  Training interrupted by user")
    print("Partial results saved in: runs/detect/license_plate_detector_continued/")
    
except Exception as e:
    print(f"\n\n❌ ERROR during training: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)