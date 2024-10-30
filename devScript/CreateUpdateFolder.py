
from DirectoryComparator import DirectoryComparator
import os
import shutil
from tqdm import tqdm
from FileCopier import FileCopier

class UpdateFolderCreator:
    def __init__(self,new_up_dir:str,old_up_dir:str,update_dir:str):
        self.new_up_dir = new_up_dir
        self.old_up_dir = old_up_dir
        self.update_dir = update_dir

        if not os.path.exists(self.update_dir):
            os.makedirs(self.update_dir)
        
        self.Create_update_folder()

    def Create_update_folder(self):
        self._get_files_for_update_folder()
        self._create_FilesToRemove_txt()

        copier= FileCopier(self.new_up_dir,self.update_dir)
        copier.copy_files(self.files_to_add)

    def _compare_directories(self):
        self.dir_comparator = DirectoryComparator(self.old_up_dir,self.new_up_dir)
    
    def _get_files_for_update_folder(self):
        self._compare_directories()
        self.files_to_add = self.dir_comparator.get_unique_files_new_update_dir() + self.dir_comparator.get_new_files()
        self.files_to_remove = self.dir_comparator.get_missing_files()
    
    def _create_FilesToRemove_txt(self):
        with open(os.path.join(self.update_dir,'files_to_remove.txt'),'w') as file:
            for el in self.files_to_remove:
                file.write(el + '\n')

if __name__ == '__main__':
    new_dir = '/home/item/UpdateOperations/Vtopia_Nord_BEV'
    old_dir = '/home/item/UpdateOperations/old/Vtopia_Nord_BEV'
    update_dir = '/home/item/UpdateOperations/Update/Vtopia_Nord_BEV'

    update_creator = UpdateFolderCreator(new_dir, old_dir, update_dir)