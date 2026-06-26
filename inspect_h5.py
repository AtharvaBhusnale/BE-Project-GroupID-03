
import os
import h5py

SOURCE_DIR = os.path.join('brats_dataset', 'BraTS2020_training_data', 'content', 'data')

def inspect_first_h5():
    if not os.path.exists(SOURCE_DIR):
        print(f"Directory not found: {SOURCE_DIR}")
        return

    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.h5')]
    if not files:
        print("No .h5 files found.")
        return

    first_file = files[0]
    filepath = os.path.join(SOURCE_DIR, first_file)
    print(f"Inspecting: {filepath}")

    try:
        with h5py.File(filepath, 'r') as f:
            print(f"Keys: {list(f.keys())}")
            for key in f.keys():
                data = f[key]
                print(f"  Key '{key}' shape: {data.shape}, dtype: {data.dtype}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    inspect_first_h5()
