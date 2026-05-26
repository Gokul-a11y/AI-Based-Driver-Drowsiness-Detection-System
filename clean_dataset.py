import os
from PIL import Image

dataset_path = r"D:\Projects\Drowsiness_Project\dataset"

for folder in ["open", "closed"]:
    folder_path = os.path.join(dataset_path, folder)

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        try:
            img = Image.open(file_path)
            img.verify()   # check if image is valid
        except:
            print("Removing corrupted:", file_path)
            os.remove(file_path)

print("✅ Dataset cleaned")