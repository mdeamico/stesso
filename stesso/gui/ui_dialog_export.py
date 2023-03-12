# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_export.ui'
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
        Dialog.resize(575, 103)
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pbExportFolder = QPushButton(Dialog)
        self.pbExportFolder.setObjectName(u"pbExportFolder")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.pbExportFolder)

        self.leExportFolder = QLineEdit(Dialog)
        self.leExportFolder.setObjectName(u"leExportFolder")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.leExportFolder)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pbExport = QPushButton(Dialog)
        self.pbExport.setObjectName(u"pbExport")

        self.verticalLayout.addWidget(self.pbExport)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout_2.addWidget(self.buttonBox)

        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Export", None))
        self.pbExportFolder.setText(QCoreApplication.translate("Dialog", u"Export Folder", None))
#if QT_CONFIG(tooltip)
        self.pbExport.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.pbExport.setText(QCoreApplication.translate("Dialog", u"Export Links and Turns", None))
    # retranslateUi

