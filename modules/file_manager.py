import os
import shutil
from datetime import datetime

def create_media_folder(trend):
    """
    Creates a folder for media based on the trend name and current date.

    Args:
        trend (str): The trend or topic name.

    Returns:
        str: The path to the created folder.
    """
    date_string = datetime.now().strftime("%d-%m-%Y")
    folder_path = os.path.join("media", f"{trend} {date_string}")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def delete_files_except_mp4(directory):
    """
    Delete all files in the given directory except those with a .mp4 extension.

    :param directory: Path to the directory.
    :type directory: str
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.mp4'):
                os.remove(os.path.join(root, file))

def delete_folder(directory):
    """
    Delete the specified directory and all its contents.

    :param directory: Path to the directory.
    :type directory: str
    """
    shutil.rmtree(directory)
