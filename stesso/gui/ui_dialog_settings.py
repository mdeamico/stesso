# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_settings.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 69)
        self.formLayout = QFormLayout(Dialog)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.sldTMViz = QSlider(Dialog)
        self.sldTMViz.setObjectName(u"sldTMViz")
        self.sldTMViz.setMinimum(1)
        self.sldTMViz.setMaximum(100)
        self.sldTMViz.setValue(8)
        self.sldTMViz.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.sldTMViz)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Settings", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Turning Movement Label Visibility", None))
    # retranslateUi

