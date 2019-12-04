# -*- coding: utf-8 -*-
from PySide2 import QtWidgets, QtCore

class IndexedTextEdit(QtWidgets.QWidget):
    textChanged = QtCore.Signal(str)
    def __init__(self, index, text='', parent=None):
        super(IndexedTextEdit, self).__init__(parent=parent)
        self.index = index
        self.text = text
        index_label = QtWidgets.QLabel(self.index)
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setStyleSheet('QTextEdit{background: white}')
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setPlainText(self.text)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(index_label)
        layout.addWidget(self.text_edit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.text_edit.textChanged.connect(self.emit_text_changed)

    def emit_text_changed(self):
        text = self.text_edit.toPlainText()
        self.text = text
        self.textChanged.emit(text)

    def resizeEvent(self, event):
        self.old_size = event.oldSize()
        self.new_size = event.size()