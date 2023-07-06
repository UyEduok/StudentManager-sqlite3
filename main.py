import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, \
    QGridLayout, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QComboBox, QToolBar, QStatusBar,QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt


class Database:

    def __init__(self, database_file='database.db'):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Student Management System')
        self.setMinimumSize(800,600)

        file_menu_item = self.menuBar().addMenu('File')
        help_menu_item = self.menuBar().addMenu('Help')
        edit_menu_item = self.menuBar().addMenu('Edit')

        add_student_action = QAction(QIcon('icons/add.png'),'Add Student', self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction('About', self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_student_action = QAction(QIcon('icons/search.png'),'Search', self)
        search_student_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_student_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id', 'Name', 'Course', 'Mobile'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # create and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student_action)

        # create status bar and add status buttons
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # detect cell clicked
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton('Edit Record')
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton('Delete Record')
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)

        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = Database().connect()
        result = connection.execute('SELECT * FROM students')
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Add Student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # capture student name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # capture student course
        self.course_name = QComboBox()
        course = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(course)
        layout.addWidget(self.course_name)

        # capture student mobile number
        self.student_number = QLineEdit()
        self.student_number.setPlaceholderText('Mobile Number')
        layout.addWidget(self.student_number)

        # add the submit button
        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.student_number.text()
        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)',
        (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Search Student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # add a search bar
        self.search_student = QLineEdit()
        self.search_student.setPlaceholderText('Name')
        layout.addWidget(self.search_student)

        # add the submit button
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        name = self.search_student.text()
        connection = Database().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        row = list(result)[0]
        print(row)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Update Student Record')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # get the current student name
        index = main_window.table.currentRow()

        # get the id of the selected item
        self.student_id = main_window.table.item(index, 0).text()

        # row = index and column is 1, because that is the name column
        table_student_name = main_window.table.item(index, 1).text()

        # capture student name
        self.student_name = QLineEdit(table_student_name)
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # row = index and column is 2, because that is the course column
        table_course_name = main_window.table.item(index, 2).text()

        # capture student course
        self.course_name = QComboBox()
        course = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(course)
        self.course_name.setCurrentText(table_course_name)
        layout.addWidget(self.course_name)

        table_number_name = main_window.table.item(index, 3).text()

        # capture student mobile number
        self.student_number = QLineEdit(table_number_name)
        self.student_number.setPlaceholderText('Mobile Number')
        layout.addWidget(self.student_number)

        # add the submit button
        submit_button = QPushButton('Update')
        submit_button.clicked.connect(self.update_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update_student(self):
        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.student_number.text(),
                        self.student_id))

        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()  # Close the associated empty window


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Delete Student Record')

        layout = QGridLayout()

        confirmation = QLabel('Are you sure you want to delete?')
        yes = QPushButton('Yes')
        no = QPushButton('No')

        # add widget to the grid layout
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        # add action to the push buttons
        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.cancel_delete)

        self.setLayout(layout)

    def delete_student(self):
        # get the current student name
        index = main_window.table.currentRow()

        # get the id of the selected item
        student_id = main_window.table.item(index, 0).text()

        connection = Database().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table in the main_window
        main_window.load_data()

        # Close the dialog window
        self.accept()

        # a delete success confirmation window
        confirmation = QMessageBox()
        confirmation.setWindowTitle('Success')
        confirmation.setText('The selected record was deleted successfully')
        confirmation.exec()

    def cancel_delete(self):
        # Refresh the table in the main_window
        main_window.load_data()

        # Close the dialog window
        self.accept()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        content = """
This system was created by Uyuho Eduok for student management, using PyQt6, feel free to modify and use. 
        """
        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
