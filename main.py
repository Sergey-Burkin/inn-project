from PyQt5 import QtCore, QtGui, QtWidgets
from ui.window import Window

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
