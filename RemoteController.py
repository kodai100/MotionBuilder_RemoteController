import sys
import os
sys.path.append("D:\\work\\MotionBuilderDev\\RemoteController")

from PySide import QtGui, QtCore
from pyfbsdk import *
from pyfbsdk_additions import *
from Util.StoppableThread import *
from Util.UdpServer import *

class WaitDialog(QtGui.QDialog):

    def WaitSignal(self):
        while True:
            
            data, addr = self.server.sock.recvfrom(1024) # buffer size is 1024 bytes
            newTake = FBTake("S1_C24_Take1")
            
            FBSystem().Scene.Takes.append(newTake)
            FBSystem().CurrentTake=newTake
            
            if self.playerControl.Record(True, False):
                
                self.playerControl.GotoStart()
                self.playerControl.Play()
                self.label.setText("Playing !")
                self.label.setStyleSheet("QLabel{color:red;}")
                
            return

    def terminate(self):
        self.thread.stop()
        self.server.close()
        self.close()

    def stopButtonClicked(self):
        self.playerControl.Stop()
        self.terminate()

    def cancelButtonClicked(self):
        self.terminate()

    def closeEvent(self, event):
        self.terminate()

    def __init__(self, parent=None):

        super(WaitDialog, self).__init__(parent)

        self.server = UdpServer()
        self.playerControl = FBPlayerControl()
        self.label = QtGui.QLabel("Waiting...")
        self.label.setStyleSheet("QLabel{color:cyan;}")

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        stopButton = QtGui.QPushButton("Stop")
        stopButton.clicked.connect(self.stopButtonClicked)
        cancelButton = QtGui.QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancelButtonClicked)
        horizon = QtGui.QHBoxLayout()
        horizon.addWidget(stopButton)
        horizon.addWidget(cancelButton)
        layout.addLayout(horizon)

        self.setLayout(layout)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("UDP Start Trigger")
        self.resize(200, 100)
        self.setModal(True)
        self.show()
        self.raise_()

        QtGui.QApplication.processEvents()
        self.thread = StoppableThread(target=self.WaitSignal)
        self.thread.start()

app = WaitDialog()