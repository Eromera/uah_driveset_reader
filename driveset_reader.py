import numpy as np   #vector management
import time
import sys
import threading
from datetime import datetime
import imageio   #video reading and displaying

"""
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

"""

#from matplotlib import use
#use("Qt5Agg")	#necessary line to allow qt5agg
from PyQt5 import QtCore, QtGui, QtWidgets
#from PySide import QtCore, QtGui, QtWidgets

#Way not supported by pyinstaller:
#from PyQt5.QtCore import pyqtSignal, Qt, QCoreApplication
#from PyQt5.QtGui import QPixmap, QImage
#from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QSpinBox, QSlider, QPushButton, QLabel, QLayout, QFileDialog

#import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.figure import Figure
import matplotlib.ticker as plticker
#import matplotlib.animation as animation


fps = -1
videowidthShow = 960
videoheightShow = 540
activateExtraFigures = True

videoName = './20151030133104.mp4'
dataFolderName = './20151030133019'

videoCorrect = False
dataCorrect = False

currentSecond = 0
timeWindow = 30

class figureToPlot(QtWidgets.QVBoxLayout):

   def __init__(self,parent=None):
      super(figureToPlot, self).__init__(parent)

      #super(figureToPlot, self).__init__(None)
      #self.parent = parent

      # a figure instance to plot on
      self.figure = Figure(frameon=True)
      self.canvas = FigureCanvas(self.figure)
		
		#self.canvas.setParent(self)
      self.draw_thread = False
      self.pausePlot = False
      self.plotting = False
      self.semaforoPlot = False
      self.dataRestarted = False

      self.fileList = QtWidgets.QComboBox()		
      self.fileList.addItem("RAW_ACCELEROMETERS")
      self.fileList.addItem("RAW_GPS")
      self.fileList.addItem("PROC_LANE_DETECTION")
      self.fileList.addItem("PROC_VEHICLE_DETECTION")
      self.fileList.addItem("PROC_OPENSTREETMAP_DATA")
      self.fileList.setCurrentIndex(0)
      self.fileList.currentIndexChanged.connect(self.selectFileFromList)
      self.fileList.setFixedWidth(220)

      self.indexCol=1
      self.spinSelectCol = QtWidgets.QSpinBox()	
      self.spinSelectCol.valueChanged.connect(self.setIndexCol)
      self.spinSelectCol.setFixedWidth(45)

      self.columnInfo = QtWidgets.QLabel()

      self.hBoxFileCol = QtWidgets.QHBoxLayout()
      self.hBoxFileCol.addWidget(self.fileList)
      self.hBoxFileCol.addWidget(self.spinSelectCol)	
      self.hBoxFileCol.addWidget(self.columnInfo)	
		
      self.selectFileFromList()  #sets self.datafilename and calls loadData

      self.addLayout(self.hBoxFileCol)
      self.addWidget(self.canvas)

   def removeAll(self):
      self.fileList.deleteLater()
      self.spinSelectCol.deleteLater()
      self.hBoxFileCol.deleteLater()
      self.columnInfo.deleteLater()
      self.canvas.deleteLater()
      self.deleteLater()
		
   def loadData(self):
      try:
         self.data = np.genfromtxt(self.dataFileName, dtype=np.float, delimiter=' ')
         self.dataCorrect = True
         print (self.data.shape)
         self.spinSelectCol.setRange(1,self.data.shape[1]-1)
         self.setIndexCol()   #necessary to restart datax and datay
      except:
         self.dataCorrect = False
      print (self.dataCorrect)



   def selectFileFromList(self):
      dataFile = str(self.fileList.currentText() + '.txt')
      self.dataFileName = dataFolderName + '/' + dataFile
      self.loadData()	

   def setIndexCol(self):
      self.indexCol = self.spinSelectCol.value()
      if (self.dataCorrect):
         self.datax = self.data[:,0]
         self.datay = self.data[:,self.indexCol]
         self.dataRestarted = True
      self.setColumnInfo()

   def setColumnInfo(self):   #def info shown depending on index and file selected
      f = self.fileList.currentText()
      i = self.indexCol
      if (f == 'RAW_ACCELEROMETERS'):
         if (i == 1):
            self.columnInfo.setText('Activation bool (1 if speed>50Km/h)')
         elif (i == 2):
            self.columnInfo.setText('X acceleration (Gs)')
         elif (i == 3):
            self.columnInfo.setText('Y acceleration (Gs)')
         elif (i == 4):
            self.columnInfo.setText('Z acceleration (Gs)')
         elif (i == 5):
            self.columnInfo.setText('X accel filtered by KF (Gs)')
         elif (i == 6):
            self.columnInfo.setText('Y accel filtered by KF (Gs)')
         elif (i == 7):
            self.columnInfo.setText('Z accel filtered by KF (Gs)')
         elif (i == 8):
            self.columnInfo.setText('Roll (degrees)')
         elif (i == 9):
            self.columnInfo.setText('Pitch (degrees)')
         elif (i == 10):
            self.columnInfo.setText('Yaw (degrees)')
      elif (f == 'RAW_GPS'):
         if (i == 1):
            self.columnInfo.setText('Speed (Km/h)')
         elif (i == 2):
            self.columnInfo.setText('Latitude')
         elif (i == 3):
            self.columnInfo.setText('Longitude')
         elif (i == 4):
            self.columnInfo.setText('Altitude')
         elif (i == 5):
            self.columnInfo.setText('Vertical accuracy')
         elif (i == 6):
            self.columnInfo.setText('Horizontal accuracy')
         elif (i == 7):
            self.columnInfo.setText('Course (degrees)')
         elif (i == 8):
            self.columnInfo.setText('Difcourse: course variation')
         elif (i == 9):
            self.columnInfo.setText('Position state [internal val]')
         elif (i == 10):
            self.columnInfo.setText('Lanex dist state [internal val]')
         elif (i == 11):
            self.columnInfo.setText('Lanex history [internal val]')
      elif (f == 'PROC_LANE_DETECTION'):
         if (i == 1):
            self.columnInfo.setText('Car pos. from lane center (meters)')
         elif (i == 2):
            self.columnInfo.setText('Phi')
         elif (i == 3):
            self.columnInfo.setText('Road width (meters)')
         elif (i == 4):
            self.columnInfo.setText('State of lane estimator')
      elif (f == 'PROC_VEHICLE_DETECTION'):
         if (i == 1):
            self.columnInfo.setText('Distance to ahead vehicle (meters)')
         elif (i == 2):
            self.columnInfo.setText('Impact time to ahead vehicle (secs.)')
         elif (i == 3):
            self.columnInfo.setText('Detected # of vehicles')
         elif (i == 4):
            self.columnInfo.setText('Gps speed (Km/h) [redundant val]')

      elif (f == 'PROC_OPENSTREETMAP_DATA'):
         if (i == 1):
            self.columnInfo.setText('Current road maxspeed')
         elif (i == 2):
            self.columnInfo.setText('Maxspeed reliability [Flag]')
         elif (i == 3):
            self.columnInfo.setText('Road type [graph not available]')
         elif (i == 4):
            self.columnInfo.setText('# of lanes in road')
         elif (i == 5):
            self.columnInfo.setText('Estimated current lane')
         elif (i == 6):
            self.columnInfo.setText('Latitude used to query OSM')
         elif (i == 7):
            self.columnInfo.setText('Longitude used to query OSM')
         elif (i == 8):
            self.columnInfo.setText('Delay answer OSM query (seconds)')
         elif (i == 9):
            self.columnInfo.setText('Speed (Km/h) [redundant val]')

   def getYaxisMinMax (self):
      maxY = np.amax(self.datay)
      minY = np.amin(self.datay)

      f = self.fileList.currentText()
      i = self.indexCol
      if (f == 'PROC_LANE_DETECTION'):
         if (i == 1):
            minY = -1.5
            maxY = 1.5
         elif (i == 2):
            minY = -2
            maxY = 2
         elif (i == 3):
            minY = 0
            maxY = 5
         elif (i == 4):
            minY = -1.5
            maxY = 2.5

      return (minY, maxY)

   def startPlot(self):
      if (self.dataCorrect):
         if (self.pausePlot):
            self.pausePlot = False
         else:
            self.plotting = True
            if (self.draw_thread == False):
               #change: 
               self.draw_thread = threading.Thread(target=self.plot)
               self.draw_thread.start()
               #self.plotting = True
               #self.plot()
            else:
               self.draw_thread.stopped= False
			
   def stopPlot(self):
      self.plotting = False
      self.draw_thread = False
      self.dataRestarted = True
      self.pausePlot = False


   def plot(self):
      self.ax = self.figure.add_subplot(111)
      self.ax.hold(False)	# discards the old graph
      #self.figure.tight_layout()
      #self.ax.axis([0, timeWindow , 0, 1000])  #just to fix the padding calculation
      #self.figure.tight_layout(pad=0.1, w_pad=0.1, h_pad=0.1)

      i=0
      #indexPrev = 0
      while (self.plotting==True):	
			
         while (self.pausePlot  == True and self.plotting == True ):
            time.sleep(0.005)

         if ((self.fileList.currentText() == "PROC_OPENSTREETMAP_DATA") and (self.indexCol == 3)):
            #i = np.abs(self.datax - (currentSecond - delayVideoToData + 1/fps)).argmin()
            #self.columnInfo.setText('Road type: ' + str(self.datay[i]))
            time.sleep (0.033)
            continue
				
			
         if (self.dataRestarted == False):	#if data was just reloaded wait to next loop to update i
            self.semaforoPlot = True

            self.ax.set_xlim([currentSecond - delayVideoToData - timeWindow, currentSecond - delayVideoToData])
            self.canvas.draw()	# refresh canvas  #ahora lo hacemos en main thread

            """
            #self.figure.draw_artist(self.figure.patch)
            self.ax.draw_artist(self.ax.patch)
            self.ax.draw_artist(self.plotter)
            #self.ax.draw_artist(self.ax.xaxis)
            #self.ax.draw_artist(self.ax.yaxis)
            #TODO: encontrar manera de reemplazar el draw, falta los ejes de la figura
            self.canvas.update()
            """
   
            
            self.canvas.flush_events()		#LINEA IMPORTANTE! SINO NO ACTUALIZA EL QT LOOP, como el plt.pause hace con su plot 
            #QtWidgets.QApplication.processEvents()
            #time.sleep(0.033)  #OLD: small value makes plots flicker
            time.sleep(0.2)  #importante, sino esta ploteando rapido y hace flickering
            self.semaforoPlot = False
         else:
            self.plotter, = self.ax.plot(self.datax, self.datay, '-')	# plot data	

            loc = plticker.MultipleLocator(base=float(5))
            self.ax.xaxis.set_major_locator(loc)
            loc2 = plticker.MultipleLocator(base=float(1))
            self.ax.xaxis.set_minor_locator(loc2)
            self.ax.grid(True)
            self.ax.grid(which='both')
            self.ax.grid(which='minor', alpha=0.5)                                                
            self.ax.grid(which='major', alpha=1)
            self.miny, self.maxy = self.getYaxisMinMax()

            self.margen = (self.maxy - self.miny)/20
            self.ax.axis([currentSecond - delayVideoToData - timeWindow, currentSecond - delayVideoToData , self.miny-self.margen, self.maxy+self.margen])	 #[xmin, xmax, ymin, ymax]		

            self.figure.tight_layout(pad=0.1, w_pad=0.1, h_pad=0.1)
            
            #ani = animation.FuncAnimation(self.figure, self.animate, range(1, 200), interval=0, blit=False)
            #print('hasta aqui')
            #self.plotting = False
            #ani = animation.FuncAnimation(self.figure, self.animate, interval=50, blit=False)

            #self.canvas.draw()


            self.dataRestarted = False


			
			#TODO: optimize loop: http://bastibe.de/2013-05-30-speeding-up-matplotlib.html


