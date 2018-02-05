Anwendungsverlauf
=================
SmartRecord ermoeglicht es Versuche automatisiert aufzunehmen und 
diese auszuwerten. Da die Funktionalitaeten der Applikation davon abhaengen, 
ob eine Messkarte angeschlossen ist, gibt es die zwei Modi Aufnahmemodus und 
Auswertemodus. Der Aufnahmemodus ermoeglicht es im Gegensatz zum 
Auswertemodus die Funktionalitaeten der Messkarte und der Kamera zu nutzen. 

Aufnahmemodus
-------------
Wenn die Messkarte am Computer angeschlossen ist und vom Programm erkannt wird, 
startet das Programm im Aufnahmemodus. Beim Starten des Programms wird versucht 
eine Verbindung zum Server aufzubauen. Falls keine Verbindung aufgebaut werden 
kann, ist der Server nicht erreichbar oder die Serverkonfiguration ist nicht 
korrekt eingestellt. In diesem Fall kann diese über das Menu Configuration 
konfiguriert werden und ein erneuter Versuch sich mit Server zu verbinden 
gestartet werden. Um die Kamera mit der Applikation ansteuern zu koennen, 
muss diese zuvor mit dem Computer per WLAN verbunden werden. Sobald eine 
Verbindung mit dem Computer aufgebaut wurde, wird dieser eine IP zugeordnet, 
welche in der Applikation eingetragen werden muss. Der Verbindung wird in der 
Regel die IP-Adresse 192.168.0.1 zugewiesen. Fuer die Versuchsaufnahme werden 
mindestens ein Input-Port und ein Output-Port benoetigt. Dabei ist zu beachten, 
dass derzeit nur ein Output-Port hinzugefuegt werden kann, der alle 
Ausgangskanaele zeitgleich ausloest. 

.. figure:: tutorial/Anwendungsverlauf/Aufnahmemodus/externe.png
   :scale: 70 %
   :alt: map to buried treasure

Um den Versuchsablauf zu definieren, muss mindestens eine Phase 
hinzugefuegt werden. Die Phasen legen fest, wann ein Bild aufgezeichnet 
werden soll. Zurzeit koennen folgende Phasen hinzugefuegt werden:
	- Value-phase  (Wertbasierte Phase)
	- Time-phase  (Zeitbasierte Phase)
	- Pause-phase (Phase wo keine Aufnahmen erfolgen)
	- Cycle (Eine Folge von Phasen, die n-mal wiederholt)

.. figure:: tutorial/Anwendungsverlauf/Aufnahmemodus/versuchsablauf.png
   :scale: 70 %
   :alt: map to buried treasure

Da die Versuche im Nachhinein eindeutig identifiziert werden sollen, 
muessen die Versuchseigenschaften entsprechend festgelegt werden. Durch 
den Typ und der Serie wird festgelegt, in welchem Ordner der Versuch 
abgelegt wird. 

.. figure:: tutorial/Anwendungsverlauf/Aufnahmemodus/versuchseigenschaften.png
   :scale: 70 %
   :alt: map to buried treasure

Hier koennen die Korrelationseigenschaften festgelegt werden, wobei diese 
wenig Verwendung finden, da derzeit kein Rechenserver zur Verfuegung steht. 

.. figure:: tutorial/Anwendungsverlauf/Aufnahmemodus/korrelationseigenschaften.png
   :scale: 70 %
   :alt: map to buried treasure

Nach der erfolgreichen Versuchsdurchführung koennen die Aufzeichnungen lokal 
abgespeichert werden. Falls der Versuch im Online-Modus durchgeführt wird, 
werden die Daten auf dem Server automatisch waehrend der Aufzeichnung abgelegt, 
sodass auf dem Server ein Backup existiert. 

.. figure:: tutorial/Anwendungsverlauf/Aufnahmemodus/aufnahme_fertig.png
   :scale: 70 %
   :alt: map to buried treasure

Auswertemodus
-------------
Im Auswertemodus koennen bereits durchgeführte Versuche lokal oder vom 
Server geladen werden. Derzeit kann die digitale Bildkorrelation nicht von 
dem Programm durchgeführt werden, weshalb es eine Funktion gibt, die das 
Importieren von externen Ergebnissen ermoeglicht. Die Dateien werden in der 
folgenden Reihenfolge eingelesen:
	- U-Displacements
	- V-Displacements
	- Strain-exx
	- Strain-exy
	- Strain-eyy

.. figure:: tutorial/Anwendungsverlauf/Auswertemodus/ergebnisse_einlesen.png
   :scale: 70 %
   :alt: map to buried treasure

Anschließend werden die Ergebnisse graphisch dargestellt und die Dehnungen 
in Abhängigkeit vom ausgewaehlten Wert angezeigt. 

.. figure:: tutorial/Anwendungsverlauf/Auswertemodus/bilder_generieren.png
   :scale: 70 %
   :alt: map to buried treasure

Fuer eine genauere Versuchsauswertung koennen virtuelle Wegaufnehmer auf 
den Aufnahmen platziert werden, welche ueber die Bildreihe hinweg verfolgt 
werden. Durch den Radius kann die Anzahl der betrachten Subsets in einem Kreis 
festgelegt werden. Je mehr Subsets ausgewaehlt werden, desto stabiler sind 
die Ergebnisse.

.. figure:: tutorial/Anwendungsverlauf/Auswertemodus/wegaufnehmer.png
   :scale: 70 %
   :alt: map to buried treasure

Schließlich koennen die aufgezeichneten Werte betrachtet und abgespeichert 
werden.

.. figure:: tutorial/Anwendungsverlauf/Auswertemodus/ergebnisse_anzeigen.png
   :scale: 70 %
   :alt: map to buried treasure