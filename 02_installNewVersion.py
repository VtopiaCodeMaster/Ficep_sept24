import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from Vlib.VtopiaSWUpdate.FileCopier import *
from Vlib.Gtk.automaticProcedureGUI import AutomaticProcedureGUI
from Vlib.VtopiaSWUpdate.Installerconfig import InstallerConfig
from Vlib.VtopiaSWUpdate.Installer import Installer

# nuitka --standalone --onefile --follow-imports --output-dir=installer_compileDir 03_installNewVersion.py 

if __name__ == '__main__':
    Gtk.init(None)
    config = InstallerConfig(
        installSrcPath="/home/item/updatefolder/Ficep_sept24",
        installPath="/home/item/Ficep_sept24",
        #installPath="/home/item/FakeInstallDir/Vtopia_Nord_BEV",
        fileRemoverTxtPath="/home/item/updatefolder/Ficep_sept24/files_to_remove.txt"
    )
    window = AutomaticProcedureGUI("Installation", logo_path="/home/item/Ficep_sept24/Ficep_Logo.png")
    window.runInThread()

    installer = Installer(
        config=config,
        setStatusCallback=window.setLabel,
        progressCallback=window.setProgressBar
    )
    installer.install_update()
    window.scheduleClose(10)
