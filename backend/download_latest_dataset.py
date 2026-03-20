from roboflow import Roboflow
import os
import shutil

print("="*70)
print("DOWNLOADING LATEST DATASET (1273 IMAGES)")
print("="*70)

# Get your API key from Roboflow
# Go to: https://app.roboflow.com → Settings → Roboflow API
api_key = input("\nEnter your Roboflow API key: ").strip()

if not api_key:
    print("❌ API key required!")
    print("\nGet it from: https://app.roboflow.com")
    print("Settings → Roboflow API → Copy Private API Key")
    exit(1)

print("\n🔐 API key received")

# Initialize Roboflow
rf = Roboflow(api_key=api_key)

# Your project
print("\n📦 Accessing your project...")
project = rf.workspace("aman-chaudhary").project("license-plate-detection-n9ped")

# List available versions
print("\n📋 Available dataset versions:")
print("-" * 70)

try:
    # Get all versions
    versions_list = []
    version_num = 1
    
    while True:
        try:
            version = project.version(version_num)
            # Try to access version info to see if it exists
            version_info = version.model
            versions_list.append(version_num)
            print(f"   Version {version_num}: Available")
            version_num += 1
        except:
            break
    
    if not versions_list:
        print("   No versions found!")
        exit(1)
    
    print("-" * 70)
    print(f"\nFound {len(versions_list)} version(s)")
    
    # Get the latest version (should have 1273 images)
    latest_version = max(versions_list)
    print(f"\n💡 Latest version: {latest_version}")
    
    # Ask which version to download
    selected_version = input(f"\nWhich version to download? (Press Enter for latest [{latest_version}]): ").strip()
    
    if not selected_version:
        selected_version = latest_version
    else:
        selected_version = int(selected_version)
    
    if selected_version not in versions_list:
        print(f"❌ Version {selected_version} not found!")
        exit(1)
    
    print(f"\n📥 Downloading version {selected_version}...")
    print("⏳ This may take 2-5 minutes depending on your internet speed...")
    
    # Download dataset
    dataset = project.version(selected_version).download("yolov8")
    
    print(f"\n✅ Download complete!")
    print(f"📁 Location: {dataset.location}")
    
    # Verify the download
    print("\n🔍 Verifying dataset...")
    
    train_dir = os.path.join(dataset.location, 'train', 'images')
    valid_dir = os.path.join(dataset.location, 'valid', 'images')
    test_dir = os.path.join(dataset.location, 'test', 'images')
    
    train_count = 0
    valid_count = 0
    test_count = 0
    
    if os.path.exists(train_dir):
        train_count = len([f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        print(f"   ✓ Training images: {train_count}")
    
    if os.path.exists(valid_dir):
        valid_count = len([f for f in os.listdir(valid_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        print(f"   ✓ Validation images: {valid_count}")
    
    if os.path.exists(test_dir):
        test_count = len([f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        print(f"   ✓ Test images: {test_count}")
    
    total = train_count + valid_count + test_count
    print(f"\n   📊 TOTAL: {total} images")
    
    if total < 1000:
        print(f"\n⚠️  Warning: Expected ~1273 images, but got {total}")
        print("   Make sure you selected the right version with augmented data")
    elif total >= 1200:
        print(f"\n🎉 Perfect! Dataset has {total} images")
    
    # Check data.yaml
    yaml_file = os.path.join(dataset.location, 'data.yaml')
    if os.path.exists(yaml_file):
        print(f"   ✓ data.yaml found")
        
        # Read and display
        with open(yaml_file, 'r') as f:
            print("\n📄 data.yaml contents:")
            print("-" * 70)
            print(f.read())
            print("-" * 70)
    
    # Backup old dataset if exists
    old_dataset = 'License-Plate-Detection-1'
    if os.path.exists(old_dataset):
        backup_name = 'License-Plate-Detection-1-backup-300img'
        if not os.path.exists(backup_name):
            print(f"\n💾 Backing up old dataset...")
            shutil.move(old_dataset, backup_name)
            print(f"   ✓ Old dataset moved to: {backup_name}")
    
    # Rename new dataset to standard name
    new_name = 'License-Plate-Detection-1'
    if dataset.location != new_name:
        if os.path.exists(new_name):
            shutil.rmtree(new_name)
        shutil.move(dataset.location, new_name)
        print(f"\n✓ Dataset renamed to: {new_name}")
    
    print("\n" + "="*70)
    print("✅ DATASET READY FOR TRAINING!")
    print("="*70)
    print("\n📋 Next steps:")
    print("   1. Review dataset in: License-Plate-Detection-1/")
    print("   2. Run training: python train_final.py")
    print("   3. Wait 10-12 hours for training to complete")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check your API key is correct")
    print("2. Make sure you have internet connection")
    print("3. Verify the project exists in your Roboflow account")
    print("4. Check if version has been generated")
    import traceback
    traceback.print_exc()