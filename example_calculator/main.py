# -*- coding: utf-8 -*-
# Time    : 2020/12/10 20:32
# Author  : LiaoKong

from PySide2.QtWidgets import *
from example_calculator.calc_window import CalculatorWindow

if __name__ == '__main__':
    app =QApplication([])

    print(QStyleFactory.keys())
    app.setStyle('Fusion')
    window = CalculatorWindow()
    window.show()

    app.exec_()


