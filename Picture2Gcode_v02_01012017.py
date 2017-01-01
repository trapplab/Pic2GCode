#!/usr/local/bin/python3
"""
This file is part of Picture2GCode.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Picture2GCode.  If not, see <http://www.gnu.org/licenses/>.
"""


"""
GCcode Converter "Picture2GCode_0.1" 

Load jpeg or png Image and convert it to GCode for Laserengraving

Need libraries installed:
- PyQt4
- PIL
- numpy

Author: Thomas Trapp
Date:1.1.2017


TODO:
-Add Menü
-Add Plotter Settings
"""


import sys
import re
import time
import datetime
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import *

#Plotter Settings
#Change this for your Plotter
maxStrength = 255

#Variable um ausgewählten Dateipfad zwischenzuspeichern
fileName = ""


notloaded = []
try:
	from PIL import Image
except:
	notloaded.append("PIL")

try:
	import numpy as np
except:
	notloaded.append("numpy")
	
if notloaded:
	statusmessage = "Please install following librarys: " 
	for lib in notloaded:
		statusmessage += " %s\t" % lib
	#~ w.statusbar.message(statusmessage)
	print(statusmessage)
	

#Funktionen-------------------------------------------------------
def skalieren(image, xmm):
	tmp = image.size
	abmessungen = (int(xmm*w.pixmm.value()),int(xmm*w.pixmm.value()*tmp[1]/tmp[0]))
	return image.resize(abmessungen)
	
	#liefert eine Liste mit Zahlen zwischen 0 u 254
def invertValues(bild):
	return [~zahl & 0xFF for zahl in list(bild.getdata())]
	

#Funktion stellt Bild mit gewÃ¼nschter Anzahl an Graustufen dar
def Stufen(bildarray, graustufen):
	tmp = []
	schrittweite = round(255/graustufen)-1				#schrittweite zwischen 
	werteteiler = round(255/graustufen)

	for element in bildarray:
		tmp.append(schrittweite * round(element/werteteiler))
	return tmp


	
	#Fkt findet den ersten und letzten Punkt einer Zeile..wenn nicht vorhanden return 0
def findEnds(matrix,line):	#Zeilen und Spalten werden jeweils ab 1 gezÃ¤hlt!
									#Deshalb das +1
									
	#finding the nonzero values
	#liefert Tupel mit information Ãber x und y Richtugn in der Matrix
	nozero = np.transpose(np.nonzero(matrix))
	#list mit allen positionen der gewÃ¼nschten linie
	linenumbers = []
	for element in nozero:
		if element[0] == line-1:
			linenumbers.append(element[1])
	if linenumbers == []:
		return 0
	else:
		return (linenumbers[0]+1 ,linenumbers[-1]+1)
		
		
#Funktion checkt ob die danebenliegenden Punkte gleich sind
def nextPoint(matrixline, pos, fromright):
	#if pos >= len(matrixline) or pos <= len(matrixline):
	#	return False
	pos = pos-1						#position korrigieren auf meine Positionsrechnung
	if (pos+1) > len(matrixline)-1 or (pos -1) < 0:		#Wenn auserhalb dann true...die Zeile ist dann eh zu ande
		return True
		
	elif fromright:
		if matrixline[pos] == matrixline[pos -1]:
			return True
	else:
		if matrixline[pos] == matrixline[pos +1]:
			return True
	
	return False
	
