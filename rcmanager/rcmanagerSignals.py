
from PyQt4 import QtCore

class RCManagerSignals(QtCore.QObject):

    sample = QtCore.pyqtSignal()
    modelIsReady = QtCore.pyqtSignal()
    viewerIsReady = QtCore.pyqtSignal()
    controllerIsReady = QtCore.pyqtSignal()
    addNode = QtCore.pyqtSignal(dict)
    startComponent = QtCore.pyqtSignal(str)
    stopComponent = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)
