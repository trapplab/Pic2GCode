# Picture2GCode
Einfaches graphisches Pythonprogramm, welches Bilder in GCode wandelt um mit einem Laserplotter zu verwenden.

Das Skript ist in der Python Version 3.5 programmiert worden.
Folgende zusätzliche Bibliotheken sind erforderlich:
- PyQt4
- Numpy
- PIL(Python Imaging Library)

# Update Summary Version 0.2
- GCode Generator überarbeitet. Besser GCode für neue grbl Version 1.1 mit Laser Mode
- Angepasste Standartwerte in Masske für Holzgravur


_**Tutorial:**_

![Oberfläche1](/pictures/Picture2GcodeTut1.png)

Beim starten des Skripts öffnet sich diese Oberfläche. In der Maske kann man die gewünschten Einstellungen vornehmen.


![Oberfläche2](/pictures/Picture2GCodeTut2)

Nach Auswahl des Fotos und Drücken des Convert-Buttons zeigt der Ladebalken den aktuellen Fortschritt an. Nach Abschluss wird die größe des Bildes in Pixel unten links angezeigt und der erzeugte G-Code im unteren Bild dargestellt. Hellblaue Linien sind dabei Wege bei denen der Laser ausgeschalten ist.
Die erzeugt *.ngc Datei wird dabei im selben Ordner gespeichert, in der sich das Skript befindet


Erstes Ergebniss:
![Ergebniss](/pictures/Resultat.jpg)
