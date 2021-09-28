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
        self.hide()# hide this window
        self.ui = logWindow.LogWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window
        
    def backToMain(self):
        self.hide()# hide this window
        self.ui = handler.MainWindow()# Change to the auth window
        self.ui.show()# is displayed via auth window

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
        self.bt_cancel = QtWidgets.QPushButton(self)
        self.bt_cancel.setGeometry(QtCore.QRect(280, 280, 21, 23))
        self.bt_cancel.setText("")
        self.bt_cancel.setObjectName("bt_cancel")
        self.bt_cancel.setStyleSheet("image: url(:/DriveMyFiles/Resources/error.ico);")
        # Data
        json_data = json_handler()
        self.chk_unzip.setChecked(json_data.get_list("OPTIONS", "UNZIP"))
        files = drive.get_files()
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
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.bt_download.setText(_translate("Dialog", "Download"))
        
    def download_thread(self, files):
        # Initial actions
        filename = self.list_backups.currentItem().text()
        self.update_progress(0)
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(lambda: self.worker.run(files[filename], filename))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress)
        #self.bt_cancel.clicked.connect(self.worker.stop)
        # Start the thread
        self.thread.start()

    def update_progress(self, progress):
        self.pr_download.setValue(progress)
        self.bt_download.setEnabled(progress == 100 or progress == 0)
    
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self, file_id, filename):
        try:
            drive.download_drive(file_id, filename, self.update_progress)
            self.finished.emit()
        except (OSError, IndexError, FileNotFoundError) as e:
            self.status.emit("Problems downloading the file or files",True)
            logger.error(e)
            self.progress.emit(0)
            self.finished.emit()

    def update_progress(self, percent):
        self.progress.emit(percent)       