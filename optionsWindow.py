from Sources.json_handler import json_handler
from UI.ui_OptionsWindow import Ui_OptionsWindow
from UI.ui_MainWindow import *
import logWindow
import handler
import Sources.drive as drive
from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from logger_settings import logger

class OptionsWindow(QtWidgets.QMainWindow, Ui_OptionsWindow):
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_OptionsWindow.__init__(self)
        self.init_ui()
        
    def init_ui(self):
        self.setupUi(self)
        self.setFixedSize(812,706)
        #Setting values
        self.set_backup_options()
        # view handler
        self.bt_back.clicked.connect(self.backToMain)
        self.bt_log_viewer.clicked.connect(self.reload)
        self.bt_drive.clicked.connect(self.backToMain)
        # Enable local delete backups
        self.chk_delete_local.toggled.connect(self.delete_toggle_local)
        self.bt_number_backups_local.clicked.connect(self.save_backups_local)
        # Disable/Enabled download button in function of authenticated
        json_data = json_handler()
        self.bt_download.setEnabled(json_data.get_list("DRIVE","AUTHENTICATED"))
        # Enable cloud delete backups 
        self.chk_delete_cloud.toggled.connect(self.delete_toggle_cloud)
        self.bt_number_backups_cloud.clicked.connect(self.save_backups_cloud)
        # Handlers
        self.bt_download.clicked.connect(self.download_dialog)
    
    def set_backup_options(self):
        json_data = json_handler()
        # Local
        state_auto_local = json_data.get_list("OPTIONS","DELETE_BACKUP_LOCAL")
        self.chk_delete_local.setChecked(state_auto_local)
        self.sp_number_local.setEnabled(state_auto_local)
        self.bt_number_backups_local.setEnabled(state_auto_local)
        self.sp_number_local.setValue(json_data.get_list("OPTIONS","NUM_BACKUP_LOCAL"))
        # Cloud
        state_auto_cloud = json_data.get_list("OPTIONS","DELETE_BACKUP_CLOUD")
        self.chk_delete_cloud.setChecked(state_auto_cloud)
        self.sp_number_cloud.setEnabled(state_auto_cloud)
        self.bt_number_backups_cloud.setEnabled(state_auto_cloud)
        self.sp_number_cloud.setValue(json_data.get_list("OPTIONS","NUM_BACKUP_CLOUD"))
    
    def delete_toggle_local(self):
        json_data = json_handler()
        state = True
        if not self.chk_delete_local.isChecked():
           state = False
        self.sp_number_local.setEnabled(state)
        self.bt_number_backups_local.setEnabled(state)
        json_data.write_field("OPTIONS",state,"DELETE_BACKUP_LOCAL")
        
    def save_backups_local(self):
        json_data = json_handler()
        json_data.write_field("OPTIONS",int(self.sp_number_local.text()),"NUM_BACKUP_LOCAL")
        QMessageBox.information(self, "Info", "Local backup options saved")
        
    def delete_toggle_cloud(self):
        json_data = json_handler()
        state = True
        if not self.chk_delete_cloud.isChecked():
           state = False
        self.sp_number_cloud.setEnabled(state)
        self.bt_number_backups_cloud.setEnabled(state)
        json_data.write_field("OPTIONS",state,"DELETE_BACKUP_CLOUD")
        
    def save_backups_cloud(self):
        json_data = json_handler()
        json_data.write_field("OPTIONS",int(self.sp_number_cloud.text()),"NUM_BACKUP_CLOUD")
        QMessageBox.information(self, "Info", "Cloud backup options saved")
    
    def reload(self):
        self.hide()
        self.ui = logWindow.LogWindow()
        self.ui.show()
        
    def backToMain(self):
        self.hide()
        self.ui = handler.MainWindow()
        self.ui.show()

    def download_dialog(self): 
        self.dialog = Download_Backup(self)
        self.dialog.show()

class Download_Backup(QDialog):

    def __init__(self, *args, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)
        self.init_ui()
        
    def init_ui(self):
        self.setObjectName("Download Backups")
        self.setFixedSize(400, 322)
        #self.setFixedSize(400, 300)
        self.list_backups = QtWidgets.QListWidget(self)
        self.list_backups.setGeometry(QtCore.QRect(70, 20, 256, 192))
        self.list_backups.setObjectName("list_backups")
        self.bt_download = QtWidgets.QPushButton(self)
        self.bt_download.setGeometry(QtCore.QRect(160, 240, 75, 23))
        self.bt_download.setObjectName("bt_download")
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.pr_download = QtWidgets.QProgressBar(self)
        self.pr_download.setGeometry(QtCore.QRect(140, 280, 112, 23))
        self.pr_download.setProperty("value", 0)
        self.pr_download.setObjectName("pr_download")
        self.chk_unzip = QtWidgets.QCheckBox(self)
        self.chk_unzip.setGeometry(QtCore.QRect(320, 240, 51, 21))
        self.chk_unzip.setObjectName("chk_unzip")
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.chk_unzip.setPalette(palette)
        self.chk_unzip.setText("Unzip")

        # Data
        json_data = json_handler()
        self.chk_unzip.setChecked(json_data.get_list("OPTIONS", "UNZIP"))
        files = drive.get_files(False)
        # Load the data into the list
        if files: [self.list_backups.addItem(name) for name in files.keys()]
        # Handlers
        self.bt_download.clicked.connect(lambda: self.download_thread(files))
        self.chk_unzip.toggled.connect(self.unzip)

    def unzip(self):
        json_data = json_handler()
        state = True
        if not self.chk_unzip.isChecked():
           state = False
        json_data.write_field("OPTIONS", state, "UNZIP")
        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Download Backups"))
        self.bt_download.setText(_translate("Dialog", "Download"))
        
    def download_thread(self, files):
        # Initial actions
        
        # If there's no backup selected, no actions will be executed
        try:
            if self.list_backups.selectedItems():
                filename = self.list_backups.currentItem().text()
            else:
                QMessageBox.warning(self, "Warning", "Select a item to donwload")
                return False
        except:
            return False
        
        self.update_progress(0)
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.worker.error.connect(self.show_error)
        self.thread.started.connect(lambda: self.worker.run(files[filename], filename))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.blk.connect(self.show_problems)
        self.worker.progress.connect(self.update_progress)
        # Start the thread
        self.thread.start()

    def update_progress(self, progress):
        self.pr_download.setValue(progress)
        self.bt_download.setEnabled(progress == 100 or progress == 0)
    
    def show_problems(self, output):
        if not output:
            self.bt_download.setEnabled(True)
            QMessageBox.warning(
                self, "Warning", "You need to be authenticated")
    def show_error(self):
        QMessageBox.warning(
                self, "Warning", "The backup you are trying to download already exist")
    
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    blk = pyqtSignal(bool)
    error = pyqtSignal()

    def run(self, file_id, filename):
        try:
            out = drive.download_drive(file_id, filename, self.update_progress)
            self.blk.emit(out)
            self.finished.emit()
        except Exception as e:
            self.error.emit()
            print(e)
            logger.error(e)
            self.progress.emit(0)
            self.finished.emit()

    def update_progress(self, percent):
        self.progress.emit(percent)       