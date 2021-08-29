from UI.ui_LogWindow import Ui_LogWindow
from UI.ui_MainWindow import *
import handler
import optionsWindow
import sys
class LogWindow(QtWidgets.QMainWindow, Ui_LogWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_LogWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)
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
        self.ui = handler.MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def startOptionsWindow(self):
        self.hide()# hide this window
        self.ui = optionsWindow.OptionsWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec_())
        