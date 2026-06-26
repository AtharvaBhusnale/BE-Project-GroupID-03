import os

lr_folder = 'test_images_lr'
hr_folder = 'test_images_hr'

print(f"--- Checking contents of '{lr_folder}' ---")
try:
    lr_files = os.listdir(lr_folder)
    if not lr_files:
        print("Result: Folder is EMPTY.")
    else:
        print(f"Found {len(lr_files)} files. Here are the first 10:")
        for f in lr_files[:10]:
            print(f"  - {f}")
except FileNotFoundError:
    print(f"Error: Folder '{lr_folder}' DOES NOT EXIST.")
except Exception as e:
    print(f"An error occurred: {e}")

print(f"\n--- Checking contents of '{hr_folder}' ---")
try:
    hr_files = os.listdir(hr_folder)
    if not hr_files:
        print("Result: Folder is EMPTY.")
    else:
        print(f"Found {len(hr_files)} files. Here are the first 10:")
        for f in hr_files[:10]:
            print(f"  - {f}")
except FileNotFoundError:
    print(f"Error: Folder '{hr_folder}' DOES NOT EXIST.")
except Exception as e:
    print(f"An error occurred: {e}")