from json_handler import json_handler
from logging import exception
from ui_OptionsWindow import Ui_OptionsWindow
from ui_LogWindow import Ui_LogWindow
from ui_AuthWindow import Ui_AuthWindow
from PyQt5.QtCore import QEvent, QModelIndex, QPoint
from PyQt5.QtWidgets import QFileDialog, QAction, QTableWidgetItem, QPushButton, QScrollBar, QWidget, QMessageBox
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.uic.properties import QtWidgets
from ui_MainWindow import *
from PyQt5.QtWidgets import *
from qtpy.QtWidgets import QApplication, QWidget
import sys
import os
from utils import get_size
from os.path import expanduser
import resources
from PyQt5.Qt import QUrl, QDesktopServices
import drive
import backup
import re

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Class to relate the functions of the lower layers to the interface elements"""

    def __init__(self, *args, **kwargs):
        """Constructor that will be in charge of initializing the main components."""
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_MainWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(780,706)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))
        
        # AUTH_status
        drive.auth_status()
        
        # Set 0 by default
        self.pr_backup.setValue(0)
        
        # Getting an instance of json_handler
        json_data = json_handler()
        array = json_data.get_list("DIRECTORIES")
        # Setting values to ListView
        for route in array:
            self.list_Paths.addItem(route)
        # Setting values to labels
        self.update_sizes()
        
        # Compress checkbox
        self.chk_compress.setChecked(json_data.get_list("DRIVE","COMPRESS"))
        # Automatic Backup
        state_auto = json_data.get_list("DRIVE","AUTO_BACKUP")
        self.chk_automatic.setChecked(state_auto)
        self.sp_day.setEnabled(state_auto)
        self.sp_day.setValue(json_data.get_list("TIMES","DAY"))
        self.sp_hour.setEnabled(state_auto)
        self.sp_hour.setValue(json_data.get_list("TIMES","HOUR"))
        self.sp_month.setEnabled(state_auto)
        self.sp_month.setValue(json_data.get_list("TIMES","MONTH"))
        self.bt_save_dates.setEnabled(state_auto) 
        
        # Event handlers
        self.list_Paths.customContextMenuRequested.connect(self.editItem)
        # Enable automatic
        self.chk_automatic.toggled.connect(self.automatic)
        # Backup
        self.bt_backup.clicked.connect(self.backup)
    
        # view handler
        self.link_auth.clicked.connect(self.startAuthWindow)
        self.bt_log_viewer.clicked.connect(self.startLogWindow)
        self.bt_options.clicked.connect(self.startOptionsWindow)
        self.bt_target.clicked.connect(self.select_path)
        self.bt_save_path.clicked.connect(self.save_path)
 

    def update_sizes(self):
        # Setting values to labels
        size, num_files, num_folders = get_size()
        self.lb_files.setText(num_files)
        self.lb_folders.setText(num_folders)
        self.lb_size.setText(size)
        # Cloud Size
        used, free, total, percent = drive.get_size()
        self.lb_used.setText(used)
        self.lb_free.setText(free)
        self.lb_total.setText(total)
        self.pr_size.setMinimum(0)
        self.pr_size.setMaximum(100)
        self.pr_size.setValue(percent)
        
    def backup(self):
        output = backup.recompile(self.chk_compress.isChecked())
        if not output:
            QMessageBox.warning(self, "Warning", "You need to be authenticated")
        else:
            QMessageBox.information(self, "Info", "Backup Completed")
        
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
        
    def editItem(self, item):
        #QMessageBox.information(self, "Info", item.text())
        if(self.list_Paths.itemAt(item)):
            contextMenu = QMenu(self)
            editAct = contextMenu.addAction("Edit")
            deleteAct = contextMenu.addAction("Delete")
            action = contextMenu.exec_(QtGui.QCursor().pos())
            if action == editAct:
                file = self.select_path()
                print(file)
                if file and self.not_exists_path(file):
                    self.list_Paths.currentItem().setText(os.path.normpath(file))
                    json_data = json_handler()
                    json_data.edit_field_list("DIRECTORIES", self.list_Paths.row(self.list_Paths.itemAt(item)), os.path.normpath(file))
                    self.update_sizes()
                elif not file:
                    return None
                else:
                    QMessageBox.warning(self, "Warning", "The directory or file already exists")  
            if action == deleteAct:
                self.list_Paths.takeItem(self.list_Paths.currentRow())
                json_data = json_handler()
                json_data.remove_field_list("DIRECTORIES",self.list_Paths.row(self.list_Paths.itemAt(item)))
                self.update_sizes()
                
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
    def select_path(self):
        """Function to select de path of the file"""
        try:
            button = self.sender()
            
            if button:
                file = QFileDialog.getExistingDirectory(self, "Folder to backup", expanduser("~"))
                
                if not self.valid_path(file):
                    return None
                elif self.not_exists_path(file):
                    print("Path selected: ", file)
                    self.lb_path.setPlainText(os.path.normpath(file))
                    return file
                else:
                    QMessageBox.warning(self, "Warning", "The directory or file already exists")
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Path of the file not valid")
            msg.setWindowTitle("Error")
            msg.exec_()
            return None    
    
    def save_path(self):
        path = os.path.normpath(self.lb_path.toPlainText())
        
        if not self.valid_path(path):
            QMessageBox.information(self, "Warning", "Select a correct path folder")   
        elif path and self.not_exists_path(path):
            self.list_Paths.addItem(path)           
            json_data = json_handler()
            json_data.add_field_list("DIRECTORIES",path)
            self.update_sizes()
            QMessageBox.information(self, "Info", "Path saved")
        else:
            QMessageBox.information(self, "Info", "Select a path folder that doesn't exists")   
            
    def not_exists_path(self,path):
        notExists = True
        for i in range(self.list_Paths.count()):
            if self.list_Paths.item(i).text() == os.path.normpath(path):
                notExists = False
        return notExists
    
    def valid_path(self,path):
        valid = True
        if re.match("/^$|\s+/|\.+",path) or not os.path.isdir(path):
            valid = False
        return valid

class AuthWindow(QtWidgets.QMainWindow, Ui_AuthWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_AuthWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(780,706)
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
        self.setFixedSize(780,706)
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
        self.setFixedSize(780,706)
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())