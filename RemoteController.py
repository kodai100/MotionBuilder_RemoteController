import sys
import os
sys.path.append("D:\\work\\MotionBuilderDev\\RemoteController")

from PySide import QtGui, QtCore
from PySide import shiboken

from pyfbsdk import *
from pyfbsdk_additions import *

from Util.StoppableThread import *
from Util.UdpServer import *

import json
import traceback

class NativeWidgetHolder(FBWidgetHolder):
    def WidgetCreate(self, pWidgetParent):
        
        self.mNativeQtWidget = WaitDialog()
        
        return shiboken.getCppPointer(self.mNativeQtWidget)[0]

class NativeQtWidgetTool(FBTool):
    def BuildLayout(self):
        x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
        w = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
        h = FBAddRegionParam(0,FBAttachType.kFBAttachBottom,"")
        self.AddRegion("main","main", x, y, w, h)
        self.SetControl("main", self.mNativeWidgetHolder)
         
    def __init__(self, name):
        FBTool.__init__(self, name)
        self.mNativeWidgetHolder = NativeWidgetHolder()
        self.BuildLayout()
        self.StartSizeX = 200
        self.StartSizeY = 200

class WaitDialog(QtGui.QWidget):

    def WaitSignal(self):

        while True:
            
            data, addr = self.server.sock.recvfrom(1024) # buffer size is 1024 bytes
            
            try:
                decodedSignal = json.loads(str(data))
                
                if decodedSignal["signal"] == "player":
                    if decodedSignal["value"] == "record":
                        
                        if self.playerControl.Record(True, False):
                            self.play("Recording !")
                            
                    elif decodedSignal["value"] == "play":
                        self.play()

                    elif decodedSignal["value"] == "stop":
                        self.stopButtonClicked()

                elif decodedSignal["signal"] == "ready":
                    newTake = FBTake(decodedSignal["value"].encode())
                    FBSystem().Scene.Takes.append(newTake)
                    FBSystem().CurrentTake=newTake

            except Exception as e:
                t, v, tb = sys.exc_info()
                print traceback.format_exception(t,v,tb)
                
                continue
            

    def terminate(self):
        self.thread.stop()
        self.server.close()

    def stopButtonClicked(self):
        self.playerControl.Stop()
        self.label.setText("Ready ...")
        self.label.setStyleSheet("QLabel{color:cyan;}")

    def play(self, label="Playing !"):
        self.playerControl.GotoStart()
        self.playerControl.Play()
        self.label.setText(label)
        self.label.setStyleSheet("QLabel{color:red;}")

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

        horizon = QtGui.QHBoxLayout()
        horizon.addWidget(stopButton)

        layout.addLayout(horizon)

        self.setLayout(layout)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("UDP Start Trigger")

        QtGui.QApplication.processEvents()
        self.thread = StoppableThread(target=self.WaitSignal)
        self.thread.start()


gToolName = "Remote Controller"

gDEVELOPMENT = True

if gDEVELOPMENT:
    FBDestroyToolByName(gToolName)

if gToolName in FBToolList:
    tool = FBToolList[gToolName]
    ShowTool(tool)
else:
    tool=NativeQtWidgetTool(gToolName)
    
    FBAddTool(tool)
    
    if gDEVELOPMENT:
        ShowTool(tool)