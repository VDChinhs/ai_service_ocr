import os
import gdown

def create_folder(name_folder: str):
    os.makedirs(name_folder, exist_ok=True)
    print(f"Create folder {name_folder}")

def is_model_path_exists(model_path: str) -> bool:
    return os.path.exists(model_path)

def download_model_from_drive(file_id: str, output_path: str) -> bool:
    if not os.path.exists(output_path):
        print(f"[Download] Model does not exist. Downloading from Google Drive...")
        url = f"https://drive.google.com/uc?id={file_id}"
        try:
            gdown.download(url, output_path, quiet=False, fuzzy=True)
        except Exception as e:
            print(f"[Error] Failed to download model: {e}")
            return False

        if os.path.exists(output_path):
            print(f"[Download] Model has been downloaded to: {output_path}")
            return True
        else:
            print(f"[Error] Model file was not found after download!")
            return False
    else:
        print(f"[Check] Model already exists: {output_path}")
        return True