#http://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
   def animate(self):
      self.ax.set_xlim([currentSecond - delayVideoToData - timeWindow, currentSecond - delayVideoToData])
      #self.canvas.draw()
      #return lines

# We'd normally specify a reasonable "interval" here...
#ani = animation.FuncAnimation(fig, animate, xrange(1, 200), interval=0, blit=True)



class WindowPlot(QtWidgets.QMainWindow):
	
   signalUpdatePixmap = QtCore.pyqtSignal(QtGui.QPixmap)	#This has to be outside init...
   signalUpdateFigure = QtCore.pyqtSignal(FigureCanvas)	#This has to be outside init...
   signalRePolish = QtCore.pyqtSignal(QtWidgets.QLabel)	#This has to be outside init...

   def __init__(self, parent=None):
      super(WindowPlot, self).__init__(parent)

      self.started = False
      self.paused = False
      self.stopped = True
      self.quitted = False
      self.frameNumberChanged = False

      self.signalUpdatePixmap.connect(self.updatePixmap)
      self.signalUpdateFigure.connect(self.updateFigure)
      self.signalRePolish.connect(self.rePolish)

      self.sliderVideoFrame = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)	#needed init before loadvideo
      self.labelCurrentVideoSecond = QtWidgets.QLabel()
      self.labelTotalVideoSecond = QtWidgets.QLabel()
      self.messageShower = QtWidgets.QLabel()

      self.capturing = False
      self.frameNumber=0
      self.loadVideo()

      self.totalFrames = -1
      self.firstTime = True

      self.video_thread = False
      #self.buttonSelectVideo = QtWidgets.QPushButton('Select video [' + videoName.split('/')[-1] + ']')
      #self.buttonSelectVideo.clicked.connect(self.selectVideo)

      self.start_button = QtWidgets.QPushButton('Start',self)
      self.start_button.clicked.connect(self.startCaptureThread)

      self.end_button = QtWidgets.QPushButton('Stop and Reset',self)
      self.end_button.clicked.connect(self.endCapture)

      self.quit_button = QtWidgets.QPushButton('Quit',self)
      self.quit_button.clicked.connect(self.quitCapture)

      vboxVideoOptions = QtWidgets.QHBoxLayout()
      vboxVideoOptions.addWidget(self.start_button)
      vboxVideoOptions.addWidget(self.end_button)
      vboxVideoOptions.addWidget(self.quit_button)

      self.labelImage = QtWidgets.QLabel()
      self.labelImage.setFixedHeight(videoheightShow)
      self.labelImage.setFixedWidth(videowidthShow)

      self.rewindPanelLayout = QtWidgets.QHBoxLayout()
       
      self.sliderVideoFrame.sliderMoved.connect(self.sliderFrameChanged)
      self.sliderWasReleased = True
      self.sliderVideoFrame.sliderReleased.connect(self.sliderFrameReleased)

      self.rewindPanelLayout.addWidget(self.labelCurrentVideoSecond)
      self.rewindPanelLayout.addWidget(self.sliderVideoFrame)
      self.rewindPanelLayout.addWidget(self.labelTotalVideoSecond)

      self.loadScoreWidgets()
   
      self.hboxLogos = QtWidgets.QHBoxLayout()    
      self.labelLogoRobesafe = QtWidgets.QLabel()
      self.labelLogoRobesafe.setFixedHeight(100)
      if hasattr(sys, '_MEIPASS'):  #differ between packed app and developed
         self.labelLogoRobesafe.setPixmap(QtGui.QPixmap(os.path.join(sys._MEIPASS, './icons/Robesafe.png')).scaled(self.labelLogoRobesafe.size(), QtCore.Qt.KeepAspectRatio))
      else:
         self.labelLogoRobesafe.setPixmap(QtGui.QPixmap('./icons/Robesafe.png').scaled(self.labelLogoRobesafe.size(), QtCore.Qt.KeepAspectRatio))         
      self.labelDrivesafe = QtWidgets.QLabel()
      self.labelDrivesafe.setFixedHeight(100)
      if hasattr(sys, '_MEIPASS'):
         self.labelDrivesafe.setPixmap(QtGui.QPixmap(os.path.join(sys._MEIPASS , './icons/drivesafe.png')).scaled(self.labelDrivesafe.size(), QtCore.Qt.KeepAspectRatio))
      else:
         self.labelDrivesafe.setPixmap(QtGui.QPixmap('./icons/drivesafe.png').scaled(self.labelDrivesafe.size(), QtCore.Qt.KeepAspectRatio))         
      self.labelLogoUah = QtWidgets.QLabel()   
      self.labelLogoUah.setFixedHeight(100)
      if hasattr(sys, '_MEIPASS'):
         self.labelLogoUah.setPixmap(QtGui.QPixmap(os.path.join(sys._MEIPASS , './icons/uah.png')).scaled(self.labelLogoUah.size(), QtCore.Qt.KeepAspectRatio))
      else:
         self.labelLogoUah.setPixmap(QtGui.QPixmap('./icons/uah.png').scaled(self.labelLogoUah.size(), QtCore.Qt.KeepAspectRatio))      
      self.hboxLogos.addWidget(self.labelLogoRobesafe)
      self.hboxLogos.addStretch(1)
      self.hboxLogos.addWidget(self.labelDrivesafe)
      self.hboxLogos.addStretch(1)
      self.hboxLogos.addWidget(self.labelLogoUah)

      hLine = QtWidgets.QFrame()
      hLine.setFrameStyle(QtWidgets.QFrame.HLine)
      hLine.setLineWidth(2)

      hLine2 = QtWidgets.QFrame()
      hLine2.setFrameStyle(QtWidgets.QFrame.HLine)
      hLine2.setLineWidth(2)


      self.buttonSelectDataFolder = QtWidgets.QPushButton('Select data folder [' + dataFolderName.split('/')[-1] + ']')
      self.buttonSelectDataFolder.clicked.connect(self.selectDataFolder)

      vbox = QtWidgets.QVBoxLayout()
      #vbox.addWidget(self.buttonSelectVideo)
      vbox.addWidget(self.buttonSelectDataFolder)
      vbox.addLayout(vboxVideoOptions)
      vbox.addWidget(self.messageShower)
      vbox.addStretch(1)
      vbox.addWidget(self.labelImage)
      vbox.addLayout(self.rewindPanelLayout)
      vbox.addWidget(hLine)
      vbox.addLayout(self.gridScores)
      vbox.addWidget(hLine2)
      vbox.addStretch(1)
      vbox.addLayout(self.hboxLogos)



      hboxFigures = QtWidgets.QHBoxLayout()
      #spinbox para seleccionar seconds window
      labelTimeWindow = QtWidgets.QLabel('Select Plot Interval (s): ')
      hboxFigures.addWidget(labelTimeWindow)
      self.spinTimeWindow = QtWidgets.QSpinBox()	
      self.spinTimeWindow.valueChanged.connect(self.setTimeWindow)
      self.spinTimeWindow.setRange(5, 500)
      self.spinTimeWindow.setValue(30)
      hboxFigures.addWidget(self.spinTimeWindow)

      labelNumFigures = QtWidgets.QLabel('Select Num. of Figures: ')
      hboxFigures.addWidget(labelNumFigures)
      self.spinNumFigures = QtWidgets.QSpinBox()	
      self.spinNumFigures.setRange(2, 6)
      self.numFigures = 4  #init
      self.spinNumFigures.setValue(self.numFigures)
      self.spinNumFigures.valueChanged.connect(self.setNumFigures)
      hboxFigures.addWidget(self.spinNumFigures)

      #self.listFigures = QtCore.QList()  #qlist not available in python
      self.listFigures = []   #python list
      for n in range(0, self.numFigures):
         figure = figureToPlot()   #parent of figure = self
         self.listFigures.append(figure)
         self.listFigures[n].spinSelectCol.setValue(n+1)

      # set the layout
      self.vbox2 = QtWidgets.QVBoxLayout()
      #self.vbox2.addWidget(self.buttonSelectDataFolder)
      self.vbox2.addLayout(hboxFigures)
      for n in range(0, self.numFigures):
         self.vbox2.addLayout(self.listFigures[n])
         

      vboxGlobal = QtWidgets.QHBoxLayout()
      vboxGlobal.addLayout(vbox)
      vboxGlobal.addLayout(self.vbox2)
      vboxGlobal.addStretch(1)
      #self.setFixedWidth(1600)
      #self.setFixedHeight(1050)

      self.showMessage('Welcome to DriveSet Reader')

      window = QtWidgets.QWidget()
      window.setLayout(vboxGlobal)
      self.setCentralWidget(window)

      self.setWindowTitle('DriveSet Reader')
      self.move(50,100)
      self.show()


   def startCaptureThread(self):
      print ("Video loaded?:", videoCorrect)
      print ("Data loaded?:", dataCorrect)
      if (videoCorrect and dataCorrect):
         if (self.paused):
            self.paused = False
            print ("pressed start")
            self.showMessage('Sequence started')
            self.start_button.setText('Pause')
            self.startPlots()
         else:
            if (self.capturing == False):
               if (self.video_thread == False):	
                  self.video_thread = threading.Thread(target=self.startCapture)
               print ("pressed start")
               self.showMessage("Sequence started")
               self.paused = False
               self.capturing = True
               self.start_button.setText('Pause')
               self.video_thread.start()
               self.startPlots()
               #self.spinNumFigures.setEnabled(False)  #disabled for security. 
            else:
               print ("pressed Pause")
               self.showMessage("Sequence paused")
               self.start_button.setText('Start')
               self.paused = True
               self.pausePlots()	
      else:
         self.showMessage('Video or Data not correctly selected!!', 3)
	


   def startCapture(self):
      global currentSecond
      global delayVideoData
      #cap = self.capturer
      num = 0
      while(self.capturing):
         while (self.paused and self.capturing):
            time.sleep(0.05)
			
         prevTime = datetime.now()
	
         if (self.frameNumberChanged):
            newFrameNumber = int(self.sliderVideoFrame.value()*30)
            num = newFrameNumber
            self.frameNumber = newFrameNumber
            self.frameNumberChanged = False
				
         frame = self.videoReader.get_data(num)
         num = num+1
         
         if (num >= self.videoReader.get_length()):
            self.frameNumberChanged=True
            self.sliderVideoFrame.setValue(0)
            self.start_button.setText('Start')
            self.video_thread = False
            self.capturing = False		
            break

         self.frameNumber = num
         currentSecond = self.frameNumber/fps	#valor importante para sync datos
         self.labelCurrentVideoSecond.setText("{0:.1f}".format(currentSecond - delayVideoToData))
         if (self.sliderWasReleased):
            self.sliderVideoFrame.setValue(int(self.frameNumber/fps))

         #Convert opencv mat to QImage:
         imageQ = QtGui.QImage(frame.tostring(), frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)

         if (frame.shape[1] != videowidthShow or frame.shape[0] != videoheightShow):
            imageQ = imageQ.scaled(videowidthShow, videoheightShow)  #resize image to fit

         #Convert QImage to pixmap:
         pixmap = QtGui.QPixmap.fromImage(imageQ)
         #Set pixmap to label:
         #self.labelImage.setPixmap(pixmap)	#old mode, cuidado porque es un thread outside the GUI, esto da problemas en pyqt
         self.signalUpdatePixmap.emit(pixmap)	#nuevo mode para evitar esos problemas
         self.updateScoreLabels()
         diftime = ((datetime.now()-prevTime).microseconds)/1000000.0
         #print (diftime)
         #print(1/fps - diftime )
         if (diftime < 1/fps):
            time.sleep (1/fps - diftime)
         else:
            time.sleep(0.01)
         app.processEvents()	#prevents app from crashing because of lack of responsiveness
	
   def updatePixmap(self, pixmap):
      self.labelImage.setPixmap(pixmap)
      #self.paintPlots()

   def updateFigure(self, canvas):  #currently not used
      canvas.draw()
      #canvas.update()
      #canvas.flush_events()

   def rePolish(self, label):  #if this is not done by signal it throws a SegFault
      label.style().unpolish(label)
      label.style().polish(label)
      label.update()
      #label.ensurePolished()

   def endCapture(self):
      print ("pressed Stop")
      self.showMessage("Sequence stopped & reset")
      self.start_button.setText('Start')
      self.video_thread = False
      self.capturing = False
      #self.stopPlots()
      self.frameNumber=0
      self.frameNumberChanged = True
      self.sliderVideoFrame.setValue(0)
	
   def closeEvent(self, event):
      self.quitCapture()

   def quitCapture(self):
      print ("pressed Quit")
      self.video_thread = False
      self.capturing = False
      self.frameNumber=0
      self.stopPlots()
      QtCore.QCoreApplication.quit()

   def loadScoresData(self):
      scoresFileName = dataFolderName + '/' + 'SEMANTIC_ONLINE.txt'
      global dataCorrect
      try:
         self.scoresData = np.genfromtxt(scoresFileName, dtype=np.float, delimiter=' ')	
         self.scoresDataTime = self.scoresData[:,0]
         dataCorrect = True
      except:
         dataCorrect = False

   def getScoreForLineCol(self, i, col):
      #TODO: cambiar esto porque esta buscando en todo el archivo para cada label!!! el i se puede hacer general por cada linea
      if (dataCorrect):
         #i = np.abs(self.scoresDataTime - (currentSecond - delayVideoToData + 1/fps)).argmin()
         #i=0
         return self.scoresData[i,col]
      else:
         if ((col >= 11 and col < 14) or (col >=23 and col < 26)):
            return 1.0
         return 100.0

   def loadScoreWidgets(self):
      self.gridScores = QtWidgets.QGridLayout()  #row, column

      verticalLine 	=  QtWidgets.QFrame()
      verticalLine.setFrameStyle(QtWidgets.QFrame.VLine)
      verticalLine.setLineWidth(3)
      verticalLine.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Expanding)

      verticalLine2 	=  QtWidgets.QFrame()
      verticalLine2.setFrameStyle(QtWidgets.QFrame.VLine)
      verticalLine2.setLineWidth(3)
      verticalLine2.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Expanding)

      d=2   #controlar desplazamiento de ultimas casillas, d=0 o d=1    
      d1=1

      self.gridScores.addWidget(verticalLine, 0, 2, 3, 3) 
      self.gridScores.addWidget(verticalLine2, 0, 10, 3, 11) 

      self.lbScores = QtWidgets.QLabel('SCORES')
      self.gridScores.addWidget(self.lbScores, 0, 0)
      self.lbScore0t = QtWidgets.QLabel('Total', )
      self.gridScores.addWidget(self.lbScore0t, 0, 1, QtCore.Qt.AlignCenter)
      self.lbScoresg = QtWidgets.QLabel('Until now:')
      self.lbScoresg.setToolTip('Scores obtained in the whole route until the current time')
      self.gridScores.addWidget(self.lbScoresg, 1, 0) 
      self.lbScoresw = QtWidgets.QLabel('Last minute:')
      self.lbScoresw.setToolTip('Scores obtained only during the last minute of the route')
      self.gridScores.addWidget(self.lbScoresw, 2, 0) 


      self.listScores0 = []   #python list
      self.listScores1 = []   #python list
      self.listScores2 = []   #python list

      for n in range(0, 11):
         score = QtWidgets.QLabel()   #parent of figure = self
         #self.setInitialStyleSheet(score)	

         score.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding);
         self.listScores0.append(score)
         d=1
         if (n==0):
            d=0
         elif (n>7):
            d=2
         self.gridScores.addWidget(self.listScores0[n], 0, n+1+d, QtCore.Qt.AlignCenter)

      
      for n in range(0, 11):
         score = QtWidgets.QLabel('10.0')   #parent of figure = self
         self.setInitialStyleSheet(score)	
         score.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
         self.listScores1.append(score)
         d=1
         if (n==0):
            d=0
         elif (n>7):
            d=2
         self.gridScores.addWidget(self.listScores1[n], 1, n+1+d)

      for n in range(0, 11):
         score = QtWidgets.QLabel('10.0')   #parent of figure = self
         self.setInitialStyleSheet(score)	
         score.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
         self.listScores2.append(score)
         d=1
         if (n==0):
            d=0
         elif (n>7):
            d=2
         self.gridScores.addWidget(self.listScores2[n], 2, n+1+d)

      self.listScores0[0].setText('Total')
      self.listScores0[1].setText('Accel.')
      self.listScores0[2].setText('Brakings')
      self.listScores0[3].setText('Turnings')
      self.listScores0[4].setText('Weaving')
      self.listScores0[5].setText('Drifting')
      self.listScores0[6].setText('Overspeed')
      self.listScores0[7].setText('Carfollow')
      self.listScores0[8].setText('Normal')
      self.listScores0[9].setText('Drowsy')
      self.listScores0[10].setText('Aggressive')

      #self.lbScore0.setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

      self.loadScoresData()
      self.updateScoreLabels()
      self.firstTime = False

   def setInitialStyleSheet(self, label):
      label.setProperty('color', 'green')
      label.setStyleSheet("""
           [color="green"] {background-color: green; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
           [color="yellow"] {background-color: yellow; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
           [color="red"] {background-color: red; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
           [color="orange"] {background-color: orange; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
           [color="lightblue"] {background-color: lightblue; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
           [color="GreenYellow"] {background-color: GreenYellow; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
           [color="coral"] {background-color: coral; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 14px; qproperty-alignment: AlignCenter;}
            """)
      self.signalRePolish.emit(label)

   def updateScoreLabels(self):
      if (dataCorrect):
         i = np.abs(self.scoresDataTime - (currentSecond - delayVideoToData + 1/fps)).argmin()
      else:
         i=0
      #3 = global, 4=Accelerations...
      d = 3
      for n in range(0, 8):
         if (dataCorrect):
            scoreval = self.getScoreForLineCol(i, n+d)/10.0
            self.listScores1[n].setText("{0:.1f}".format(scoreval))
         else:
            scoreval = 10.0
         colorstr = 'green'
         if (scoreval < 2.5):
            colorstr = 'red'
         elif (scoreval < 5.0):
            colorstr = 'orange'
         elif (scoreval < 7.5):
            colorstr = 'yellow'
         self.setStyleLabelScoreStr(self.listScores1[n], colorstr)

      for n in range(8, 11):
         if (dataCorrect):
            scoreval = self.getScoreForLineCol(i, n+d)*10.0
            self.listScores1[n].setText("{0:.1f}".format(scoreval))

      values = [float(self.listScores1[8].text()), float(self.listScores1[9].text()), float(self.listScores1[10].text())]
      if (isinstance(max(values), list) == False):
         ind = values.index(max(values))
         if (ind == 0):
            self.setStyleLabelScoreStr(self.listScores1[8], 'green') 
            self.setStyleLabelScoreStr(self.listScores1[9], 'lightblue')
            self.setStyleLabelScoreStr(self.listScores1[10], 'coral')   
         elif (ind == 1):
            self.setStyleLabelScoreStr(self.listScores1[8], 'GreenYellow')
            self.setStyleLabelScoreStr(self.listScores1[9], 'blue') 
            self.setStyleLabelScoreStr(self.listScores1[10], 'coral') 
         elif (ind == 2):
            self.setStyleLabelScoreStr(self.listScores1[8], 'GreenYellow')
            self.setStyleLabelScoreStr(self.listScores1[9], 'lightblue')
            self.setStyleLabelScoreStr(self.listScores1[10], 'red') 


      d = 15
      for n in range(0, 8):
         if (dataCorrect):
            scoreval = self.getScoreForLineCol(i, n+d)/10.0
            self.listScores2[n].setText("{0:.1f}".format(scoreval))
         else:
            scoreval = 10.0
         colorstr = 'green'
         if (scoreval < 2.5):
            colorstr = 'red'
         elif (scoreval < 5.0):
            colorstr = 'orange'
         elif (scoreval < 7.5):
            colorstr = 'yellow'
         self.setStyleLabelScoreStr(self.listScores2[n], colorstr)

      for n in range(8, 11):
         scoreval = self.getScoreForLineCol(i, n+d)*10.0
         self.listScores2[n].setText("{0:.1f}".format(scoreval))

      values = [float(self.listScores2[8].text()), float(self.listScores2[9].text()), float(self.listScores2[10].text())]
      if (isinstance(max(values), list) == False):
         ind = values.index(max(values))
         if (ind == 0):
            self.setStyleLabelScoreStr(self.listScores2[8], 'green') 
            self.setStyleLabelScoreStr(self.listScores2[9], 'lightblue')
            self.setStyleLabelScoreStr(self.listScores2[10], 'coral')   
         elif (ind == 1):
            self.setStyleLabelScoreStr(self.listScores2[8], 'GreenYellow')
            self.setStyleLabelScoreStr(self.listScores2[9], 'blue') 
            self.setStyleLabelScoreStr(self.listScores2[10], 'coral') 
         elif (ind == 2):
            self.setStyleLabelScoreStr(self.listScores2[8], 'GreenYellow')
            self.setStyleLabelScoreStr(self.listScores2[9], 'lightblue')
            self.setStyleLabelScoreStr(self.listScores2[10], 'red') 

   def setStyleLabelScoreStr(self, label, colorstr):

      #if (label.property('color') != colorstr):
      label.setProperty('color', colorstr)   
      self.signalRePolish.emit(label)

   def setStyleLabelScore(self, label, color):
      colorstr = 'green'
      if (color == 1): 
         colorstr = 'green'
      if (color == 11): 
         colorstr = 'lightgreen'
      elif (color == 2): 
         colorstr = 'yellow'
      elif (color == 3): 
         colorstr = 'orange'
      elif (color == 4): 
         colorstr = 'red'
      elif (color == 44): 
         colorstr = 'coral'
      elif (color == 5): 
         colorstr = 'blue'
      elif (color == 55): 
         colorstr = 'lightblue'
      
      self.setStyleLabelScoreStr(label, colorstr)
 

   def sliderFrameChanged(self):
      self.sliderWasReleased = False
      self.frameNumberChanged = True
      #self.plotsRestarted()
      self.labelCurrentVideoSecond.setText("{0:.1f}".format(self.sliderVideoFrame.value()-delayVideoToData))

   def sliderFrameReleased(self):
      self.sliderWasReleased = True

   def updateDatesInfo(self):
      global videoDateString
      global videoDate
      global delayVideoToData
      global dataDateString
      global dataDate

      videoDateString = videoName.split('/')[-1][0:14]
      dataDateString = dataFolderName.split('/')[-1][0:14]

      videoDate = datetime.strptime(videoDateString, "%Y%m%d%H%M%S")
      dataDate = datetime.strptime(dataDateString, "%Y%m%d%H%M%S")
      delayVideoToData = (dataDate - videoDate).total_seconds()
      self.labelCurrentVideoSecond.setText("{0:.1f}".format((self.frameNumber/fps)-delayVideoToData))
      self.labelTotalVideoSecond.setText("{0:.1f}".format((self.totalFrames/fps)-delayVideoToData))
      print (delayVideoToData) 
      if (abs(delayVideoToData) > 300): #si delay mayor que dos minutos y medio   
         self.showMessage('Video & Data not synced, please make both from the same route', 3)
      else:
         self.showMessage('Video & Data synced correctly', 1) 

   def selectVideo(self):
      global videoName
      self.fileNameQ, _ = QtWidgets.QFileDialog.getOpenFileName()
      videoName = str(self.fileNameQ)
      self.buttonSelectVideo.setText('Select video [' + videoName.split('/')[-1] + ']')
      self.loadVideo()


   def loadVideo(self):
      global videoCorrect
      self.frameNumber = 0
      try:
         imageio.plugins.ffmpeg.download()  #need ffmpeg to load the video
         self.videoReader = imageio.get_reader(videoName, 'ffmpeg')
         videoCorrect = True
      except:
         videoCorrect = False

      if (videoCorrect):
         global fps
         video_meta = self.videoReader.get_meta_data()   #returns dict
         #print (video_meta)
         fps = video_meta['fps']
         print (fps)
         if (fps == 0):	#error control for division by 0
	         fps = 30
         self.totalFrames = self.videoReader.get_length()
         self.sliderVideoFrame.setRange(0, (self.totalFrames/fps))
         self.updateDatesInfo()

   def selectDataFolder(self):
      global dataFolderName
      dataFolderNameQ = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Data Folder')
      dataFolderName = str(dataFolderNameQ)
      self.buttonSelectDataFolder.setText('Select data folder [' + dataFolderName.split('/')[-1] + ']')
      
      #filterList = QtCore.QStringList("*.mp4")
      filterList = ['*.mp4']
      directory = QtCore.QDir(dataFolderNameQ)
      listvideos = directory.entryList(filterList)
      print (listvideos)
      if (len(listvideos)==0):
         print ('0 videos, searching MOV, AVI, MKV')
         filterList = ['*.mp4', '*.MOV', '.MP4', '.AVI', '.mov', '.avi', '.mkv', '.MKV']
         listvideos = directory.entryList(filterList)
         print (listvideos)
      
      global videoName
      global videoCorrect
      if (len(listvideos) == 0):
         videoCorrect = False
         self.frameNumber = 0
         videoName = ''
         self.showMessage('Video not found in folder', 3)
      else:
         videoName = dataFolderName + '/' + listvideos[0]
         self.loadVideo()
     
      self.loadScoresData()
      self.loadDataPlots()

      if (dataCorrect and videoCorrect):
         self.updateDatesInfo()
   
   def loadDataPlots(self):
      for n in range(0, self.numFigures):
         #self.listFigures[n].loadData()  #this doesnt reload folder name
         self.listFigures[n].selectFileFromList()

   def startPlots(self):
      print (self.numFigures)
      for n in range(0, self.numFigures):
         self.listFigures[n].startPlot()   		

   def pausePlots(self):
      for n in range(0, self.numFigures):
         self.listFigures[n].pausePlot = True  	

   def stopPlots(self):
      for n in range(0, self.numFigures):
         #self.listFigures[n].pausePlot = True   #pause para que no siga pintando al esperar semaforo
         #while(self.listFigures[n].semaforoPlot):  
         #   time.sleep(0.005)
         self.listFigures[n].stopPlot() 

   def plotsRestarted(self):	
      for n in range(0, self.numFigures):
         self.listFigures[n].dataRestarted = True  

   def paintPlots(self):
      for n in range(0, self.numFigures):
         if ( self.listFigures[n].plotting==True):
            self.listFigures[n].canvas.draw()

   def showMessage(self, string, color=0):
      self.messageShower.setText('Message: ' + string)
      self.messageShower.setAutoFillBackground(True)
      if (color==0 or color==1):
         self.messageShower.setStyleSheet('color: black; background-color: green')
      elif (color==2):
         self.messageShower.setStyleSheet('color: black; background-color: yellow')
      elif (color==3):
         self.messageShower.setStyleSheet('color: black; background-color: red')

   def setTimeWindow(self):
      global timeWindow
      timeWindow = self.spinTimeWindow.value()

  # def resizeEvent(self,resizeEvent):
         

   def setNumFigures(self):

      if (self.capturing):
         self.startCaptureThread()  #pause everything

      #for n in range(0, self.numFigures):
      #   while(self.listFigures[n].semaforoPlot):  #TODO check, esto no asegura el pause
      #      time.sleep(0.001)

      prevNumFigures = self.numFigures
      self.numFigures = self.spinNumFigures.value()

      if (prevNumFigures > self.numFigures):   #si mayor borrar figures
         self.listFigures[self.numFigures].removeAll()
         self.listFigures.pop()
         
      elif (prevNumFigures < self.numFigures):  #si menor aniadir figures
         for n in range(prevNumFigures, self.numFigures):
            figure = figureToPlot()
            self.listFigures.append(figure)
            self.listFigures[n].spinSelectCol.setValue(n+1)
            self.listFigures[n].pausePlot = self.paused
            if(self.capturing):
               self.listFigures[n].startPlot()
            self.vbox2.addLayout(self.listFigures[n])

      if (self.capturing):
         #self.startPlots()
         self.startCaptureThread()



if __name__ == '__main__':
   global app
   app = QtWidgets.QApplication(sys.argv)
   app.setStyle("fusion") #Changing the style

   windowplot = WindowPlot()
   sys.exit(app.exec_())


