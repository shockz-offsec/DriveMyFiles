from ui_log import Ui_LogWindow
from ui_AuthWindow import Ui_AuthWindow
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QFileDialog, QAction, QTableWidgetItem, QPushButton, QScrollBar, QWidget, QMessageBox
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.uic.properties import QtWidgets
from ui_MainWindow import *
from qtpy.QtWidgets import QApplication, QWidget
import sys
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
        self.setFixedSize(830,660)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))
        
        # Set 0 by default
        self.lb_files.setText("0")
        self.lb_folders.setText("0")
        self.lb_size.setText("0")
        # Add items
        json_data = json.load(open('config.json', 'r'))
        lista = list(json_data["DIRECTORIES"])
        for ruta in lista:
            self.list_Paths.addItem(ruta)
        
        # Event handlers
        self.list_Paths.itemDoubleClicked.connect(self.editItem)
        # Enable automatic
        self.chk_automatic.toggled.connect(self.automatic)
    
        # view handler
        self.link_auth.clicked.connect(self.startAuthWindow)
        self.bt_log_viewer.clicked.connect(self.startLogWindow)
        
        
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

        self.lb_path.setText(item.text())
        info = item.text()
        self.bt_save.clicked.connect(self.modifyItem)
        
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



class AuthWindow(QtWidgets.QMainWindow, Ui_AuthWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_AuthWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(830,660)
        # Theme
        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))
        
        
        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_drive.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.startLogWindow)
        
    def backToMain(self):
        self.hide()# hide this window
        self.ui = MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startLogWindow(self):
        self.hide()# hide this window
        self.ui = LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
class LogWindow(QtWidgets.QMainWindow, Ui_LogWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_LogWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(830,660)
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