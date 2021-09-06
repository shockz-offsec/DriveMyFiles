from Sources.json_handler import json_handler
from UI.ui_OptionsWindow import Ui_OptionsWindow
from UI.ui_MainWindow import *
import logWindow
import handler
from PyQt5.QtWidgets import (
    QMessageBox,
)

class OptionsWindow(QtWidgets.QMainWindow, Ui_OptionsWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_OptionsWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)
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
        self.ui = logWindow.LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def backToMain(self):
        self.hide()# hide this window
        self.ui = handler.MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
