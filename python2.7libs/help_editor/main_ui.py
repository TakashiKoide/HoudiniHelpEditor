# -*- coding: utf-8 -*-
import hou
from PySide2 import QtWidgets, QtGui, QtCore
import os
from . import indexed_text_edit
from . import help_base
from . import parameter_widget
from . import example_area
from . import command

reload(indexed_text_edit)
reload(help_base)
reload(parameter_widget)
reload(example_area)
reload(command)

from indexed_text_edit import IndexedTextEdit
from help_base import category_to_label
from parameter_widget import ParameterWidget
from example_area import ExampleArea

class TitleWidget(QtWidgets.QWidget):
    def paintEvent(self, event):
        hou_icon = hou.qt.Icon('MISC_logo')
        painter = QtGui.QPainter(self)
        rect = self.rect()
        painter.setBrush(QtCore.Qt.black)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(QtCore.QRectF(0, 0, rect.width(), rect.height()))

        painter.setPen(QtCore.Qt.white)
        font = QtGui.QFont('arial-black', 24, QtGui.QFont.Bold, False)
        painter.setFont(font)
        painter.drawText(QtCore.QPoint(16, 28), 'Houdini')
        painter.drawPixmap(124, 8, hou_icon.pixmap(20, 20))

class HelpCodeEditor(QtWidgets.QWidget):
    def __init__(self, help_text, parent=None):
        super(HelpCodeEditor, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('HelpCodeEditor')
        base_style = 'QWidget#HelpCodeEditor{background: 40,40,40}\n'
        self.setStyleSheet(base_style + hou.qt.styleSheet())
        self.help_text = help_text
        self.edit_text = QtWidgets.QTextEdit()
        self.edit_text.setPlainText(self.help_text)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.edit_text)
        self.setLayout(layout)

