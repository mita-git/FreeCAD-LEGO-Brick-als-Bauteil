# coding: UTF-8
"""
FCDialog.py -- 
-- Michael Talarczyk, 2025-11-02 2026-01-03 auch mit spire
The goal is to make Lego-compatible pieces for use in 3D printer
The script generates .stl files in a directory.
"""

import sys
import FreeCAD
from FreeCAD import Console, Gui
from PySide2.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QSpinBox, QComboBox, QPushButton
from PySide2.QtCore import Qt


class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        
        self.setWindowTitle("Mita Brick Macro")

        layout = QVBoxLayout()

        # Breite des Bricks
        self.breite_label = QLabel("Breite des Bricks (LEGO Stud):")
        self.breite_spinbox = QSpinBox()
        self.breite_spinbox.setRange(1, 20)
        self.breite_spinbox.setValue(2)
        layout.addWidget(self.breite_label)
        layout.addWidget(self.breite_spinbox)

        # Länge des Bricks
        self.laenge_label = QLabel("Länge des Bricks  (LEGO Stud):")
        self.laenge_spinbox = QSpinBox()
        self.laenge_spinbox.setRange(1, 20)
        self.laenge_spinbox.setValue(6)
        layout.addWidget(self.laenge_label)
        layout.addWidget(self.laenge_spinbox)

        # Höhe des Bricks
        self.hoehe_label = QLabel("Höhe des Bricks  (LEGO Plate):")
        self.hoehe_spinbox = QSpinBox()
        self.hoehe_spinbox.setRange(1, 9)
        self.hoehe_spinbox.setValue(3)
        layout.addWidget(self.hoehe_label)
        layout.addWidget(self.hoehe_spinbox)

        # Stubs in x
        self.stubs_label = QLabel("Wie viele Studs (-> x) stehen bleiben sollen beim Dachstein:")
        self.stubs_spinbox = QSpinBox()
        self.stubs_spinbox.setRange(0, 100)
        self.stubs_spinbox.setValue(1)
        layout.addWidget(self.stubs_label)
        layout.addWidget(self.stubs_spinbox)

        # Auswahlbox
        self.auswahl_label = QLabel("Auswahl:")
        self.auswahl_combobox = QComboBox()
        self.auswahl_combobox.addItems([ "brick", "plate", "tile", "slope","dslope", "qslope", "spire"])
        layout.addWidget(self.auswahl_label)
        layout.addWidget(self.auswahl_combobox)

        # Buttons
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Abbrechen")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def getValues(self):
        return [
            self.breite_spinbox.value(),
            self.laenge_spinbox.value(),
            self.hoehe_spinbox.value(),
            self.stubs_spinbox.value(),
            self.auswahl_combobox.currentText()
        ]


# # if __name__ == "__main__":
# #    app = QApplication(sys.argv)
# dialog = Dialog()
# 
# if dialog.exec() == QDialog.Accepted:
#     values = dialog.getValues()
#     print("Die Werte:")
#     print(values)
# else:
#     print("Dialog wurde abgebrochen.")
# 
# # Ensure the application exits
# # sys.exit()
