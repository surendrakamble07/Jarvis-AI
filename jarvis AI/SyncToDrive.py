import os
import shutil

def sync_to_drive():
    source = r"C:\Users\suren\OneDrive\Desktop\jarvis AI\Data"
    destination = r"G:\My Drive\JarvisData"

    if not os.path.exists(destination):
        os.makedirs(destination)

    for filename in os.listdir(source):
        src_file = os.path.join(source, filename)
        dest_file = os.path.join(destination, filename)
        try:
            shutil.copy2(src_file, dest_file)
            print(f"Copied: {filename}")
        except Exception as e:
            print(f"Failed to copy {filename}: {e}")

if __name__ == "__main__":
    sync_to_drive()