class NodeHelperUI(QtWidgets.QWidget):
    def __init__(self, node_type, parent=None):
        super(NodeHelperUI, self).__init__(parent)
        self.node_type = node_type
        self.setObjectName('HelpEditor')

        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        content_layout = QtWidgets.QVBoxLayout()

        title_widget = TitleWidget()
        title_widget.setFixedHeight(32)

        main_layout.addWidget(title_widget)

        node_label = self.node_type.description()
        node_type_label = QtWidgets.QLabel(node_label)
        node_type_label.setObjectName('NodeTypeLabel')

        node_category = self.node_type.category().name()
        category_label = QtWidgets.QLabel(category_to_label[node_category])
        category_label.setObjectName('CategoryLabel')

        node_icon_label = QtWidgets.QLabel('')
        node_icon_label.setFixedSize(QtCore.QSize(32, 32))
        node_name_layout = QtWidgets.QHBoxLayout()
        try:
            node_icon = hou.qt.Icon(self.node_type.icon())
            node_icon_label.setPixmap(node_icon.pixmap(32, 32))
        except:
            pass
        node_name_layout.addWidget(node_icon_label)
        node_name_layout.addWidget(node_type_label)
        node_name_layout.addWidget(category_label)
        node_name_layout.setStretch(2, 1)

        self.help_file = command.get_help_file_path(self.node_type)
        self.is_official = hou.getenv('HH') in self.help_file
        help_info = command.get_help_info_from_file(
            self.help_file, self.node_type)
        intro, description, parameters = help_info
        #Introduction Widget
        self.intro_widget = IndexedTextEdit('Overview', text=intro)
        self.intro_widget.setMinimumHeight(48)

        #Description Widget
        self.desc_widget = IndexedTextEdit('Description', description)
        self.desc_widget.setMinimumHeight(48)

        #Parameter Widget
        self.parm_widget = ParameterWidget(self.node_type, parameters)
        self.parm_data = self.parm_widget.parm_data

        self.example_area = ExampleArea(self.node_type)

        #Splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self)
        self.splitter.addWidget(self.intro_widget)
        self.splitter.addWidget(self.desc_widget)
        self.splitter.addWidget(self.parm_widget)
        self.splitter.addWidget(self.example_area)
        self.splitter.setHandleWidth(10)
        content_size = [72, 80, self.parm_widget.height(),
                        len(self.example_area.example_data) * 200]
        self.splitter.setSizes(content_size)
        self.splitter.setMinimumHeight(sum(content_size))

        #スクロールエリア内を一つにまとめるためのレイアウトとウィジェット
        inner_layout = QtWidgets.QVBoxLayout()
        inner_layout.addLayout(node_name_layout)
        inner_layout.addWidget(self.splitter)
        inner_layout.setContentsMargins(0, 10, 0, 10)
        inner_widget = QtWidgets.QWidget()
        inner_widget.setLayout(inner_layout)

        #Scroll Area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(inner_widget)
        self.scroll_area.setMinimumHeight(100)
        self.scroll_area.setStyleSheet('QScrollArea{border: none}')
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        #Button
        self.show_button = QtWidgets.QPushButton('Show Help Text')
        self.show_button.setFixedSize(QtCore.QSize(200, 32))

        self.export_button = QtWidgets.QPushButton('Export Help Text')
        self.export_button.setFixedSize(QtCore.QSize(200, 32))

        #Event
        self.show_button.clicked.connect(self.show_help_text)
        self.export_button.clicked.connect(self.export_help_text)
        self.parm_widget.v_header.sectionResized.connect(self.resize_splitter)
        self.splitter.splitterMoved.connect(self.adjust_splitter_size)

        #Layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.show_button)
        button_layout.addWidget(self.export_button)
        button_layout.setAlignment(self.show_button, QtCore.Qt.AlignRight)
        button_layout.setAlignment(self.export_button, QtCore.Qt.AlignRight)
        button_layout.setStretch(0, 1)

        content_layout.addWidget(self.scroll_area)
        content_layout.addLayout(button_layout)
        content_layout.insertSpacing(1, 8)
        content_layout.setContentsMargins(16, 10, 16, 10)

        main_layout.addLayout(content_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def adjust_splitter_size(self, pos, index):
        widget = self.splitter.widget(index - 1)
        if widget.__class__.__name__ != 'IndexedTextEdit':
            return
        old_height = widget.old_size.height()
        new_height = widget.new_size.height()
        self.resize_splitter(0, old_height, new_height)

    def show_help_text(self):
        intro = self.intro_widget.text
        desc = self.desc_widget.text
        desc = '\n'.join(desc.splitlines())
        if self.is_official:
            help_text = command.get_help_file_text(self.help_file,
                                                   splitlines=False)
        else:
            example_data = self.example_area.example_data
            help_text = command.get_help_text(self.node_type, intro, desc,
                                              self.parm_data, example_data)

        help_editor = HelpCodeEditor(help_text, parent=self)
        help_editor.resize(600, 800)
        help_editor.show()

    def export_help_text(self):
        intro = self.intro_widget.text
        desc = self.desc_widget.text
        desc = '\n'.join(desc.splitlines())
        example_data = self.example_area.example_data

        help_text = command.get_help_text(self.node_type, intro, desc,
                                          self.parm_data, example_data)
        export = command.export_help_text(self.node_type, help_text)
        command.export_example_text(self.example_area.example_data)
        if export:
            hou.ui.displayNodeHelp(self.node_type)

    def resize_splitter(self, row, old_height, new_height):
        offset = new_height - old_height
        height = self.splitter.height()
        self.splitter.setMinimumHeight(height + offset)

class MainWindow(QtWidgets.QTabWidget):
    def __init__(self, node_types, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Help Editor')
        self.setObjectName('HelpEditor')
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.remove_tab)
        self.script_path = os.path.dirname(__file__)
        style_file = self.script_path + '/style.qss'
        with open(style_file, 'r') as f:
            style = f.read()
        self.setStyleSheet(style)
        self.node_types = node_types
        for node_type in node_types:
            widget = NodeHelperUI(node_type, parent=self)
            label = node_type.description()
            self.addTab(widget, label)
        self.resize(600, 800)

    def remove_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
        else:
            self.close()

    def show_window(self):
        main_window = hou.qt.mainWindow()
        self.setParent(main_window, QtCore.Qt.Window)
        self.show()

    def closeEvent(self, event):
        self.deleteLater()