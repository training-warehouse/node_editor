# -*- coding: utf-8 -*-
# Time    : 2020/12/19 15:17
# Author  : LiaoKong
import os

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from node_editor.node_editor_window import NodeEditorWindow
from example_calculator.calc_sub_window import CalculatorSubWindow
from node_editor.utils import load_stylesheet
import example_calculator.qss.nodeeditor_dark_resources


class CalculatorWindow(NodeEditorWindow):
    def init_ui(self):
        self.name_company = 'LiaoKong'
        self.name_product = 'Calculator NodeEditor'

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), 'qss/nodeeditor.qss')
        load_stylesheet(
            os.path.join(os.path.dirname(__file__), 'qss/nodeeditor-dark.qss'),
            self.stylesheet_filename
        )

        self.mdi_area = QMdiArea()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setViewMode(QMdiArea.TabbedView)
        self.mdi_area.setDocumentMode(True)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)
        self.setCentralWidget(self.mdi_area)

        self.mdi_area.subWindowActivated.connect(self.update_menus)
        self.window_mapper = QSignalMapper(self)
        self.window_mapper.mapped[QWidget].connect(self.set_active_sub_window)

        self.create_actions()
        self.create_menus()
        self.create_tool_bars()
        self.create_status_bar()
        self.update_menus()

        self.create_node_dock()
        self.read_settings()

        self.setWindowTitle("Calculator NodeEditor")

    def create_actions(self):
        super(CalculatorWindow, self).create_actions()
        self.closeAct = QAction("Cl&ose", self,
                                statusTip="Close the active window",
                                triggered=self.mdi_area.closeActiveSubWindow)

        self.closeAllAct = QAction("Close &All", self,
                                   statusTip="Close all the windows",
                                   triggered=self.mdi_area.closeAllSubWindows)

        self.tileAct = QAction("&Tile", self, statusTip="Tile the windows",
                               triggered=self.mdi_area.tileSubWindows)

        self.cascadeAct = QAction("&Cascade", self,
                                  statusTip="Cascade the windows",
                                  triggered=self.mdi_area.cascadeSubWindows)

        self.nextAct = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild,
                               statusTip="Move the focus to the next window",
                               triggered=self.mdi_area.activateNextSubWindow)

        self.previousAct = QAction("Pre&vious", self,
                                   shortcut=QKeySequence.PreviousChild,
                                   statusTip="Move the focus to the previous window",
                                   triggered=self.mdi_area.activatePreviousSubWindow)

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction("&About", self,
                                statusTip="Show the application's About box",
                                triggered=self.about)

    def on_file_new(self):
        sub_window = self.create_mdi_child()
        sub_window.show()

    def create_mdi_child(self):
        node_editor = CalculatorSubWindow()
        sub_window = self.mdi_area.addSubWindow(node_editor)
        return sub_window

    def about(self):
        QMessageBox.about(self, "About MDI",
                          "The <b>MDI</b> example demonstrates how to write multiple "
                          "document interface applications using Qt.")

    def create_menus(self):
        super(CalculatorWindow, self).create_menus()
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdi_area.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.get_user_friendly_filename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.window_mapper.map)
            self.window_mapper.setMapping(action, window)

    def update_menus(self):
        pass

    def create_tool_bars(self):
        pass

    def create_status_bar(self):
        pass

    def create_node_dock(self):
        self.list_widget = QListWidget()
        self.list_widget.addItems(['Add', 'Substract', 'Multiply', 'Divide'])

        self.items = QDockWidget('Nodes')
        self.items.setWidget(self.list_widget)
        self.items.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.items)

    def set_active_sub_window(self, window):
        if window:
            self.mdi_area.setActiveSubWindow(window)

    def closeEvent(self, event):
        self.mdi_area.closeAllSubWindows()
        if self.mdi_area.currentSubWindow():
            event.ignore()
        else:
            self.write_settings()
            event.accept()

    def activeMdiChild(self):
        activeSubWindow = self.mdi_area.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None