def transform2Gcode():				
	#startZeit = time.time()
	
	pxpromm = w.pixmm.value()
	#Ãffnen,skalieren,in graustufen wandeln
	im = Image.open(fileName)
	bild = skalieren(im, w.bildbreite.value()).convert("L")
	
	#bilddaten holen und invertieren
	bilddaten = invertValues(bild)
	
	bilddaten = Stufen(bilddaten , w.graustufen.value())
	
	#numpy array daraus machen
	x = np.array(bilddaten)
	BildMatrix = x.reshape(bild.size[1],bild.size[0])
	
	w.statusbar.message("Size" + str(bild.size))
	
	
	with open(w.Dateiname.text() + ".ngc","w") as gcode_file:
		header = "(Generated Code from GCodeConverter V0.1)\n\
(Selected Settings:)\n\
(Size[Höhe x Breite]:\t %d x %d pix | %d x %d mm)\n\
(Pixel pro mm:\t\t\t %d)\n\
(Graustufen:\t\t\t %d)\n\
(Intensität:\t\t\t min: %d%%,\t max: %d%% | Plotter Laser GCode Setting: M3 0...%d)\n\
(Speed:\t\t\t\t\t min %d,\t max: %d )\n\
(Offset:\t\t\t\t X %d,\t Y: %d )\n\
(Date:\t\t\t\t\t %s )\n\n\n\
M05	(turn of Plasma)\n\
G21	(All units in mm)\n\
\n\
G90	(Absolutmaß)\n\
M04 S0 (Enable M04 Dynamic Laser Power Mode)\n\n" % (bild.size[1], bild.size[0], w.bildbreite.value()*bild.size[1]/bild.size[0], w.bildbreite.value(),\
					w.pixmm.value(), w.graustufen.value(), w.inten_min.value(), w.inten_max.value(), maxStrength, \
					w.speed_min.value(), w.speed_max.value(), w.offset_x.value(), w.offset_y.value() ,datetime.datetime.now().strftime("%d. %B %Y, %H:%M Uhr" ) )

		footer = "(Footer)\n\
M05		(turn of Plasma)\n\
G0 X0.0 Y0.0 (Go home)"
	
		
		gcode_file.write(header)
		
		vonRechts = True
		for line in range(1, BildMatrix.shape[0]+1,1):	#werte von 0 bis matrixHoehe
			enden = findEnds(BildMatrix, line)		#enden = Tupel mit anfangs und endpunkt der Zeile
			if enden:							#wenn anfangspunkt dann ....
				if vonRechts:
					pos = enden[1]
				else :
					pos = enden[0]
				##GCode schreiben an Anfang fahren
				gcode_file.write("(turn off plasma an go into next Line)\n" + "G0 X" + getX(pos) + " Y" + getY(BildMatrix.shape[0]+1-line)+"\n\n")		#In schneller Fahr an die erste Position
				##
				if vonRechts:
					pos = pos-1
				else:
					pos = pos+1
				
				
				while pos < enden[1]  and pos > enden[0]:
					if nextPoint(BildMatrix[line-1,:],pos, vonRechts):
						if vonRechts:
							pos = pos-1
						else:
							pos = pos+1
							
					else:
						##GCode bis zur FarbÃ¤nderung
						#gcode_file.write(getM03(BildMatrix[line-1,pos-1]) +"\n")
						if vonRechts:
							gcode_file.write(whichGCommand(BildMatrix[line-1,pos-1]) + " X" + getX(pos-2)+ " Y" + getY(BildMatrix.shape[0]+1-line) + getM03(BildMatrix[line-1,pos-1]) + getF(BildMatrix[line-1,pos-1]) + "\n\n")	#bei farbÃ¤nderung zur Grenze fahren
						else:
							gcode_file.write(whichGCommand(BildMatrix[line-1,pos-1]) + " X" + getX(pos)+ " Y" + getY(BildMatrix.shape[0]+1-line) + getM03(BildMatrix[line-1,pos-1]) + getF(BildMatrix[line-1,pos-1]) + "\n\n")	#bei farbÃ¤nderung zur Grenze fahren
						##
						if vonRechts:
							pos = pos-1
						else:
							pos = pos+1
				
				##GCode schreiben wenn enden erricht
				#gcode_file.write(getM03(BildMatrix[line-1,pos-1]) +"\n")
				gcode_file.write(whichGCommand(BildMatrix[line-1,pos-1]) + " X" + getX(pos) + " Y" + getY(BildMatrix.shape[0]+1-line) + getM03(BildMatrix[line-1,pos-1]) + getF(BildMatrix[line-1,pos-1]) + "\n\n")		#An die Grenzen fahren wenn erreicht
				##
				
				vonRechts = not vonRechts			#toggelt den Zeilenanfang
				
				#Fortschrittsanzeige
				w.fortschritt.setValue(int(line/BildMatrix.shape[0]*100))
				
		gcode_file.write(footer)
		
		drawGCode()
	
	#print("Transformation in: " + str(round(time.time() - startZeit,2)) + "s")
			
			
			
	
