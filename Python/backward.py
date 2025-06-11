import os
import shutil

def move_files_to_script_folder():
    script_folder = os.path.abspath(os.path.dirname(__file__))

    for foldername, subfolders, filenames in os.walk(script_folder):
        if foldername == script_folder:
            continue  # Skip the script's own folder

        for filename in filenames:
            src_path = os.path.join(foldername, filename)
            dst_path = os.path.join(script_folder, filename)

            # Overwrite if file exists
            shutil.move(src_path, dst_path)

        # Remove empty folders
        if not os.listdir(foldername):
            os.rmdir(foldername)

if __name__ == "__main__":
    move_files_to_script_folder()
