from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QFileDialog, QAction, QTableWidgetItem, QPushButton, QScrollBar, QWidget, QMessageBox
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.uic.properties import QtWidgets
from ui_MainWindow import *
from qtpy.QtWidgets import QApplication, QWidget
import sys
import resources


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Clase para relacionar las funciones de la capas inferiores con los elementos de la interfaz"""

    def __init__(self, *args, **kwargs):
        """Constructor que se encargara de inicializar los componentes principales"""
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setFixedSize(830,660)
        # Set 0 by default
        self.lb_files.setText("0")
        self.lb_folders.setText("0")
        self.lb_size.setText("0")
        # Añadir items
        self.list_Paths.addItem("Item 1")
        self.list_Paths.addItem("Item 2")
        self.list_Paths.addItem("Item 3")

        qss_file = open('theme.qss').read()
        app.setStyleSheet(qss_file)
        app.setWindowIcon(QIcon("Resources/icon.png"))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