def getX(pos):
	pxpromm = w.pixmm.value()
	OffsetXY = (w.offset_x.value(), w.offset_y.value())
	return str(round(pos/pxpromm + OffsetXY[0],4))
	 
def getY(yPos):
	pxpromm = w.pixmm.value()
	OffsetXY = (w.offset_x.value(), w.offset_y.value())
	return str(round(yPos/pxpromm + OffsetXY[1],4))

def getF(number):
	geschw = (w.speed_min.value(), w.speed_max.value() )
	geschwStep = round((geschw[1]-geschw[0])/255, 4)
	if number:
		return " F" + str(geschw[1] - number*geschwStep)
	else:
		return ""
	
def getM03(pix):
	staerkeProz = (w.inten_min.value(), w.inten_max.value())
	staerke = ((staerkeProz[0]*maxStrength)/100,(staerkeProz[1]*maxStrength)/100)		#max und min Stärke
	staerkeStep = round((staerke[1]-staerke[0])/maxStrength, 4)
	if pix:
		return " S" + str(int(round(pix*staerkeStep+staerke[0])))
	else:
		return " S0"

def whichGCommand(number):
	if number:
		return "G1"
	else:
		return "G0"

		


def loadPic(fileName):
	scene = QGraphicsScene()
	item = QPixmap(fileName).scaled(w.Vorschau.size(), aspectRatioMode=Qt.KeepAspectRatio)
	item = QGraphicsPixmapItem(item)
	scene.addItem(item)
	w.Vorschau.setScene(scene)

	
def browsePic():
	global fileName 
	fileName = QFileDialog.getOpenFileName(None, "Open File", "","Pictures (*.jpg *jpeg *png)");  #;;C++ Files (*.cpp *.h)");
	if fileName != "":
		loadPic(fileName) # Bild oeffnen
		w.Dateiname.setText(fileName.split("/")[-1].split(".")[0]) #Datei nach Bild nennen

def drawGCode():
	drawing = QGraphicsScene()
	pen = QPen()
	color = QColor()
	
	
	with open(w.Dateiname.text() + ".ngc","r") as datei:
		#find max
		maxX = 0.0001
		maxY = 0.0001
		for line in datei:
			if re.search("G[01]", line):
				line = line.split(" ")
				maxX = max(maxX, float(line[1].strip("X")))
				maxY = max(maxY, float(line[2].strip("Y")))
		
		scale = min(w.Vorschau_2.height()/maxY, w.Vorschau_2.width()/maxX) * 0.9		#scale Picture to 90% 
		
	with open(w.Dateiname.text() + ".ngc","r") as datei:
		verstaerkung = 5	
		staerke_visual = 0

		x_koord_old = 0		
		y_koord_old = 0
		
		x_koord = 0
		y_koord = 0
		
		
		for line in datei:
			if re.search("M03", line):
				staerke_visual = int(line[5:7])
			
			elif re.search("M05", line):
				staerke_visual = 0
			
			elif re.search("G[01]", line):
				line = line.split(" ")
				x_koord = float(line[1].strip("X"))
				y_koord = float(line[2].strip("Y"))
		
			#drawing the Gcode
			if staerke_visual == 0:
				color.setHsv(190,240,250)
			else:
				pass
				color.setHsv(max((maxStrength - staerke_visual*verstaerkung) , 0),max((maxStrength - staerke_visual*verstaerkung) , 0),max((maxStrength - staerke_visual*verstaerkung) , 0))
		
			pen.setColor(color)
			
			
			drawing.addLine(x_koord_old*scale,-y_koord_old*scale, x_koord*scale,-y_koord*scale,pen)
			x_koord_old = x_koord		
			y_koord_old = y_koord
		w.Vorschau_2.setScene(drawing)
	


	
app = QApplication(sys.argv)


##GUI-Elements
w = loadUi("GCodeConverter.ui")
w.connect(w.Browsepic, SIGNAL("released()"), browsePic)
w.connect(w.pushButton_2_Convert, SIGNAL("released()"), transform2Gcode)
#~ w.connect(w.pushButton_2_Convert, SIGNAL("released()"), drawGCode)
#~ w.connect(w.pushButton_close, SIGNAL("clicked()"), w.close)
w.pushButton_close.clicked.connect(w.close)

##GUI-Elements



w.show()


sys.exit(app.exec_())
