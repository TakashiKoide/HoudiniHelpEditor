# -*- coding: utf-8 -*-
from PySide2 import QtWidgets, QtGui, QtCore
import hou
import subprocess
import os
import glob
import sys
import codecs
from . import command
from .indexed_text_edit import IndexedTextEdit

def get_example_path(node_type):
    u"""
    指定したノードタイプからhdaファイルのパスを取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    hda_file : string
        hdaファイルのパス。
    """
    hda_file = command.get_hda_file_path(node_type)
    if not hda_file:
        return []
    file_path = os.path.dirname(hda_file)
    context = command.get_context(node_type)
    node_name = command.get_node_name(node_type)
    example_path = '{}/help/examples/nodes/{}/{}'.format(
        os.path.dirname(file_path),
        context,
        node_name)
    return example_path

class ExampleWidget(QtWidgets.QWidget):
    def __init__(self, hda_file, parent=None):
        super(ExampleWidget, self).__init__(parent)
        self.hda_file = hda_file
        self.help_path = '/'.join(os.path.normpath(hda_file).split(os.sep)[:-5])
        self.hda_def = hou.hda.definitionsInFile(self.hda_file)[0]
        self.hda_name = os.path.basename(hda_file).split('.')[0]
        self.hda_label = self.hda_def.description()
        self.desc_file = hda_file.replace('.hda', '.txt')
        self.desc_text = ''
        if os.path.exists(self.desc_file):
            with codecs.open(self.desc_file, 'r', 'utf-8') as f:
                lines = [line.lstrip() for line in f.readlines()]
                self.desc_text = ''.join(lines)
        self.example_info = {}
        self.example_info['example_file'] = self.desc_file
        self.example_info['example_name'] = self.hda_name
        self.example_info['example_label'] = self.hda_label
        self.example_info['example_desc'] = self.desc_text

        self.init_ui()

    def init_ui(self):
        load_button = QtWidgets.QPushButton('Load')
        load_button.setFixedHeight(32)

        launch_button = QtWidgets.QPushButton('Launch')
        launch_button.setFixedHeight(32)
        launch_button.setObjectName('LaunchButton')

        self.desc_edit = IndexedTextEdit(self.hda_label, text=self.desc_text)
        self.desc_edit.setMinimumHeight(48)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(load_button)
        main_layout.addWidget(launch_button)
        main_layout.addWidget(self.desc_edit)
        main_layout.setAlignment(load_button, QtCore.Qt.AlignTop)
        main_layout.setAlignment(launch_button, QtCore.Qt.AlignTop)
        main_layout.setSpacing(20)

        self.setLayout(main_layout)

        load_button.clicked.connect(self.load_hda)
        launch_button.clicked.connect(self.launch_hda)
        self.desc_edit.textChanged.connect(self.edit_description)

    def load_hda(self):
        import houdinihelp
        rel_path = os.path.relpath(self.hda_file, self.help_path)
        houdinihelp.load_example(rel_path.replace(os.sep, '/'))

    def launch_hda(self):
        import houdinihelp
        rel_path = os.path.relpath(self.hda_file, self.help_path)
        houdinihelp.load_example(rel_path.replace(os.sep, '/'), launch=True)

    def edit_description(self, text):
        self.desc_text = text
        self.example_info['example_desc'] = text

class ExampleArea(QtWidgets.QWidget):
    def __init__(self, node_type, parent=None):
        super(ExampleArea, self).__init__(parent)
        self.node_type = node_type
        self.example_data = []
        self.example_path = get_example_path(self.node_type)
        if not self.example_path:
            return
        hda_files = glob.glob(self.example_path + '/*.hda')
        widgets = []
        for hda_file in hda_files:
            hda_def = hou.hda.definitionsInFile(hda_file)[0]
            category = hda_def.nodeTypeCategory().name()
            if category != 'Object':
                continue
            example_widget = ExampleWidget(hda_file)
            self.example_data.append(example_widget.example_info)
            widgets.append(example_widget)

        if not self.example_data:
            return

        example_label = QtWidgets.QLabel('Examples')
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 10, 0, 10)
        main_layout.addWidget(example_label)
        main_layout.addWidget(separator)
        for example_widget in widgets:
            main_layout.addWidget(example_widget)
        main_layout.insertSpacing(2, 16)
        self.setLayout(main_layout)
