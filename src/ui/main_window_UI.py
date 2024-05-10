# Form implementation generated from reading ui file 'src/ui/main_window.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(934, 862)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox_reporting = QtWidgets.QComboBox(parent=self.groupBox)
        self.comboBox_reporting.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.comboBox_reporting.setObjectName("comboBox_reporting")
        self.gridLayout.addWidget(self.comboBox_reporting, 0, 0, 1, 1)
        self.lineEdit_reporting = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEdit_reporting.setReadOnly(True)
        self.lineEdit_reporting.setObjectName("lineEdit_reporting")
        self.gridLayout.addWidget(self.lineEdit_reporting, 0, 1, 1, 1)
        self.tabWidget_reporting = QtWidgets.QTabWidget(parent=self.groupBox)
        self.tabWidget_reporting.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.tabWidget_reporting.setObjectName("tabWidget_reporting")
        self.tab_process = QtWidgets.QWidget()
        self.tab_process.setObjectName("tab_process")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_process)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser_process = QtWidgets.QTextBrowser(parent=self.tab_process)
        self.textBrowser_process.setObjectName("textBrowser_process")
        self.verticalLayout.addWidget(self.textBrowser_process)
        self.tabWidget_reporting.addTab(self.tab_process, "")
        self.tab_tables = QtWidgets.QWidget()
        self.tab_tables.setObjectName("tab_tables")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_tables)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableWidget_tables = QtWidgets.QTableWidget(parent=self.tab_tables)
        self.tableWidget_tables.setObjectName("tableWidget_tables")
        self.tableWidget_tables.setColumnCount(0)
        self.tableWidget_tables.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget_tables)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget_reporting.addTab(self.tab_tables, "")
        self.tab_query = QtWidgets.QWidget()
        self.tab_query.setObjectName("tab_query")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_query)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_query_clear = QtWidgets.QPushButton(parent=self.tab_query)
        self.pushButton_query_clear.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.pushButton_query_clear.setObjectName("pushButton_query_clear")
        self.gridLayout_2.addWidget(self.pushButton_query_clear, 2, 1, 1, 1)
        self.pushButton_query_ok = QtWidgets.QPushButton(parent=self.tab_query)
        self.pushButton_query_ok.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.pushButton_query_ok.setObjectName("pushButton_query_ok")
        self.gridLayout_2.addWidget(self.pushButton_query_ok, 2, 2, 1, 1)
        self.textEdit_query = QtWidgets.QTextEdit(parent=self.tab_query)
        self.textEdit_query.setObjectName("textEdit_query")
        self.gridLayout_2.addWidget(self.textEdit_query, 1, 0, 1, 3)
        self.label_query = QtWidgets.QLabel(parent=self.tab_query)
        self.label_query.setObjectName("label_query")
        self.gridLayout_2.addWidget(self.label_query, 0, 0, 1, 3)
        spacerItem1 = QtWidgets.QSpacerItem(695, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 2, 0, 1, 1)
        self.tableWidget_query = QtWidgets.QTableWidget(parent=self.tab_query)
        self.tableWidget_query.setObjectName("tableWidget_query")
        self.tableWidget_query.setColumnCount(0)
        self.tableWidget_query.setRowCount(0)
        self.gridLayout_2.addWidget(self.tableWidget_query, 3, 0, 1, 3)
        self.gridLayout_2.setRowStretch(1, 1)
        self.gridLayout_2.setRowStretch(3, 3)
        self.tabWidget_reporting.addTab(self.tab_query, "")
        self.gridLayout.addWidget(self.tabWidget_reporting, 1, 0, 1, 2)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.verticalLayout_3.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 934, 20))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menu_postgresql = QtWidgets.QMenu(parent=self.menuHelp)
        self.menu_postgresql.setObjectName("menu_postgresql")
        self.menuFMP_Database = QtWidgets.QMenu(parent=self.menubar)
        self.menuFMP_Database.setObjectName("menuFMP_Database")
        self.menu_fetch_initial_data = QtWidgets.QMenu(parent=self.menuFMP_Database)
        self.menu_fetch_initial_data.setObjectName("menu_fetch_initial_data")
        self.menu_key_metrics = QtWidgets.QMenu(parent=self.menu_fetch_initial_data)
        self.menu_key_metrics.setObjectName("menu_key_metrics")
        self.menu_daily_chart = QtWidgets.QMenu(parent=self.menu_fetch_initial_data)
        self.menu_daily_chart.setObjectName("menu_daily_chart")
        self.menu_index_constituents = QtWidgets.QMenu(parent=self.menu_fetch_initial_data)
        self.menu_index_constituents.setObjectName("menu_index_constituents")
        self.menuTools = QtWidgets.QMenu(parent=self.menubar)
        self.menuTools.setObjectName("menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionPostgreSQL = QtGui.QAction(parent=MainWindow)
        self.actionPostgreSQL.setObjectName("actionPostgreSQL")
        self.actionTimescaleDB = QtGui.QAction(parent=MainWindow)
        self.actionTimescaleDB.setObjectName("actionTimescaleDB")
        self.action_timescaledb_install = QtGui.QAction(parent=MainWindow)
        self.action_timescaledb_install.setObjectName("action_timescaledb_install")
        self.action_create_tables = QtGui.QAction(parent=MainWindow)
        self.action_create_tables.setObjectName("action_create_tables")
        self.action_fetch_stock_symbols = QtGui.QAction(parent=MainWindow)
        self.action_fetch_stock_symbols.setObjectName("action_fetch_stock_symbols")
        self.action_fetch_company_profile = QtGui.QAction(parent=MainWindow)
        self.action_fetch_company_profile.setObjectName("action_fetch_company_profile")
        self.action_fetch_dividend = QtGui.QAction(parent=MainWindow)
        self.action_fetch_dividend.setObjectName("action_fetch_dividend")
        self.action_update_stoxx_europe = QtGui.QAction(parent=MainWindow)
        self.action_update_stoxx_europe.setObjectName("action_update_stoxx_europe")
        self.action_update_dividend = QtGui.QAction(parent=MainWindow)
        self.action_update_dividend.setObjectName("action_update_dividend")
        self.action_update_key_metrics = QtGui.QAction(parent=MainWindow)
        self.action_update_key_metrics.setObjectName("action_update_key_metrics")
        self.action_update_daily_chart = QtGui.QAction(parent=MainWindow)
        self.action_update_daily_chart.setObjectName("action_update_daily_chart")
        self.actionAll = QtGui.QAction(parent=MainWindow)
        self.actionAll.setObjectName("actionAll")
        self.actionStock_symbols_2 = QtGui.QAction(parent=MainWindow)
        self.actionStock_symbols_2.setObjectName("actionStock_symbols_2")
        self.actionSTOXX_Europe_602 = QtGui.QAction(parent=MainWindow)
        self.actionSTOXX_Europe_602.setObjectName("actionSTOXX_Europe_602")
        self.actionCompany_profile_2 = QtGui.QAction(parent=MainWindow)
        self.actionCompany_profile_2.setObjectName("actionCompany_profile_2")
        self.actionDividend_3 = QtGui.QAction(parent=MainWindow)
        self.actionDividend_3.setObjectName("actionDividend_3")
        self.actionKey_metrics_3 = QtGui.QAction(parent=MainWindow)
        self.actionKey_metrics_3.setObjectName("actionKey_metrics_3")
        self.actionDaily_cahrt = QtGui.QAction(parent=MainWindow)
        self.actionDaily_cahrt.setObjectName("actionDaily_cahrt")
        self.actionQuery = QtGui.QAction(parent=MainWindow)
        self.actionQuery.setObjectName("actionQuery")
        self.action_create_new_database = QtGui.QAction(parent=MainWindow)
        self.action_create_new_database.setObjectName("action_create_new_database")
        self.action_postgresql_install = QtGui.QAction(parent=MainWindow)
        self.action_postgresql_install.setObjectName("action_postgresql_install")
        self.action_postgresql_update = QtGui.QAction(parent=MainWindow)
        self.action_postgresql_update.setObjectName("action_postgresql_update")
        self.action_report_tables = QtGui.QAction(parent=MainWindow)
        self.action_report_tables.setObjectName("action_report_tables")
        self.action_env_file = QtGui.QAction(parent=MainWindow)
        self.action_env_file.setObjectName("action_env_file")
        self.action_chart_window = QtGui.QAction(parent=MainWindow)
        self.action_chart_window.setObjectName("action_chart_window")
        self.action_finance_window = QtGui.QAction(parent=MainWindow)
        self.action_finance_window.setObjectName("action_finance_window")
        self.action_fetch_key_metrics_quarter = QtGui.QAction(parent=MainWindow)
        self.action_fetch_key_metrics_quarter.setObjectName("action_fetch_key_metrics_quarter")
        self.action_fetch_key_metrics_annual = QtGui.QAction(parent=MainWindow)
        self.action_fetch_key_metrics_annual.setObjectName("action_fetch_key_metrics_annual")
        self.action_backup = QtGui.QAction(parent=MainWindow)
        self.action_backup.setObjectName("action_backup")
        self.action_historical_daily_chart = QtGui.QAction(parent=MainWindow)
        self.action_historical_daily_chart.setObjectName("action_historical_daily_chart")
        self.action_update_daily_chart_ = QtGui.QAction(parent=MainWindow)
        self.action_update_daily_chart_.setObjectName("action_update_daily_chart_")
        self.action_fetch_stoxx_600 = QtGui.QAction(parent=MainWindow)
        self.action_fetch_stoxx_600.setObjectName("action_fetch_stoxx_600")
        self.action_fetch_dow_jones = QtGui.QAction(parent=MainWindow)
        self.action_fetch_dow_jones.setObjectName("action_fetch_dow_jones")
        self.action_fetch_sp_500 = QtGui.QAction(parent=MainWindow)
        self.action_fetch_sp_500.setObjectName("action_fetch_sp_500")
        self.action_fetch_nasdaq = QtGui.QAction(parent=MainWindow)
        self.action_fetch_nasdaq.setObjectName("action_fetch_nasdaq")
        self.menu_postgresql.addAction(self.action_postgresql_install)
        self.menu_postgresql.addAction(self.action_postgresql_update)
        self.menuHelp.addAction(self.menu_postgresql.menuAction())
        self.menuHelp.addAction(self.action_timescaledb_install)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.action_env_file)
        self.menu_key_metrics.addAction(self.action_fetch_key_metrics_quarter)
        self.menu_key_metrics.addAction(self.action_fetch_key_metrics_annual)
        self.menu_daily_chart.addAction(self.action_historical_daily_chart)
        self.menu_daily_chart.addAction(self.action_update_daily_chart_)
        self.menu_index_constituents.addAction(self.action_fetch_dow_jones)
        self.menu_index_constituents.addAction(self.action_fetch_sp_500)
        self.menu_index_constituents.addAction(self.action_fetch_nasdaq)
        self.menu_index_constituents.addAction(self.action_fetch_stoxx_600)
        self.menu_fetch_initial_data.addAction(self.action_fetch_stock_symbols)
        self.menu_fetch_initial_data.addAction(self.action_fetch_company_profile)
        self.menu_fetch_initial_data.addAction(self.menu_index_constituents.menuAction())
        self.menu_fetch_initial_data.addAction(self.action_fetch_dividend)
        self.menu_fetch_initial_data.addAction(self.menu_key_metrics.menuAction())
        self.menu_fetch_initial_data.addAction(self.menu_daily_chart.menuAction())
        self.menuFMP_Database.addAction(self.action_create_new_database)
        self.menuFMP_Database.addAction(self.action_create_tables)
        self.menuFMP_Database.addAction(self.menu_fetch_initial_data.menuAction())
        self.menuFMP_Database.addSeparator()
        self.menuFMP_Database.addAction(self.action_backup)
        self.menuTools.addAction(self.action_chart_window)
        self.menuTools.addAction(self.action_finance_window)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuFMP_Database.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget_reporting.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FMP-PostgreSQL-PyQt"))
        self.groupBox.setTitle(_translate("MainWindow", "Reporting"))
        self.comboBox_reporting.setPlaceholderText(_translate("MainWindow", "Choosing a table for a report"))
        self.tabWidget_reporting.setTabText(self.tabWidget_reporting.indexOf(self.tab_process), _translate("MainWindow", "Process"))
        self.tabWidget_reporting.setTabText(self.tabWidget_reporting.indexOf(self.tab_tables), _translate("MainWindow", "Performance"))
        self.pushButton_query_clear.setText(_translate("MainWindow", "Clear"))
        self.pushButton_query_ok.setText(_translate("MainWindow", "Validation"))
        self.label_query.setText(_translate("MainWindow", "Write a SELECT SQL query (without quotes) :"))
        self.tabWidget_reporting.setTabText(self.tabWidget_reporting.indexOf(self.tab_query), _translate("MainWindow", "SQL query"))
        self.menuHelp.setTitle(_translate("MainWindow", "Preinstallation"))
        self.menu_postgresql.setTitle(_translate("MainWindow", "PostgreSQL"))
        self.menuFMP_Database.setTitle(_translate("MainWindow", "FMP Database"))
        self.menu_fetch_initial_data.setTitle(_translate("MainWindow", "Import data to tables"))
        self.menu_key_metrics.setTitle(_translate("MainWindow", "Key metrics"))
        self.menu_daily_chart.setTitle(_translate("MainWindow", "Daily chart"))
        self.menu_index_constituents.setTitle(_translate("MainWindow", "Index constituents"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.actionPostgreSQL.setText(_translate("MainWindow", "PostgreSQL"))
        self.actionTimescaleDB.setText(_translate("MainWindow", "TimescaleDB"))
        self.action_timescaledb_install.setText(_translate("MainWindow", "TimescaleDB"))
        self.action_create_tables.setText(_translate("MainWindow", "Create tables"))
        self.action_fetch_stock_symbols.setText(_translate("MainWindow", "Stock symbols"))
        self.action_fetch_company_profile.setText(_translate("MainWindow", "Company profile"))
        self.action_fetch_dividend.setText(_translate("MainWindow", "Dividend"))
        self.action_update_stoxx_europe.setText(_translate("MainWindow", "STOXX Europe 600"))
        self.action_update_dividend.setText(_translate("MainWindow", "Dividend"))
        self.action_update_key_metrics.setText(_translate("MainWindow", "Key metrics"))
        self.action_update_daily_chart.setText(_translate("MainWindow", "Daily chart"))
        self.actionAll.setText(_translate("MainWindow", "All..."))
        self.actionStock_symbols_2.setText(_translate("MainWindow", "Stock symbols"))
        self.actionSTOXX_Europe_602.setText(_translate("MainWindow", "STOXX Europe 600"))
        self.actionCompany_profile_2.setText(_translate("MainWindow", "Company profile"))
        self.actionDividend_3.setText(_translate("MainWindow", "Dividend"))
        self.actionKey_metrics_3.setText(_translate("MainWindow", "Key metrics"))
        self.actionDaily_cahrt.setText(_translate("MainWindow", "Daily chart"))
        self.actionQuery.setText(_translate("MainWindow", "Write a query"))
        self.action_create_new_database.setText(_translate("MainWindow", "Create new database"))
        self.action_postgresql_install.setText(_translate("MainWindow", "Install"))
        self.action_postgresql_update.setText(_translate("MainWindow", "Update"))
        self.action_report_tables.setText(_translate("MainWindow", "Report on tables"))
        self.action_env_file.setText(_translate("MainWindow", "Environment file"))
        self.action_chart_window.setText(_translate("MainWindow", "Chart studies"))
        self.action_finance_window.setText(_translate("MainWindow", "Finance analysis"))
        self.action_fetch_key_metrics_quarter.setText(_translate("MainWindow", "Quarter"))
        self.action_fetch_key_metrics_annual.setText(_translate("MainWindow", "Annual"))
        self.action_backup.setText(_translate("MainWindow", "Backup..."))
        self.action_historical_daily_chart.setText(_translate("MainWindow", "Historical data"))
        self.action_update_daily_chart_.setText(_translate("MainWindow", "Data update"))
        self.action_fetch_stoxx_600.setText(_translate("MainWindow", "STOXX Europe 600"))
        self.action_fetch_dow_jones.setText(_translate("MainWindow", "Dow Jones"))
        self.action_fetch_sp_500.setText(_translate("MainWindow", "SP 500"))
        self.action_fetch_nasdaq.setText(_translate("MainWindow", "NASDAQ"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
