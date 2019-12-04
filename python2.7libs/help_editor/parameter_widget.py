# -*- coding: utf-8 -*-
from PySide2 import QtWidgets, QtGui, QtCore
from . import command

class ParameterHeaderView(QtWidgets.QHeaderView):
    def __init__(self, items):
        super(ParameterHeaderView, self).__init__(QtCore.Qt.Vertical)
        self.items = items

    def paintSection(self, painter, rect, index):
        parm_info = self.items[index]
        label = parm_info['label']
        is_folder = parm_info.get('folder')

        painter.translate(rect.left(), rect.top())
        if is_folder:
            painter.setBrush(QtCore.Qt.white)
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(242, 242, 242)))
        painter.setPen(QtCore.Qt.NoPen)
        r = QtCore.QRect(0, 1, rect.width() - 1, rect.height() - 2)
        painter.drawRect(r)
        r.setX(4)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r, QtCore.Qt.AlignVCenter, label)

class ParameterDescriptionWidget(QtWidgets.QTextEdit):
    def __init__(self, row, description, parent=None):
        super(ParameterDescriptionWidget, self).__init__(description, parent)
        self.row = row
        self.setAcceptRichText(False)
        self.setPlainText(description)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet('QTextEdit{border: none}')

class ParameterItem(QtGui.QStandardItem):
    def __init__(self, info):
        super(ParameterItem, self).__init__('')
        self.info = info

class ParameterListModel(QtGui.QStandardItemModel):
    def __init__(self, items, view):
        super(ParameterListModel, self).__init__()
        self.items = items
        self.view = view
        self.header_labels = [item['label'] for item in items]
        self.setVerticalHeaderLabels(self.header_labels)
        self.setColumnCount(1)
        self.setRowCount(len(self.items))

    def set_list_items(self):
        for row, parm_info in enumerate(self.items):
            is_folder = parm_info.get('folder')
            desc = parm_info['desc']
            item = ParameterItem(parm_info)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(row, 0, item)
            if not is_folder:
                parm_desc_widget = ParameterDescriptionWidget(row, desc)
                parm_desc_widget.textChanged.connect(self.change_description)
                self.view.setIndexWidget(item.index(), parm_desc_widget)
            self.resize_text_area(row, desc)

    def resize_text_area(self, row, text):
        lines = text.splitlines()
        line_count = len(lines)
        height = 28
        if line_count:
            height = line_count * 20 + 8
        if self.view.rowHeight(row) < height:
            self.view.setRowHeight(row, height)

    def change_description(self):
        edit_text = self.sender()
        desc = edit_text.toPlainText()
        row = edit_text.row
        item = self.item(row, 0)
        item.info['desc'] = desc
        self.resize_text_area(row, desc)

    def refresh(self):
        self.removeRows(0, self.rowCount())
        self.setRowCount(len(self.items))
        self.set_list_items()

class ParameterWidget(QtWidgets.QWidget):
    def __init__(self, node_type, parameters, parent=None):
        super(ParameterWidget, self).__init__(parent)
        self.node_type = node_type
        self.parameters = parameters
        self.init_ui()

    def init_ui(self):
        parm_label = QtWidgets.QLabel('Parameters')
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)

        #Parameter Widget
        self.parm_data = command.get_parm_data(self.node_type, self.parameters)
        self.parm_view = QtWidgets.QTableView()
        self.parm_view.setShowGrid(False)
        self.v_header = ParameterHeaderView(self.parm_data)
        self.parm_view.setVerticalHeader(self.v_header)
        self.parm_view.setSelectionBehavior(self.parm_view.SelectItems)
        self.parm_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.parm_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.model = ParameterListModel(self.parm_data, self.parm_view)
        self.parm_view.setModel(self.model)
        self.model.set_list_items()

        h_header = self.parm_view.horizontalHeader()
        h_header.setVisible(False)
        h_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(parm_label)
        layout.addWidget(separator)
        layout.addWidget(self.parm_view)
        layout.insertSpacing(2, 16)
        layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(layout)
        self.adjust_height()
        self.v_header.sectionResized.connect(self.resize_height)

    def adjust_height(self):
        total_height = 0
        row_count = self.model.rowCount()
        for row in range(row_count):
            height = self.parm_view.rowHeight(row)
            total_height += height
        self.parm_view.setFixedHeight(total_height)
        self.setFixedHeight(total_height + 64)

    def resize_height(self, row, old_height, new_height):
        offset = new_height - old_height
        view_height = self.parm_view.height()
        height  = self.height()
        self.parm_view.setFixedHeight(view_height + offset)
        self.setFixedHeight(height + offset)