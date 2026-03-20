import zipfile
import os
import shutil

print("="*70)
print("EXTRACTING DOWNLOADED DATASET")
print("="*70)

# Find the downloaded zip file
downloads_dir = os.path.expanduser("~/Downloads")
print(f"\n🔍 Searching for dataset in: {downloads_dir}")

# Look for zip file
zip_files = []
for file in os.listdir(downloads_dir):
    if 'license-plate' in file.lower() and file.endswith('.zip'):
        zip_files.append(file)

if not zip_files:
    print("\n❌ No zip file found in Downloads folder!")
    print("\nPlease:")
    print("1. Download the dataset from Roboflow")
    print("2. Make sure the zip file is in your Downloads folder")
    print("3. Run this script again")
    exit(1)

if len(zip_files) > 1:
    print("\n📦 Found multiple zip files:")
    for i, f in enumerate(zip_files, 1):
        print(f"   {i}. {f}")
    
    choice = input("\nWhich one to extract? (1/2/...): ").strip()
    zip_file = zip_files[int(choice) - 1]
else:
    zip_file = zip_files[0]

zip_path = os.path.join(downloads_dir, zip_file)
print(f"\n✓ Found: {zip_file}")
print(f"📊 Size: {os.path.getsize(zip_path) / (1024*1024):.1f} MB")

# Extract
extract_dir = "License-Plate-Detection-1"

if os.path.exists(extract_dir):
    print(f"\n⚠️  {extract_dir} already exists")
    response = input("Delete and replace? (y/n): ")
    if response.lower() == 'y':
        shutil.rmtree(extract_dir)
        print("✓ Removed old dataset")
    else:
        print("Cancelled.")
        exit(0)

print(f"\n📦 Extracting to: {extract_dir}")
print("⏳ This may take 1-2 minutes...")

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    print("\n✅ Extraction complete!")
    
    # Verify structure
    print("\n🔍 Verifying dataset structure...")
    
    # The extracted folder might have a nested structure
    # Find the actual dataset folder
    dataset_root = extract_dir
    
    # Check if there's a nested folder
    items = os.listdir(extract_dir)
    if len(items) == 1 and os.path.isdir(os.path.join(extract_dir, items[0])):
        # Move contents up one level
        nested_folder = os.path.join(extract_dir, items[0])
        temp_dir = extract_dir + "_temp"
        
        shutil.move(nested_folder, temp_dir)
        shutil.rmtree(extract_dir)
        shutil.move(temp_dir, extract_dir)
        
        print("✓ Fixed nested folder structure")
    
    # Verify contents
    train_dir = os.path.join(extract_dir, 'train', 'images')
    valid_dir = os.path.join(extract_dir, 'valid', 'images')
    
    if not os.path.exists(train_dir):
        print(f"\n❌ Expected folder not found: {train_dir}")
        print("\nListing contents of extracted folder:")
        for root, dirs, files in os.walk(extract_dir):
            level = root.replace(extract_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            if level < 2:  # Only show first 2 levels
                subindent = ' ' * 2 * (level + 1)
                for file in files[:5]:  # Show first 5 files
                    print(f'{subindent}{file}')
        exit(1)
    
    train_count = len([f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
    valid_count = len([f for f in os.listdir(valid_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Training images:   {train_count}")
    print(f"   Validation images: {valid_count}")
    print(f"   Total images:      {train_count + valid_count}")
    
    # Check data.yaml
    yaml_path = os.path.join(extract_dir, 'data.yaml')
    if os.path.exists(yaml_path):
        print(f"\n✓ data.yaml found")
        
        # Fix paths in data.yaml
        import yaml
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        data['path'] = os.path.abspath(extract_dir)
        data['train'] = 'train/images'
        data['val'] = 'valid/images'
        
        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        print("✓ data.yaml paths configured")
    
    print("\n" + "="*70)
    print("✅ DATASET READY!")
    print("="*70)
    print(f"\n📁 Location: {os.path.abspath(extract_dir)}")
    print("\n🚀 Next step:")
    print("   python train_final.py")
    print("="*70)
    
except zipfile.BadZipFile:
    print("\n❌ Error: Downloaded file is corrupted")
    print("\nPlease:")
    print("1. Delete the zip file from Downloads")
    print("2. Re-download from Roboflow")
    print("3. Make sure download completes fully")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()