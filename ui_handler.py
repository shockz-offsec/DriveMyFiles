from genericpath import isfile
from json_handler import json_handler
from logger_settings import logger
from ui_OptionsWindow import Ui_OptionsWindow
from ui_LogWindow import Ui_LogWindow
from ui_AuthWindow import Ui_AuthWindow
from PyQt5.QtCore import QEvent, QModelIndex, QPoint
from PyQt5.QtGui import QIcon, QPalette
from ui_MainWindow import *
import sys
import os
from utils import get_size, set_local_sizes, set_cloud_sizes
from os.path import expanduser
import resources # Mantener
import drive
import backup
import re
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog,
    QMenu,
    QAction, 
    QTableWidgetItem, 
    QPushButton, 
    QScrollBar, 
    QWidget,
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
        self.setFixedSize(812,706)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))
        
        # Getting an instance of json_handler
        json_data = json_handler()
        array = json_data.get_list("DIRECTORIES")
        # Setting values to ListView
        for route in array:
            self.list_Paths.addItem(route)
        # Setting values to labels
        self.update_local_size()
        self.update_cloud_size()
        # Setting value to backup progress bar
        self.pr_backup.setValue(0)
        # Automatic Backup
        self.set_values_automatic_backup(json_data)
        # Compress checkbox
        self.chk_compress.setChecked(json_data.get_list("DRIVE","COMPRESS"))
        
        # Event handlers
        self.list_Paths.customContextMenuRequested.connect(self.modifyItem)
        # Enable automatic
        self.chk_automatic.toggled.connect(self.automatic)
        # Backup
        self.bt_backup.clicked.connect(self.backup_thread)
        # Compress handler
        self.chk_compress.toggled.connect(self.compress)
        
        # view handler
        self.link_auth.clicked.connect(self.startAuthWindow)
        self.bt_log_viewer.clicked.connect(self.startLogWindow)
        self.bt_options.clicked.connect(self.startOptionsWindow)
        self.bt_target.clicked.connect(self.select_path)
        self.bt_save_path.clicked.connect(self.save_path)
        self.bt_refresh.clicked.connect(lambda: set_cloud_sizes())
        self.bt_refresh.clicked.connect(self.update_cloud_size)

    def update_local_size(self):
        json_data = json_handler()
        # Setting values to labels
        self.lb_files.setText(json_data.get_list("SIZES", "LOCAL_FILES"))
        self.lb_folders.setText(json_data.get_list("SIZES", "LOCAL_FOLDERS"))
        self.lb_size.setText(json_data.get_list("SIZES", "LOCAL_SIZE"))
        
    def update_cloud_size(self):
        json_data = json_handler()
        # Cloud Size
        self.lb_used.setText(json_data.get_list("SIZES", "CLOUD_USED"))
        self.lb_free.setText(json_data.get_list("SIZES", "CLOUD_FREE"))
        self.lb_total.setText(json_data.get_list("SIZES", "CLOUD_TOTAL"))
        self.pr_size.setMinimum(0)
        self.pr_size.setMaximum(100)
        self.pr_size.setValue(json_data.get_list("SIZES", "CLOUD_PERCENT"))
        
    def set_values_automatic_backup(self, json_data):
        state_auto = json_data.get_list("DRIVE","AUTO_BACKUP")
        self.chk_automatic.setChecked(state_auto)
        self.sp_day.setEnabled(state_auto)
        self.sp_day.setValue(json_data.get_list("TIMES","DAY"))
        self.sp_hour.setEnabled(state_auto)
        self.sp_hour.setValue(json_data.get_list("TIMES","HOUR"))
        self.sp_month.setEnabled(state_auto)
        self.sp_month.setValue(json_data.get_list("TIMES","MONTH"))
        self.bt_save_dates.setEnabled(state_auto) 
        
    def automatic(self):
        json_data = json_handler()
        state = True
        if not self.chk_automatic.isChecked():
           state = False
        self.sp_day.setEnabled(state)
        self.sp_hour.setEnabled(state)
        self.sp_month.setEnabled(state)
        self.bt_save_dates.setEnabled(state)
        json_data.write_field("DRIVE",state,"AUTO_BACKUP")
        
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
        self.hide()# hide this window
        self.ui = AuthWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startLogWindow(self):
        self.hide()# hide this window
        self.ui = LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startOptionsWindow(self):
        self.hide()# hide this window
        self.ui = OptionsWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
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
                    QMessageBox.warning(self, "Warning", "The directory or file already exists")
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
        
        if not self.valid_path(paths):
            QMessageBox.information(self, "Warning", "Select a correct path")   
        elif paths and self.not_exists_path(paths):
            for p in paths:
                self.list_Paths.addItem(p)           
                json_data = json_handler()
                json_data.add_field_list("DIRECTORIES",p)
                #Update local sizes
                set_local_sizes()
                self.update_local_size()
            QMessageBox.information(self, "Info", "Paths saved")
        else:
            QMessageBox.information(self, "Info", "Select a path that doesn't exists")   
            
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
        json_data.write_field("DRIVE",state,"COMPRESS")  
            
    def backup_thread(self):
        # Initial actions
        self.update_progress(0)
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots 
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress)
        self.worker.blk.connect(self.show_problems)
        # Start the thread
        try:
            self.thread.start()
        except Exception as e:
            logger.error(str(e))
            QMessageBox.error(self, "Error", "Problems with your files")
        finally:
            # Final actions
            self.bt_backup.setEnabled(False)

    def update_progress(self, progress):
        self.pr_backup.setValue(progress)
        self.bt_backup.setEnabled(progress == 100)
        
    def show_problems(self, output):
        if  not output:
            self.bt_backup.setEnabled(True)
            QMessageBox.warning(self, "Warning", "You need to be authenticated")
            
    """Function to generate a file explorer"""
    def getOpenFilesAndDirs(self, parent=None, caption='', directory='', 
                            filter='', initialFilter='', options=None):
        def updateText():
            # update the contents of the line edit widget with the selected files
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

        # by default, if a directory is opened in file listing mode,
        # QFileDialog.accept() shows the contents of that directory, but we 
        # need to be able to "open" directories as we can do with files, so we 
        # just override accept() with the default QDialog implementation which 
        # will just return exec_()
        dialog.accept = lambda: QtWidgets.QDialog.accept(dialog)

        # there are many item views in a non-native dialog, but the ones displaying 
        # the actual contents are created inside a QStackedWidget; they are a 
        # QTreeView and a QListView, and the tree is only used when the 
        # viewMode is set to QFileDialog.Details, which is not this case
        stackedWidget = dialog.findChild(QtWidgets.QStackedWidget)
        view = stackedWidget.findChild(QtWidgets.QListView)
        view.selectionModel().selectionChanged.connect(updateText)

        lineEdit = dialog.findChild(QtWidgets.QLineEdit)
        # clear the line edit contents whenever the current directory changes
        dialog.directoryEntered.connect(lambda: lineEdit.setText(''))

        dialog.exec_()
        return dialog.selectedFiles()

