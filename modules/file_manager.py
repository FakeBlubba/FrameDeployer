import os
import shutil

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
