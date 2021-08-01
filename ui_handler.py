from json_handler import json_handler
from logging import exception
from ui_OptionsWindow import Ui_OptionsWindow
from ui_LogWindow import Ui_LogWindow
from ui_AuthWindow import Ui_AuthWindow
from PyQt5.QtCore import QModelIndex
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
import drive,json
import backup

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
        
        # Set 0 by default
        self.lb_files.setText("0")
        self.lb_folders.setText("0")
        self.lb_size.setText("0")
        self.pr_size.setValue(0)
        self.pr_backup.setValue(0)
        
        # Add items
        json_data = json.load(open('config.json', 'r'))
        lista = list(json_data["DIRECTORIES"])
        for ruta in lista:
            self.list_Paths.addItem(ruta)
        
        size = get_size()
        self.lb_size.setText(size)
        
        
        # Event handlers
        self.list_Paths.itemDoubleClicked.connect(self.editItem)
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
        
    def backup(self):
        backup.recompile(self.chk_compress.isChecked())
        
    def automatic(self):
        state = True
        if not self.chk_automatic.isChecked():
           state = False
        self.sp_day.setEnabled(state)
        self.sp_hour.setEnabled(state)
        self.sp_month.setEnabled(state)
        self.bt_save_dates.setEnabled(state)  
        
    def editItem(self, item):
        #QMessageBox.information(self, "Info", item.text())
        self.lb_path.setText(os.path.normpath(item.text()))
        info = item.text()
        self.bt_save_path.clicked.connect(self.modifyItem)
        
    def modifyItem(self):
        QMessageBox.information(self, "Info", self.lb_path.toPlainText())
        
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
                print("Path selected: ", file)
                self.lb_path.setPlainText(os.path.normpath(file))
                return file
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Path of the file not valid")
            msg.setWindowTitle("Error")
            msg.exec_()
            return None    
    
    def save_path(self):
        path = os.path.normpath(self.lb_path.toPlainText())
        
        if path:
            self.list_Paths.addItem(path)           
            json_data = json_handler()
            json_data.add_field_list("DIRECTORIES",path)
            size = get_size()
            self.lb_size.setText(size)
            QMessageBox.information(self, "Info", "Path saved")
        else:
            QMessageBox.information(self, "Info", "Select a path folder")   


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
        
        
        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.reload)
        self.bt_drive.clicked.connect(self.backToMain)
        
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