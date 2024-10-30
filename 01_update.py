
from Vlib.VtopiaSWUpdate.UpdateConfig import UpdateConfig
from Vlib.Gtk.automaticProcedureGUI import AutomaticProcedureGUI
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Vlib.VtopiaSWUpdate.Updater import Updater

# nuitka --standalone --onefile --follow-imports --output-dir=installer_compileDir 02_update.py
# scp installer_compileDir/02_update.bin item@10.10.10.150:Vtopia_Nord_BEV/
if __name__ == '__main__':

    config = UpdateConfig( 
        urlJson = 'https://www.item.to.it/Ficep/Polaris/v01/latest_version.json',
        zipFile = '/home/item/update.zip',
        unzipPath = '/home/item/updatefolder',
        installerFile = '/home/item/updatefolder/Ficep_sept24/03_installNewVersion.bin',
        zipPassword = 'D4M4R0_cmg',
        systemPassword = 'item178',
        installPath = '/home/item/Ficep_sept24',
        localJsonFile = '/home/item/Ficep_sept24/current_version.json',
        backupPath = '/home/item/backup',
        filesToRemoveAfterInstall=["files_to_remove.txt","02_installNewVersion.bin"]
    )
    Gtk.init(None)
    
    window = AutomaticProcedureGUI("Upgrade", logo_path="/home/item/Ficep_sept24/VTopia_logo.png")
    window.runInThread()

    updater = Updater(config=config, 
                      setStatusCallback=window.setLabel, 
                      setProgressCallback=window.setProgressBar)

    updater.update()
    window.scheduleClose(10)
