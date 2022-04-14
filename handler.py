from Sources.json_handler import json_handler
from logger_settings import logger
from PyQt5.QtGui import QIcon
from UI.ui_MainWindow import *
import sys
import os
from Sources.utils import  set_local_sizes, set_cloud_sizes, check_space_availability, local_cleaner, cloud_cleaner
from os.path import expanduser
import Style.resources  # Mantener
import Sources.drive as drive
import Sources.backup as backup
import re
import logWindow
import optionsWindow
import authWindow
from Sources.task_scheduler import run_task
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMessageBox,
    QMenu
)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Class to relate the functions of the lower layers to the interface elements"""

    def __init__(self, *args, **kwargs):
        """Constructor that will be in charge of initializing the main components."""
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_MainWindow.__init__(self)
        self.init_ui()

    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812, 706)
        self.lb_path
        
        json_data = json_handler()
        array = json_data.get_list("DIRECTORIES")
        
        for route in array:
            self.list_Paths.addItem(route)
        self.update_local_size()
        self.update_cloud_size()
        
        self.pr_backup.setValue(0)
        self.set_values_automatic_backup(json_data)
        self.chk_compress.setChecked(json_data.get_list("DRIVE", "COMPRESS"))

        self.list_Paths.customContextMenuRequested.connect(self.modifyItem)
        self.chk_automatic.toggled.connect(self.automatic)
        self.bt_backup.clicked.connect(self.backup_thread)
        self.chk_compress.toggled.connect(self.compress)
        self.link_auth.clicked.connect(self.startAuthWindow)
        self.bt_log_viewer.clicked.connect(self.startLogWindow)
        self.bt_options.clicked.connect(self.startOptionsWindow)
        self.bt_target.clicked.connect(self.select_path)
        self.bt_save_path.clicked.connect(self.save_path)
        self.bt_save_times.clicked.connect(self.save_times)
        self.bt_refresh.clicked.connect(lambda: set_cloud_sizes())
        self.bt_refresh.clicked.connect(self.update_cloud_size)

    #Function to update size of list view
    def update_local_size(self):
        json_data = json_handler()
        self.lb_files.setText(json_data.get_list("SIZES", "LOCAL_FILES"))
        self.lb_folders.setText(json_data.get_list("SIZES", "LOCAL_FOLDERS"))
        self.lb_size.setText(json_data.get_list("SIZES", "LOCAL_SIZE"))

    #Comprobe sizes of cloud
    def check_cloud_changes(self):
        json_data = json_handler()
        if json_data.get_list("DRIVE", "AUTHENTICATED"):
            set_cloud_sizes()
            self.update_cloud_size()
            
    #Function to update size of cloud          
    def update_cloud_size(self):
        json_data = json_handler()
        self.lb_used.setText(json_data.get_list("SIZES", "CLOUD_USED"))
        self.lb_free.setText(json_data.get_list("SIZES", "CLOUD_FREE"))
        self.lb_total.setText(json_data.get_list("SIZES", "CLOUD_TOTAL"))
        self.pr_size.setMinimum(0)
        self.pr_size.setMaximum(100)
        self.pr_size.setValue(json_data.get_list("SIZES", "CLOUD_PERCENT"))
        
    #Function to set values of config.json      
    def set_values_automatic_backup(self, json_data):
        state_auto = json_data.get_list("DRIVE", "AUTO_BACKUP")
        self.chk_automatic.setChecked(state_auto)
        self.sp_day.setEnabled(state_auto)
        self.sp_day.setValue(json_data.get_list("TIMES", "DAY"))
        self.sp_hour.setEnabled(state_auto)
        self.sp_hour.setValue(json_data.get_list("TIMES", "HOUR"))
        self.sp_month.setEnabled(state_auto)
        self.sp_month.setValue(json_data.get_list("TIMES", "MONTH"))
        self.bt_save_times.setEnabled(state_auto)

    #Function to actualize values of automatic config
    def automatic(self):
        json_data = json_handler()
        state = True
        if not self.chk_automatic.isChecked():
           state = False
        self.sp_day.setEnabled(state)
        self.sp_hour.setEnabled(state)
        self.sp_month.setEnabled(state)
        self.bt_save_times.setEnabled(state)
        json_data.write_field("DRIVE", state, "AUTO_BACKUP")

    def save_times(self):
        json_data = json_handler()
        json_data.write_field("TIMES", self.sp_day.value(), "DAY")
        json_data.write_field("TIMES", self.sp_hour.value(), "HOUR")
        json_data.write_field("TIMES", self.sp_month.value(), "MONTH")
        if self.chk_automatic.isChecked():
           run_task(self.sp_hour.value(),self.sp_day.value(), self.sp_month.value())
           QMessageBox.information(self,"info", "Automatic backup configured")
           logger.info("Automatic backup configured")
            

    def modifyItem(self, item):
        json_data = json_handler()
        if(self.list_Paths.itemAt(item)):
            contextMenu = QMenu(self)
            editAct = contextMenu.addAction("Edit")
            deleteAct = contextMenu.addAction("Delete")
            action = contextMenu.exec_(QtGui.QCursor().pos())
            if action == editAct:
                self.edit_item(item)
            if action == deleteAct:
                self.list_Paths.takeItem(self.list_Paths.currentRow())
                json_data.remove_field_list("DIRECTORIES",self.list_Paths.row(self.list_Paths.itemAt(item)))
                #Update local sizes
                set_local_sizes()
                self.update_local_size()
                
    def edit_item(self, item):
        file = self.getOpenFilesAndDirs(self,"Folder or files to backup", expanduser("~"))
        
        if not file:
            return None
        elif len(file)>1:
            QMessageBox.warning(self, "Warning", "You can only replace one path with another path")
            logger.warning("You can only replace one path with another path")
        else:
            path = file[0]
            if self.not_exists_path([path]):
                json_data = json_handler()
                self.list_Paths.currentItem().setText(os.path.normpath(path))
                json_data.edit_field_list("DIRECTORIES", self.list_Paths.row(self.list_Paths.itemAt(item)), os.path.normpath(path))
                #Update local sizes
                set_local_sizes()
                self.update_local_size()
            else:
                QMessageBox.warning(self, "Warning", "The directory or file already exists")
        

    def startAuthWindow(self):
        self.hide()  
        self.ui = authWindow.AuthWindow()
        self.ui.show() 

    def startLogWindow(self):
        self.hide()
        self.ui = logWindow.LogWindow()
        self.ui.show()

    def startOptionsWindow(self):
        self.hide()
        self.ui = optionsWindow.OptionsWindow()
        self.ui.show()

    ##Selector of path
    """Function to select de path of the file"""
    def select_path(self):
        button = self.sender()
        try:
            if button:
                files = self.getOpenFilesAndDirs(self,"Folder or files to backup", expanduser("~"))
                if not self.valid_path(files) or not files:
                    return None
                elif self.not_exists_path(files):
                    if len(files) > 1:
                        logger.info("Paths selected: " + ",".join(files))
                        self.lb_path.setPlainText(os.path.normpath(",".join(files)))
                    else:
                        logger.info("Path selected: " + str(files[0]))
                        self.lb_path.setPlainText(os.path.normpath(files[0]))
                    return files
                else:
                    QMessageBox.warning(self, "Warning", "The selected files already exist")
        except Exception as e:
            msg = QMessageBox()
            logger.error(str(e))
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Path of the file not valid")
            msg.setWindowTitle("Error")
            msg.exec_()
            return None

    def save_path(self):
        paths = [os.path.normpath(p) for p in self.lb_path.toPlainText().split(",")]
        json_data = json_handler()
        if not self.valid_path(paths):
            QMessageBox.information(self, "Warning", "Select a correct path")   
        elif paths and self.not_exists_path(paths):
            for p in paths:
                json_data.add_field_list("DIRECTORIES", p)
                self.list_Paths.addItem(p)
                set_local_sizes()
                self.update_local_size()
            if(check_space_availability()==False):
              self.list_Paths.takeItem(self.list_Paths.count()-1)
              json_data.remove_field_list("DIRECTORIES",self.list_Paths.row(self.list_Paths.item(self.list_Paths.count())))
              set_local_sizes()
              self.update_local_size()
              QMessageBox.information(self, "Info", "There is not enough space in drive")
            else:
              QMessageBox.information(self, "Info", "Paths saved")
        else:
            QMessageBox.information(self, "Info", "Select paths that don't exists")   
            
    def not_exists_path(self,path):
        notExists = True
        for p in path:
            for i in range(self.list_Paths.count()):
                if self.list_Paths.item(i).text() == os.path.normpath(p):
                    notExists = False
        return notExists
    
    def valid_path(self,path):
        valid = True
        for p in path:
            if not p or re.match("/^$|\s+/|\.+",p) or (not os.path.isdir(p) and not os.path.isfile(p)):
                valid = False
        return valid

    def compress(self):
        json_data = json_handler()
        state = True
        if not self.chk_compress.isChecked():
           state = False
        json_data.write_field("DRIVE", state, "COMPRESS")

    def backup_thread(self):
        # Delete extra local backups
        local_cleaner()
        cloud_cleaner()
        # Initial actions
        self.update_progress(0)
        # Create a QThread object
        self.thread = QThread()
        self.thread.setTerminationEnabled(True)
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        self.thread.setTerminationEnabled(enabled=True)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress)
        self.worker.not_size.connect(self.not_size)
        self.worker.status.connect(self.show_status)
        self.worker.blk.connect(self.show_problems)
        self.thread.start()
            
    def update_progress(self, progress):
        self.pr_backup.setValue(progress)
        self.bt_backup.setEnabled(progress == 100 or progress == 0)
        
    def not_size(self, not_size):
        if(not_size==True):
          QMessageBox.warning(
          self, "Warning", "There's no space left")
        
    def show_status(self,status,warning=False):
        self.lb_backup.setText(status)
        if warning:
           self.lb_backup.setStyleSheet("color : red")
           QMessageBox.critical(self, "Critical", status) 

    def show_problems(self, output):
        if not output:
            self.bt_backup.setEnabled(True)

            QMessageBox.warning(
                self, "Warning", "You need to be authenticated")
 
    """Function to generate a file explorer"""
    def getOpenFilesAndDirs(self, parent=None, caption='', directory='', 
                            filter='', initialFilter='', options=None):
        def updateText():
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append('"{}"'.format(index.data()))
            lineEdit.setText(' '.join(selected))

        dialog = QtWidgets.QFileDialog(parent, windowTitle=caption)
        dialog.setFileMode(dialog.ExistingFiles)
        if options:
            dialog.setOptions(options)
        dialog.setOption(dialog.DontUseNativeDialog, True)
        if directory:
            dialog.setDirectory(directory)
        if filter:
            dialog.setNameFilter(filter)
            if initialFilter:
                dialog.selectNameFilter(initialFilter)

        dialog.accept = lambda: QtWidgets.QDialog.accept(dialog)

        stackedWidget = dialog.findChild(QtWidgets.QStackedWidget)
        view = stackedWidget.findChild(QtWidgets.QListView)
        view.selectionModel().selectionChanged.connect(updateText)

        lineEdit = dialog.findChild(QtWidgets.QLineEdit)

        dialog.directoryEntered.connect(lambda: lineEdit.setText(''))

        dialog.exec_()
        return dialog.selectedFiles()
    
class Worker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    status = pyqtSignal(str,bool)
    blk = pyqtSignal(bool)
    not_size = pyqtSignal(bool)

    def run(self):
        try:
            if(check_space_availability()==False):
              self.not_size.emit(True)
            else:    
                output = backup.recompile(self.update_progress, self.show_status)
                self.blk.emit(output)
                self.finished.emit()
            
        except (OSError, IndexError, FileNotFoundError) as e:
            self.status.emit("Problems with your files",True)
            logger.error(e)
            self.progress.emit(0)
            self.finished.emit()

    def update_progress(self, percent):
        self.progress.emit(percent)
    
    def show_status(self, status,warning=False):
        self.status.emit(status,warning)
      


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qss_file = open('Style/theme.qss').read()
    app.setStyleSheet(qss_file)
    app.setWindowIcon(QIcon("Resources/icon.png"))
    app.aboutToQuit.connect(lambda: os.system('taskkill /f /im gdrive.exe'))
    # AUTH_status
    drive.auth_status()
    # Set sizes in json config file
    set_local_sizes()
    set_cloud_sizes()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())