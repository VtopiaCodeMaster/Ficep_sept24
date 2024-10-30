import os
import sys
import subprocess
import argparse
import json
import zipfile
import shutil
from ftplib import FTP
from CreateUpdateFolder import UpdateFolderCreator
from FileCopier import FileCopier

def main():
    parser = argparse.ArgumentParser(description='Create an update folder and zip it.')
    parser.add_argument('--lastVersion_path', '-lvp', type=str, help='Path to the folder to be processed', default="old")
    parser.add_argument('--developement_path', type=str, help='Path to the folder to be processed', default="Ficep_sept24")
    parser.add_argument('--zipignore', type=str, help='Path to the file containing the exclusion patterns', default="Ficep_sept24/.zipignore")
    parser.add_argument('--zip_pw', type=str, help='Password for the zip file', default="D4M4R0_cmg")
    parser.add_argument('--installer_script', type=str, help='Path to the installer script wrt the lastVersion_path', default="02_installNewVersion.bin")
    parser.add_argument('--delivered_versions_folder', type=str, help='Path to the folder where a copy of the delivered version will be stored wrt /home/item/', default="Ficep_sept24/delivered_versions")
    args = parser.parse_args()

    os.chdir('/home/item')
    print(f"Current working directory: {os.getcwd()}")


    # Check if the folder exists and define paths of working directories
    developement_dir = args.developement_path
    if not os.path.isdir(developement_dir):
        print(f"Error: Folder '{developement_dir}' does not exist.")
        sys.exit(1)
    print(f"Processing folder: {developement_dir}")
    version = read_json(f"{developement_dir}/current_version.json")["version"]
    filteredNewVersionDir = f"UpdateOperations/{developement_dir}"
    oldVersionDir = f"UpdateOperations/old/{developement_dir}"
    packedUpgradeDir = f"UpdateOperations/Update_folder/{developement_dir}"

    # Copy old version to the working directory
    if os.path.exists(oldVersionDir):
        shutil.rmtree(oldVersionDir)
    print(f"Copying old version to: {oldVersionDir}...")
    shutil.copytree(args.lastVersion_path, oldVersionDir)
    
    # Copy new version to the working directory applying the exclusion patterns specified in the .zipignore file
    if os.path.exists(filteredNewVersionDir):
        shutil.rmtree(filteredNewVersionDir)
    os.makedirs(filteredNewVersionDir)
    print(f"New directory created: {filteredNewVersionDir}")
    if args.zipignore:
        exclude_patterns = load_ignore_from_file(args.zipignore)
        exclude_patterns = [p.replace('*', '') for p in exclude_patterns]
    else:
        exclude_patterns = []
    #print(f"Exclusion patterns: {exclude_patterns}")
    dev_dir_ls = get_all_files(developement_dir)
    obj_to_copy = [f for f in dev_dir_ls if not any([pattern in f for pattern in exclude_patterns])]
    #print(f"Files to copy: {obj_to_copy}")
    fileCopier = FileCopier('Ficep_sept24', filteredNewVersionDir)
    fileCopier.copy_files(obj_to_copy)
 

    # Compare new and old version directories and create the upgrade folder
    UpdateFolderCreator(filteredNewVersionDir, oldVersionDir, packedUpgradeDir)

    # Copy the installer script to the working directory
    shutil.copy(f"{filteredNewVersionDir}/{args.installer_script}", f"{packedUpgradeDir}/{args.installer_script}") 

    # Zip the updated directory
    zip_filename = f"update_v01_{str(version).replace('.','')}.zip"
    if os.path.isfile(zip_filename):
        try:
            os.remove(zip_filename)
            print(f"Old zip file '{zip_filename}' successfully deleted.")
        except Exception as e:
            print(f"Error: Failed to delete old zip file. {str(e)}")
            sys.exit(1)

    os.chdir(packedUpgradeDir)
    os.chdir('..')
    print(f"Current working directory: {os.getcwd()}")
    zip_command = f"zip -r -P {args.zip_pw} {zip_filename} {developement_dir}"
    print(f"Running command: {zip_command}")
    result = subprocess.run(zip_command, shell=True)

    # Check if the zip command was successful
    if result.returncode == 0:
        print(f"Folder '{packedUpgradeDir}' successfully zipped into '{zip_filename}' with password protection.")
    else:
        print("Error: Failed to zip the folder.")
        sys.exit(1)

    # Create latest_version.json with relevant data
    update_json = {}
    update_json["version"] = version
    update_json["url"] = f"https://www.item.to.it/Ficep/Polaris/v01/{zip_filename}"
    update_json["zip_size"] = int(os.path.getsize(zip_filename) / 1024)
    print(f"Zip size: {update_json['zip_size']} KB")

    os.makedirs("zip_with_pw_check_size", exist_ok=True)
    input("Continue?")
    # Extract zip file to check size
    print("Extracting zip file to check size...")
    extract_files(zip_filename, "zip_with_pw_check_size", "D4M4R0_cmg")

    update_json["extracted_size"] = int(check_dim("zip_with_pw_check_size"))
    print(f"Vtopia size: {update_json['extracted_size']} KB")

    # Write latest_version.json
    print("Writing latest_version.json...")
    write_json(update_json, "latest_version.json")

    # Clean up extracted files
    print("Cleaning up...")
    shutil.rmtree("zip_with_pw_check_size")

    # Upload update to server if desired
    if input("Do you want to upload the update to the server? (y/n): ").lower() == 'y':
        load_on_server([zip_filename, "latest_version.json"])

    # Copy the zip to delivered_versions folder if desired
    if input("Do you want to copy the zip to delivered_versions folder? (y/n): ").lower() == 'y':
        os.chdir('/home/item')
        newVersionStorageDir = f"{args.delivered_versions_folder}/update_v01_{str(version).replace('.','')}"
        if os.path.exists(newVersionStorageDir):
            shutil.rmtree(newVersionStorageDir)
        print(f"Current working directory: {os.getcwd()}")
        if not os.path.exists(args.delivered_versions_folder):
            os.makedirs(args.delivered_versions_folder)
        shutil.copytree(f"UpdateOperations/Update_folder", newVersionStorageDir)
        os.rename(f"{newVersionStorageDir}/{developement_dir}", f"{newVersionStorageDir}/zipContent")
        shutil.copytree(filteredNewVersionDir, f"{newVersionStorageDir}/{developement_dir}")

    if input("Do you want to clean the temporary directory used for the update packing operations?") == 'y':
        shutil.rmtree("/home/item/UpdateOperations")

        
    print("Done!")


