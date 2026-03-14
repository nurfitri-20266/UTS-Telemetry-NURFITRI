import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
from datetime import datetime


class SerialThread(QThread):

    data_received = pyqtSignal(str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True

    def run(self):

        try:
            ser = serial.Serial(self.port,115200)
        except:
            return

        while self.running:

            if ser.in_waiting:

                data = ser.readline().decode(errors="ignore").strip()

                if data:
                    self.data_received.emit(data)


class TelemetryGUI(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("LoRa Telemetry Dashboard")
        self.setGeometry(100,100,1400,800)

        self.tempData=[]
        self.humData=[]
        self.soilData=[]
        self.lightData=[]

        self.initUI()


    def initUI(self):

        mainLayout=QVBoxLayout()

        # ================= TOP BAR =================

        topLayout=QHBoxLayout()

        self.portBox=QComboBox()
        self.refreshPorts()

        refreshBtn=QPushButton("Refresh")
        refreshBtn.clicked.connect(self.refreshPorts)

        connectBtn=QPushButton("Connect")
        connectBtn.clicked.connect(self.connectSerial)

        topLayout.addWidget(QLabel("COM Port"))
        topLayout.addWidget(self.portBox)
        topLayout.addWidget(refreshBtn)
        topLayout.addWidget(connectBtn)

        mainLayout.addLayout(topLayout)

        # ================= SENSOR BOX =================

        sensorLayout=QHBoxLayout()

        self.tempBox=self.createSensorBox("Temperature")
        self.humBox=self.createSensorBox("Humidity")
        self.soilBox=self.createSensorBox("Soil")
        self.lightBox=self.createSensorBox("Light")
        self.rssiBox=self.createSensorBox("RSSI")

        sensorLayout.addWidget(self.tempBox)
        sensorLayout.addWidget(self.humBox)
        sensorLayout.addWidget(self.soilBox)
        sensorLayout.addWidget(self.lightBox)
        sensorLayout.addWidget(self.rssiBox)

        mainLayout.addLayout(sensorLayout)

        # ================= GRAPH =================

        graphLayout=QGridLayout()

        self.tempGraph=self.createGraph("Temperature","#ef4444")
        self.humGraph=self.createGraph("Humidity","#3b82f6")
        self.soilGraph=self.createGraph("Soil","#22c55e")
        self.lightGraph=self.createGraph("Light","#facc15")

        graphLayout.addWidget(self.tempGraph[0],0,0)
        graphLayout.addWidget(self.humGraph[0],0,1)
        graphLayout.addWidget(self.soilGraph[0],1,0)
        graphLayout.addWidget(self.lightGraph[0],1,1)

        mainLayout.addLayout(graphLayout)

        # ================= TABLE =================

        self.table=QTableWidget()
        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "Time","Temp","Humidity","Soil","Light","RSSI"
        ])

        mainLayout.addWidget(self.table)

        widget=QWidget()
        widget.setLayout(mainLayout)

        self.setCentralWidget(widget)

        # ================= STYLE =================

        self.setStyleSheet("""

        QMainWindow{
            background-color:#0f172a;
        }

        QLabel{
            color:white;
            font-size:14px;
        }

        QGroupBox{
            background-color:#1e293b;
            border-radius:10px;
            border:1px solid #334155;
            margin-top:10px;
            font-weight:bold;
            color:#e2e8f0;
        }

        QGroupBox::title{
            subcontrol-origin: margin;
            left:10px;
            padding:0 5px 0 5px;
        }

        QPushButton{
            background-color:#3b82f6;
            color:white;
            border:none;
            border-radius:6px;
            padding:6px 14px;
            font-weight:bold;
        }

        QPushButton:hover{
            background-color:#2563eb;
        }

        QComboBox{
            background-color:#1e293b;
            color:white;
            border:1px solid #334155;
            border-radius:5px;
            padding:4px;
        }

        QTableWidget{
            background-color:#1e293b;
            color:white;
            gridline-color:#334155;
            border-radius:6px;
        }

        QHeaderView::section{
            background-color:#334155;
            color:white;
            padding:5px;
            border:none;
        }

        """)


    def createSensorBox(self,title):

        box=QGroupBox(title)

        layout=QVBoxLayout()

        label=QLabel("--")
        label.setAlignment(Qt.AlignCenter)

        label.setStyleSheet("""
        font-size:32px;
        font-weight:bold;
        color:#38bdf8;
        """)

        layout.addWidget(label)

        box.setLayout(layout)

        box.value=label

        return box


    def createGraph(self,title,color):

        graph=pg.PlotWidget()

        graph.setBackground('#1e293b')

        graph.setTitle(title,color='w',size='12pt')

        graph.showGrid(x=True,y=True,alpha=0.3)

        pen=pg.mkPen(color,width=3)

        curve=graph.plot(pen=pen)

        return graph,curve


    def refreshPorts(self):

        self.portBox.clear()

        ports=serial.tools.list_ports.comports()

        for port in ports:
            self.portBox.addItem(port.device)


    def connectSerial(self):

        port=self.portBox.currentText()

        self.thread=SerialThread(port)

        self.thread.data_received.connect(self.processData)

        self.thread.start()


    def processData(self,data):

        try:

            # ===== SENSOR DATA =====

            if "TEMP=" in data:

                parts=data.split(";")

                temp=float(parts[0].split("=")[1])
                hum=float(parts[1].split("=")[1])
                soil=int(parts[2].split("=")[1])
                light=int(parts[3].split("=")[1])

                self.tempBox.value.setText(str(temp))
                self.humBox.value.setText(str(hum))
                self.soilBox.value.setText(str(soil))
                self.lightBox.value.setText(str(light))

                self.tempData.append(temp)
                self.humData.append(hum)
                self.soilData.append(soil)
                self.lightData.append(light)

                if len(self.tempData)>50:

                    self.tempData.pop(0)
                    self.humData.pop(0)
                    self.soilData.pop(0)
                    self.lightData.pop(0)

                self.tempGraph[1].setData(self.tempData)
                self.humGraph[1].setData(self.humData)
                self.soilGraph[1].setData(self.soilData)
                self.lightGraph[1].setData(self.lightData)

                time=datetime.now().strftime("%H:%M:%S")

                row=self.table.rowCount()

                self.table.insertRow(row)

                self.table.setItem(row,0,QTableWidgetItem(time))
                self.table.setItem(row,1,QTableWidgetItem(str(temp)))
                self.table.setItem(row,2,QTableWidgetItem(str(hum)))
                self.table.setItem(row,3,QTableWidgetItem(str(soil)))
                self.table.setItem(row,4,QTableWidgetItem(str(light)))


            # ===== RSSI =====

            if "RSSI" in data:

                rssi=data.split(":")[1].strip()

                self.rssiBox.value.setText(rssi)

                row=self.table.rowCount()-1

                if row>=0:
                    self.table.setItem(row,5,QTableWidgetItem(rssi))

        except Exception as e:

            print("Parse error:",e)



app=QApplication(sys.argv)

window=TelemetryGUI()

window.show()

sys.exit(app.exec_())