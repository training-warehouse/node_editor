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

        self.empty_icon = QIcon('.')

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

    def on_file_open(self):
        filenames, file_filter = QFileDialog.getOpenFileNames(self, 'Open graph form file')
        for filename in filenames:
            if os.path.isfile(filename):
                if filename:
                    exsting = self.find_mdi_child(filename)
                    if exsting:
                        self.mdi_area.setActiveSubWindow(exsting)
                    else:
                        node_editor = CalculatorSubWindow()
                        if node_editor.file_load(filename):
                            self.statusBar().showMessage('File %s loaded' % filename, 5000)
                            node_editor.set_title()
                            sub_window = self.create_mdi_child(node_editor)
                            sub_window.show()
                        else:
                            node_editor.close()

    def find_mdi_child(self, filename):
        for window in self.mdi_area.subWindowList():
            if window.widget().filename == filename:
                return window
        return None

    def on_file_new(self):
        sub_window = self.create_mdi_child()
        sub_window.show()

    def create_mdi_child(self, child_widget=None):
        node_editor = child_widget if child_widget is not None else CalculatorSubWindow()
        sub_window = self.mdi_area.addSubWindow(node_editor)
        sub_window.setWindowIcon(self.empty_icon)
        # node_editor.scene.add_item_selected_listener(self.update_edit_menu)
        # node_editor.scene.add_item_deselected_listener(self.update_edit_menu)
        node_editor.scene.history.add_history_modified_listener(self.update_edit_menu)
        node_editor.add_close_event_listener(self.on_sub_window_close)
        return sub_window

    def on_sub_window_close(self, widget, event):
        existing = self.find_mdi_child(widget.filename)
        self.mdi_area.setActiveSubWindow(existing)

        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

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

        self.edit_menu.aboutToShow.connect(self.update_edit_menu)

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
            action.setChecked(child is self.get_current_node_editor_widget())
            action.triggered.connect(self.window_mapper.map)
            self.window_mapper.setMapping(action, window)

    def get_current_node_editor_widget(self):
        activeSubWindow = self.mdi_area.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def update_menus(self):
        active = self.get_current_node_editor_widget()
        has_mdi_child = (active is not None)

        self.action_save.setEnabled(has_mdi_child)
        self.action_save_as.setEnabled(has_mdi_child)
        self.closeAct.setEnabled(has_mdi_child)
        self.closeAllAct.setEnabled(has_mdi_child)
        self.tileAct.setEnabled(has_mdi_child)
        self.cascadeAct.setEnabled(has_mdi_child)
        self.nextAct.setEnabled(has_mdi_child)
        self.previousAct.setEnabled(has_mdi_child)
        self.separatorAct.setEnabled(has_mdi_child)

        self.update_edit_menu()

    def update_edit_menu(self):
        active = self.get_current_node_editor_widget()
        has_mdi_child = (active is not None)

        self.action_paste.setEnabled(has_mdi_child)

        self.action_cut.setEnabled(has_mdi_child and active.has_selected_items())
        self.action_copy.setEnabled(has_mdi_child and active.has_selected_items())
        self.action_del.setEnabled(has_mdi_child and active.has_selected_items())

        self.action_undo.setEnabled(has_mdi_child and active.can_undo())
        self.action_redo.setEnabled(has_mdi_child and active.can_redo())

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
