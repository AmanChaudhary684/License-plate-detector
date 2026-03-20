import yaml
import os

print("="*70)
print("FIXING data.yaml PATH")
print("="*70)

# Get absolute path to dataset
dataset_dir = os.path.abspath('License-Plate-Detection-1')

print(f"\n📁 Dataset location: {dataset_dir}")

# Verify folders exist
train_dir = os.path.join(dataset_dir, 'train', 'images')
valid_dir = os.path.join(dataset_dir, 'valid', 'images')

print(f"\n🔍 Checking directories:")
print(f"   Train: {os.path.exists(train_dir)} - {train_dir}")
print(f"   Valid: {os.path.exists(valid_dir)} - {valid_dir}")

if not os.path.exists(train_dir):
    print("\n❌ Training directory not found!")
    print("Listing dataset contents:")
    for item in os.listdir(dataset_dir):
        print(f"   - {item}")
    exit(1)

# Read current data.yaml
yaml_file = os.path.join(dataset_dir, 'data.yaml')

print(f"\n📄 Reading: {yaml_file}")

with open(yaml_file, 'r') as f:
    data = yaml.safe_load(f)

print("\n📋 Current data.yaml:")
print(data)

# Fix paths
data['path'] = dataset_dir
data['train'] = 'train/images'
data['val'] = 'valid/images'

if 'test' in data and os.path.exists(os.path.join(dataset_dir, 'test', 'images')):
    data['test'] = 'test/images'

print("\n✏️  Updated data.yaml:")
print(data)

# Save
with open(yaml_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

print(f"\n✅ data.yaml fixed!")

# Verify
train_count = len([f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
valid_count = len([f for f in os.listdir(valid_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])

print(f"\n📊 Dataset verified:")
print(f"   Training: {train_count} images")
print(f"   Validation: {valid_count} images")
print(f"   Total: {train_count + valid_count}")

print("\n🚀 Ready to train!")
print("   python train_final.py")
print("="*70)