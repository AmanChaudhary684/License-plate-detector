import os
import yaml

print("Fixing dataset configuration...")

# Get absolute path to backend folder
backend_path = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(backend_path, 'License-Plate-Detection-1')

print(f"Backend path: {backend_path}")
print(f"Dataset path: {dataset_path}")

# Read existing data.yaml
yaml_file = os.path.join(dataset_path, 'data.yaml')
with open(yaml_file, 'r') as f:
    data = yaml.safe_load(f)

print(f"\nOriginal data.yaml:")
print(data)

# Update paths to absolute paths
data['path'] = dataset_path
data['train'] = 'train/images'
data['val'] = 'valid/images'

# Check if test exists
if os.path.exists(os.path.join(dataset_path, 'test', 'images')):
    data['test'] = 'test/images'

print(f"\nUpdated data.yaml:")
print(data)

# Save updated yaml
with open(yaml_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

print(f"\n✓ data.yaml updated successfully!")

# Verify directories exist
train_dir = os.path.join(dataset_path, 'train', 'images')
valid_dir = os.path.join(dataset_path, 'valid', 'images')

print(f"\nVerifying directories:")
print(f"  Train images: {train_dir}")
print(f"    Exists: {os.path.exists(train_dir)}")
if os.path.exists(train_dir):
    count = len([f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
    print(f"    Images: {count}")

print(f"  Valid images: {valid_dir}")
print(f"    Exists: {os.path.exists(valid_dir)}")
if os.path.exists(valid_dir):
    count = len([f for f in os.listdir(valid_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
    print(f"    Images: {count}")

print("\n✓ Ready to train!")