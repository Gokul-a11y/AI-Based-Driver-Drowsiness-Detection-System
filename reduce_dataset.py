import os
import random

dataset_path = r"D:\Projects\Drowsiness_Project\dataset"

LIMIT = 5000

for folder in ["open", "closed"]:
    path = os.path.join(dataset_path, folder)
    files = os.listdir(path)

    print(f"{folder} before:", len(files))

    if len(files) > LIMIT:
        remove_files = random.sample(files, len(files) - LIMIT)

        for f in remove_files:
            os.remove(os.path.join(path, f))

    print(f"{folder} after:", len(os.listdir(path)))

print("✅ Dataset reduced")