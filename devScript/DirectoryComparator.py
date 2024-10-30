import os
import hashlib
from tqdm import tqdm


import os
import hashlib
from tqdm import tqdm


class DirectoryComparator:
    def __init__(self, old_up_dir: str, new_up_dir: str):
        self.old_up_dir = old_up_dir
        self.new_up_dir = new_up_dir
        
        self.RunDirectoryComparator()

    
    def RunDirectoryComparator(self):
        self._compare_directories()
        self._compare_common_files(self.common_files)
        self._print_differences()

    def get_new_files(self):
        return list(self._unique_files_new_update_dir) + list(self._differing_files)

    def get_unique_files_new_update_dir(self):
        return list(self._unique_files_new_update_dir)

    def get_missing_files(self):
        return list(self._unique_files_old_update_dir)
    
    
    def _hash_file(self, file_path: str):
        hash_sha256 = hashlib.sha256()

        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_sha256.update(chunk)

        return hash_sha256.hexdigest()

    def _collect_files(self, directory: str):
        all_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                all_files.append(relative_path)

        return all_files

    def _print_unique_files(self):
        if self._unique_files_old_update_dir:
            print("Files only in the old update:")
            for file in self._unique_files_old_update_dir:
                print(file)
        if self._unique_files_new_update_dir:
            print("Files only in the new update:")
            for file in self._unique_files_new_update_dir:
                print(file)

    def _compare_common_files(self, common_files: set):
        self._differing_files = []

        print("Comparing common files...")
        for file in tqdm(common_files, desc="Progress", unit="file"):
            file1 = os.path.join(self.old_up_dir, file)
            file2 = os.path.join(self.new_up_dir, file)

            if self._hash_file(file1) != self._hash_file(file2):
                self._differing_files.append(file)

    def _print_differences(self):
        if self._differing_files:
            print("Files with differences in content:")
            for file in self._differing_files:
                print(f"File: {file}")
        else:
            print("The directories are identical in content.")

    def _compare_directories(self):
        all_files_old_update_dir = self._collect_files(self.old_up_dir)
        all_files_new_update_dir = self._collect_files(self.new_up_dir)

        self._unique_files_old_update_dir = set(all_files_old_update_dir) - set(all_files_new_update_dir)
        self._unique_files_new_update_dir = set(all_files_new_update_dir) - set(all_files_old_update_dir)
        self.common_files = set(all_files_old_update_dir) & set(all_files_new_update_dir)

        #self._print_unique_files()


if __name__ == '__main__':
    dir2 = '/home/item/Vtopia_Nord_BEV/delivered_versions/15/Vtopia_Nord_BEV'
    dir1 = '/home/item/Vtopia_Nord_BEV/delivered_versions/Vtopia_Nord_BEV'
    comparator = DirectoryComparator(dir1, dir2)
