import os
import shutil
from tqdm import tqdm

class FileCopier:
    def __init__(self, source_folder, destination_folder, setStatusCallback=None, setProgressCallback=None):
        self._source_folder = source_folder
        self._destination_folder = destination_folder
        self._setStatusCallback = setStatusCallback
        self._setProgressCallback = setProgressCallback

    def copy_files(self, files_to_copy=None):
        self._ensure_directory_exists(self._destination_folder)

        if files_to_copy is None:
            files_to_copy = self._get_all_files(self._source_folder)

        for relative_file in tqdm(files_to_copy, desc="Copying files", unit="file"):
            source_path = os.path.join(self._source_folder, relative_file)
            destination_path = self._destination_folder
            #try:
            self._copy_fileWithStructure(source_path, self._source_folder, destination_path)
            print(f"Copied: {relative_file}")
            self._log_success(f"Copied: {relative_file}")
            self._log_progress(relative_file)
            #except Exception as e:
            #    self._handleException(f"Error copying {relative_file}: {e}")

    def _ensure_directory_exists(self, directory_path):
        os.makedirs(directory_path, exist_ok=True)

    def _get_all_files(self, source_folder):
        return [
            os.path.relpath(os.path.join(root, file), source_folder)
            for root, _, files in os.walk(source_folder)
            for file in files
        ]

    def _copy_fileWithStructure(self, source_path, source_base_path, destination_base_path):
        destination_path = source_path.replace(source_base_path, destination_base_path).split('/')[:-1]
        destination_path = '/'.join(destination_path)
        print(f"Attempting to copy from {source_path} to {destination_path}")
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file does not exist: {source_path}")
        
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        if os.path.samefile(source_path, destination_path):
            print(f"Skipping {source_path} as source and destination are the same.")
            return

        self._ensure_directory_exists(os.path.dirname(destination_path))
        
        shutil.copy2(source_path, destination_path)


    def _handleException(self, message):
        raise CopyError(message)
    
    def _log_success(self, message):
        if self._setStatusCallback:
            self._setStatusCallback(message)
        else:
            print(f"Success: {message}")

    def _log_progress(self, file):
        if self._setProgressCallback:
            self._setProgressCallback(f"Copied: {file}")
        else:
            print(f"Copied: {file}")

class CopyError(Exception):
    def __init__(self, message):
        super().__init__(message)

if __name__ == "__main__":
    def print_callback(message):
        print(message)

    def progress_callback(progress):
        print(progress)

    def end_callback():
        print("Copy operation completed")

    source = "/home/item/Recordings/Al"
    destination = "/home/item/Recordings/Al1"
    copier = FileCopier(source, destination, setStatusCallback=print_callback, setProgressCallback=progress_callback, endCallback=end_callback)
    copier.copy_files()
