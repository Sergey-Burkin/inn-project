from PyQt5 import QtCore, QtGui, QtWidgets
from ui.window import Window
import settings



if __name__ == "__main__":
    import sys
    settings.init()

    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