def get_all_files(source_folder):
    return [
        os.path.relpath(os.path.join(root, file), source_folder)
        for root, _, files in os.walk(source_folder)
        for file in files
    ]

def load_ignore_from_file(filename):
    try:
        with open(filename, 'r') as file:
            patterns = [line.strip() for line in file.readlines()]
        
        return patterns
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""


def check_dim(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # Skip if it's a symbolic link
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)

    # Convert bytes to kilobytes
    total_size_kb = total_size / 1024

    return total_size_kb

def read_json(file_path):

    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    
def write_json(data, file_path):

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def extract_files(zip_file, extractedFiles_dir, password):
    """
    Estrae i file dall'archivio ZIP nella directory di destinazione.
    """
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            if password:
                zip_ref.extractall(extractedFiles_dir, pwd=password.encode('utf-8'))
            else:
                zip_ref.extractall(extractedFiles_dir)
    except zipfile.BadZipFile:
        print(f"Errore: Il file {zip_file} non è un archivio ZIP valido.")
        return
    except RuntimeError as e:
        if 'password' in str(e).lower():
            print("Errore: Password errata o non fornita per l'archivio ZIP.")
        else:
            print(f"Errore durante l'estrazione: {e}")
    except Exception as e:
        print(f"Errore durante l'estrazione: {e}")


def load_on_server(files):
    # FTP server details
    ftp_server = 'ftp.item.to.it'
    ftp_username = '6871331@aruba.it'
    ftp_password = 'Item2024!?'
    remote_path = '/item.to.it/Ficep/Polaris/v01/'

    # Connect to the FTP server
    ftp = FTP(ftp_server)
    ftp.login(ftp_username, ftp_password)

    # Change to the desired directory on the FTP server
    ftp.cwd(remote_path)

    # Loop through every file in the directory
    for file_path in files:
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                # Upload file to FTP server
                ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)
                print(f'Successfully uploaded {os.path.basename(file_path)}')

    # Quit the FTP session
    ftp.quit()



if __name__ == "__main__":
    main()
