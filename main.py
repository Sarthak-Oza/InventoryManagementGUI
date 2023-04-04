from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, \
    QMessageBox, QToolBar, QStatusBar, QGridLayout, QLabel
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sqlite3


# sql connection
def sql_connection():
    connection = sqlite3.connect("inventorydata.db")
    return connection


# main window of the app
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Management System")
        self.setWindowIcon(QIcon("icons/asset.png"))
        self.setMinimumSize(430, 300)

        # create add menu items to menubar
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Add action from menubar
        add_item_action = QAction(QIcon("icons/add.png"), "Add", self)
        add_item_action.triggered.connect(self.add_item)
        file_menu_item.addAction(add_item_action)

        # search action from menubar
        search_item_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_item_action.triggered.connect(self.search_item)
        edit_menu_item.addAction(search_item_action)

        # search from toolbar
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.search_from_widget)

        # About action from menubar
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about_menu)
        help_menu_item.addAction(about_action)

        # create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Asset_ID", "Item Description", "Location", "Delivery Date"))

        self.setCentralWidget(self.table)

        self.load_table_data()

        # create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        toolbar.addAction(add_item_action)
        #search button for toolbar
        # toolbar.addAction(search_item_action)
        toolbar.addWidget(self.search)
        self.addToolBar(toolbar)

        # create statusbar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # action for currently selected cell
        self.table.cellClicked.connect(self.cell_clicked)

    def search_from_widget(self):
        # Clear current selection
        self.table.setCurrentItem(None)

        if not self.search.text():
            # return for empty string
            return

        matching_items = self.table.findItems(self.search.text(), Qt.MatchFlag.MatchContains)
        if matching_items:
            # match found
            item = matching_items[0]
            self.table.setCurrentItem(item)

            self.table.selectRow(self.table.currentRow())

    def cell_clicked(self):
        # create buttons for statusbar
        edit_button = QPushButton("Edit Record")
        delete_button = QPushButton("Delete Record")

        # delete statusbar buttons that gets created on every click and will be followed by creating new buttons
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # add buttons to statusbar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

        edit_button.clicked.connect(self.edit_dialog)
        delete_button.clicked.connect(self.delete_dialog)

    def load_table_data(self):
        sql_connect = sql_connection()
        cursor = sql_connect.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS items (asset_id INT UNIQUE, asset_type VARCHAR(100) NOT NULL, location "
            "VARCHAR(100) NOT NULL, receive_date DATE NOT NULL);")
        sql_connect.commit()
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        cursor.close()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(rows):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def edit_dialog(self):
        edit = EditItemDialog()
        edit.exec()

    def delete_dialog(self):
        delete = DeleteDialog()
        delete.exec()

    def about_menu(self):
        about_dialog = QMessageBox()
        about_dialog.setWindowTitle("About")
        about_message = "This App manages inventory for devices. You can add, edit and delete device information using this app."
        about_dialog.setText(about_message)
        about_dialog.exec()

    def add_item(self):
        add_item_dialog_box = AddItemDialog()
        add_item_dialog_box.exec()

    def search_item(self):
        search_dialog = SearchDialog()
        search_dialog.exec()


class AddItemDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Item")
        self.setWindowIcon(QIcon("icons/add.png"))
        layout = QVBoxLayout()

        # create widgets for dialog
        self.asset_id_input = QLineEdit()
        self.asset_id_input.setPlaceholderText("Asset ID")

        self.item_type_input = QLineEdit()
        self.item_type_input.setPlaceholderText("Item")

        self.location_input = QComboBox()
        self.location_input.addItems(["Shelf: A", "Shelf: B", "Shelf: C"])

        self.date_received_input = QLineEdit()
        self.date_received_input.setPlaceholderText("Received Date YYYY-MM-DD")

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.save_new_item)

        # add widgets to layout
        layout.addWidget(self.asset_id_input)
        layout.addWidget(self.item_type_input)
        layout.addWidget(self.location_input)
        layout.addWidget(self.date_received_input)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def save_new_item(self):
        try:
            save_connect = sql_connection()
            cursor_save = save_connect.cursor()
            cursor_save.execute("INSERT INTO items VALUES(?, ?, ?, ?)",
                                (self.asset_id_input.text(), self.item_type_input.text(),
                                 self.location_input.currentText(), self.date_received_input.text()))
            save_connect.commit()
            cursor_save.execute("SELECT * FROM items")
            cursor_save.close()
            save_connect.close()

            # refresh main table after saving data
            window.load_table_data()

            # close dialog box
            self.close()

        except:
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Error")
            message_box.setWindowIcon(QIcon("icons/warning.png"))
            message_box.setText("Please enter valid values!")
            message_box.exec()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.setWindowTitle("Search Item")
        self.setWindowIcon(QIcon("icons/search.png"))

        # create widgets for dialog
        self.asset_id_search = QLineEdit()
        self.asset_id_search.setPlaceholderText("asset_id")

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.item_search)

        # add widgets to layout
        layout.addWidget(self.asset_id_search)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def item_search(self):

        try:
            # reset selected cell
            window.table.setCurrentItem(None)

            # find match
            matching_items = window.table.findItems(self.asset_id_search.text(), Qt.MatchFlag.MatchContains)
            window.table.setCurrentItem(matching_items[0])

            # highlight entire row after selecting only matching cell
            window.table.selectRow(window.table.currentRow())

            self.close()

        except:
            # clear input box
            self.asset_id_search.setText("")

            # display error message
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Error")
            message_box.setWindowIcon(QIcon("icons/warning.png"))
            message_box.setText("Asset does not exist, please try again!")
            message_box.exec()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delete Asset")
        self.setWindowIcon(QIcon("icons/delete.png"))

        # create gridlayout, message and buttons
        layout = QGridLayout()
        delete_message = QLabel("Are you sure you want to delete?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        # add widgets to layout
        layout.addWidget(delete_message, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)

        self.setLayout(layout)

        # click action for buttons
        yes_button.clicked.connect(self.delete_asset)
        no_button.clicked.connect(self.no_delete_asset)

    def no_delete_asset(self):
        self.close()

    def delete_asset(self):
        selected_asset_id = window.table.item(window.table.currentRow(), 0).text()

        delete_connect = sql_connection()
        cursor = delete_connect.cursor()
        cursor.execute("DELETE FROM items WHERE asset_id = ?", (selected_asset_id,))
        delete_connect.commit()
        cursor.close()
        delete_connect.close()

        # refresh main table after deleting asset
        window.load_table_data()

        # close dialog
        self.close()

        # display message on successful deletion
        successful_delete_message = QMessageBox()
        successful_delete_message.setWindowTitle("Delete Confirmation")
        successful_delete_message.setWindowIcon(QIcon("icons/check-mark.png"))
        successful_delete_message.setText("Asset has been successfully deleted!")

        successful_delete_message.exec()


class EditItemDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Edit Item")
        layout = QVBoxLayout()

        # get current row and col index from table
        row_index = window.table.currentRow()

        # get current asset details
        self.asset_id_input = QLineEdit(window.table.item(row_index, 0).text())
        self.item_type_input = QLineEdit(window.table.item(row_index, 1).text())

        self.location_input = QComboBox()
        self.location_input.addItems(["Shelf: A", "Shelf: B", "Shelf: C"])
        self.location_input.setCurrentText(window.table.item(row_index, 2).text())

        self.date_received_input = QLineEdit(window.table.item(row_index, 3).text())

        # update button action
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_item)

        # add widgets to layout
        layout.addWidget(self.asset_id_input)
        layout.addWidget(self.item_type_input)
        layout.addWidget(self.location_input)
        layout.addWidget(self.date_received_input)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update_item(self):
        try:
            update_connect = sql_connection()
            cursor = update_connect.cursor()
            cursor.execute(
                "UPDATE items SET asset_id = ?, asset_type = ?, location = ?, receive_date = ? WHERE asset_id = ?",
                (self.asset_id_input.text(), self.item_type_input.text(), self.location_input.currentText(),
                 self.date_received_input.text(), window.table.item(window.table.currentRow(), 0).text()))
            update_connect.commit()
            cursor.close()
            update_connect.close()

            # reload table data after updating the asset info
            window.load_table_data()

            # close dialog box
            self.close()

        except:
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Error")
            message_box.setWindowIcon(QIcon("icons/warning.png"))
            message_box.setText("Please enter valid values!")
            message_box.exec()


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
