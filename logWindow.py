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
        with open('log/message.log','r') as logg:
            lines = reversed(logg.readlines())
            for entry in lines:
                widgitItem = QtWidgets.QListWidgetItem() 
                widget = QtWidgets.QWidget()
                
                if "INFO" in entry:
                    entry = entry.split("INFO")
                    widgetText =  QtWidgets.QLabel(entry[0] + '<span style="color:#00ff00;">INFO</span>'+ entry[1])
                elif "WARNING" in entry:
                    entry = entry.split("WARNING")
                    widgetText =  QtWidgets.QLabel(entry[0] + '<span style="color:#ff6700;">WARNING</span>'+ entry[1])
                elif "ERROR" in entry:
                    entry = entry.split("ERROR")
                    widgetText =  QtWidgets.QLabel(entry[0] + '<span style="color:#ff0000;">ERROR</span>'+ entry[1])    
                else:
                    widgetText =  QtWidgets.QLabel(entry)
                    
                widgetLayout = QtWidgets.QHBoxLayout()
                widgetLayout.addWidget(widgetText)
                widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widgetLayout)      
                self.list_log.addItem(widgitItem)
                widgitItem.setSizeHint(widget.sizeHint())
                self.list_log.setItemWidget(widgitItem, widget)
        
        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.reload)
        self.bt_drive.clicked.connect(self.backToMain)
        self.bt_options.clicked.connect(self.startOptionsWindow)
        self.bt_clear.clicked.connect(lambda:[open('log/message.log', 'w').close(), self.reload()])
        
    def reload(self):
        self.hide()
        self.ui = LogWindow()
        self.ui.show()
        
    def backToMain(self):
        self.hide()
        self.ui = handler.MainWindow()
        self.ui.show()
        
    def startOptionsWindow(self):
        self.hide()
        self.ui = optionsWindow.OptionsWindow()
        self.ui.show()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec_())
        