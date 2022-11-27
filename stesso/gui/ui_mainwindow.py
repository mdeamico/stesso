# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from .schematic_view import SchematicView

import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(926, 712)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QSize(16777215, 1024))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pbShowDialogOpen = QPushButton(self.centralwidget)
        self.pbShowDialogOpen.setObjectName(u"pbShowDialogOpen")

        self.horizontalLayout.addWidget(self.pbShowDialogOpen)

        self.pbBalance = QPushButton(self.centralwidget)
        self.pbBalance.setObjectName(u"pbBalance")

        self.horizontalLayout.addWidget(self.pbBalance)

        self.pbShowExportDialog = QPushButton(self.centralwidget)
        self.pbShowExportDialog.setObjectName(u"pbShowExportDialog")

        self.horizontalLayout.addWidget(self.pbShowExportDialog)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setStyleSheet(u"QSplitter::handle {\n"
"	image: url(:/theme/splitter_handle.png);\n"
"}")
        self.splitter.setFrameShape(QFrame.NoFrame)
        self.splitter.setFrameShadow(QFrame.Plain)
        self.splitter.setLineWidth(1)
        self.splitter.setMidLineWidth(0)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(10)
        self.gvSchematic = SchematicView(self.splitter)
        self.gvSchematic.setObjectName(u"gvSchematic")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.gvSchematic.sizePolicy().hasHeightForWidth())
        self.gvSchematic.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.gvSchematic)

        self.verticalLayout.addWidget(self.splitter)

        self.verticalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Jodeln", None))
        self.pbShowDialogOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.pbBalance.setText(QCoreApplication.translate("MainWindow", u"Balance", None))
        self.pbShowExportDialog.setText(QCoreApplication.translate("MainWindow", u"Export", None))
    # retranslateUi