class AuthWindow(QtWidgets.QMainWindow, Ui_AuthWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_AuthWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)

        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_drive.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.startLogWindow)
        self.bt_options.clicked.connect(self.startOptionsWindow)
        self.bt_save_cred.clicked.connect(self.save_cred)
        
        
    def save_cred(self):
        cred = drive.get_credentials(self.lb_code.toPlainText()) # Return a boolean

        if cred:
            QMessageBox.information(self, "Info", "Credentials saved")
            json_data = json_handler()
            json_data.write_field("DRIVE",True,"AUTHENTICATED")
        else:
            QMessageBox.information(self, "Info", "Invalid credentials")
    
    def backToMain(self):
        self.hide()# hide this window
        self.ui = MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startLogWindow(self):
        self.hide()# hide this window
        self.ui = LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startOptionsWindow(self):
        self.hide()# hide this window
        self.ui = OptionsWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
class LogWindow(QtWidgets.QMainWindow, Ui_LogWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_LogWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))
        
        # add items
        with open('log/message.log','r') as logg:
            for entry in logg:
                self.list_log.addItem(entry)
        
        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.reload)
        self.bt_drive.clicked.connect(self.backToMain)
        self.bt_options.clicked.connect(self.startOptionsWindow)
        
    def reload(self):
        self.hide()# hide this window
        self.ui = LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def backToMain(self):
        self.hide()# hide this window
        self.ui = MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startOptionsWindow(self):
        self.hide()# hide this window
        self.ui = OptionsWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
class OptionsWindow(QtWidgets.QMainWindow, Ui_OptionsWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_OptionsWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))
        
        #Getting a instance of json_handler
        json_data = json_handler()
        #Setting values
        state_auto = json_data.get_list("OPTIONS","DELETE_BACKUP")
        self.chk_delete.setChecked(state_auto)
        self.sp_number.setEnabled(state_auto)
        self.bt_number_backups.setEnabled(state_auto)
        self.sp_number.setValue(json_data.get_list("OPTIONS","NUM_BACKUP"))
        
        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.reload)
        self.bt_drive.clicked.connect(self.backToMain)
        # Enable delete
        self.chk_delete.toggled.connect(self.delete_toggle)
        self.bt_number_backups.clicked.connect(self.save_backups)
    
    def delete_toggle(self):
        json_data = json_handler()
        state = True
        if not self.chk_delete.isChecked():
           state = False
        self.sp_number.setEnabled(state)
        self.bt_number_backups.setEnabled(state)
        json_data.write_field("OPTIONS",state,"DELETE_BACKUP")
        
    def save_backups(self):
        json_data = json_handler()
        json_data.write_field("OPTIONS",int(self.sp_number.text()),"NUM_BACKUP")
        QMessageBox.information(self, "Info", "Backup options saved")
    
    def reload(self):
        self.hide()# hide this window
        self.ui = LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def backToMain(self):
        self.hide()# hide this window
        self.ui = MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    blk = pyqtSignal(bool)

    def run(self):

        output = backup.recompile(self.update_progress)
        self.blk.emit(output)
        self.finished.emit()
        
    def update_progress(self, percent):
        self.progress.emit(percent)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # AUTH_status
    drive.auth_status()
    #Set sizes in json config file
    set_local_sizes()
    set_cloud_sizes()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())