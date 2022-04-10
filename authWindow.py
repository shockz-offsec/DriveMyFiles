from Sources.json_handler import json_handler
from UI.ui_AuthWindow import Ui_AuthWindow
from UI.ui_MainWindow import *
import logWindow
import optionsWindow
import handler
import Sources.drive as drive
from PyQt5.QtWidgets import (
    QMessageBox
)
class AuthWindow(QtWidgets.QMainWindow, Ui_AuthWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_AuthWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)

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
            # Cloud sizes update
            self.ui = handler.MainWindow()
            self.ui.check_cloud_changes()
        else:
            QMessageBox.information(self, "Info", "Invalid credentials")
    
    def backToMain(self):
        self.hide()
        self.ui = handler.MainWindow()
        self.ui.show()
        
    def startLogWindow(self):
        self.hide()
        self.ui = logWindow.LogWindow()
        self.ui.show()
        
    def startOptionsWindow(self):
        self.hide()
        self.ui = optionsWindow.OptionsWindow()
        self.ui.show()
        

