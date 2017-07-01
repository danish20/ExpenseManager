import csv
import os

from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
import datetime
import sys

class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):

        #Top Menu Bar
        menu_bar = self.menuBar()

        #Menu items
        action_item = menu_bar.addMenu("Action")

        #Submenu Items
        add_expense_action = QAction('&Add Expense',self)
        add_expense_action.setShortcut('Ctrl+A')
        view_expense_action = QAction('&View Expense',self)
        view_expense_action.setShortcut('Ctrl+V')


        #Add Actions to menu item
        action_item.addAction(add_expense_action)
        action_item.addAction(view_expense_action)

        content_window = ContentWindow()
        self.setCentralWidget(content_window)

        self.setWindowTitle("Home")
        self.resize(500,400)
        self.show()


class ContentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_vals(self):
        today = datetime.datetime.now()
        self.month = today.strftime('%B')
        self.amounts = {"Groceries": 0, "House": 0, "Car": 0, "School Fees": 0, "Leisure": 0, "Sports": 0, "Travel": 0}
        self.read_file()
        self.cat_values = [
            {"name": "Groceries", "amount": self.amounts['Groceries']},
            {"name": "House", "amount": self.amounts['House']},
            {"name": "Car", "amount": self.amounts['Car']},
            {"name": "School Fees", "amount": self.amounts['School Fees']},
            {"name": "Leisure", "amount": self.amounts['Leisure']},
            {"name": "Sports", "amount": self.amounts['Sports']},
            {"name": "Travel", "amount": self.amounts['Travel']}
        ]

        self.debit = 0;
        self.credit = 0;
        self.read_credit()

        for vals in self.cat_values:
            self.debit += vals['amount']

    def init_ui(self):
        self.init_vals()


        hbox = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()
        titlebox = QHBoxLayout()

        self.topleft = HighlightedTextWidget('Debit',self.debit)
        self.topright = HighlightedTextWidget('Credit',self.credit)
        self.bottomleft = CategoryGrid(self.cat_values,self.debit)
        bottomright = QVBoxLayout()
        title = QLabel(self.month+" Expense Summary")
        title.setFont(QFont("Helvetica", 25))
        title.setStyleSheet("QLabel {color : #1B5E20; }")

        titlebox.addStretch()
        titlebox.addWidget(title)
        titlebox.addStretch()

        add_expense = QPushButton("Add Expense")
        view_expense = QPushButton("View Expense")
        export_csv = QPushButton("Export to CSV")
        credit_btn = QPushButton("Add Credit")

        bottomright.addWidget(add_expense)
        bottomright.addWidget(view_expense)
        bottomright.addWidget(export_csv)
        bottomright.addWidget(credit_btn)

        hbox.addWidget(self.topleft)
        hbox.addWidget(self.topright)

        hbox2.addWidget(self.bottomleft)
        hbox2.addLayout(bottomright)

        vbox.addLayout(titlebox)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        self.add_ex_win = Dialog()
        self.view_ex_win = ViewExpenseDialog()
        self.view_ex_win.resize(400,400)
        add_expense.clicked.connect(self.addex_clicked)
        view_expense.clicked.connect(self.viewex_clicked)
        credit_btn.clicked.connect(self.add_credit)
        export_csv.clicked.connect(self.export_csv_file)

        self.setLayout(vbox)

    def export_csv_file(self):
        path = QFileDialog.getSaveFileName(self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
        if path[0] != '':
            with open(path[0], 'w') as csvfile:
                fieldnames = ['name', 'category', 'amount']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                with open(self.month+'.csv') as csvrfile:
                    reader = csv.reader(csvrfile)
                    for row in reader:
                        print(row)
                        writer.writerow({'name':row[0],'category':row[1],'amount':row[2]})

    def addex_clicked(self):
        self.add_ex_win.exec_()

    def viewex_clicked(self):
        self.view_ex_win.exec_()

    def read_file(self):
        with open(self.month+'.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.amounts[row[1].strip()] += int(row[2])

    def read_credit(self):
        try:
            f = open("credit.txt", "r")
            for credit in f.readlines():
                self.credit = int(credit)
            f.close()
        except Exception:
            self.credit = 0

    def write_credit(self):
        f = open("credit.txt", "w")
        f.write(str(self.credit))
        f.close()

    def add_credit(self):
        text, ok = QInputDialog.getText(self, 'Add Credit','Enter Credit Amount')

        if ok:
            self.credit += int(text)
            print(self.credit)
            self.write_credit()


class HighlightedTextWidget(QWidget):
    def __init__(self,label_text,value):
        super().__init__()
        self.init_ui(label_text,value)

    def init_ui(self,label_text,value):
        self.label = QLabel(label_text)
        self.value = QLabel("$"+str(value))

        self.label.setFont(QFont("Times", 15, QtGui.QFont.StyleItalic))
        self.value.setFont(QFont("Times", 30, QtGui.QFont.Bold))

        if(label_text == "Credit"):
            self.value.setStyleSheet("QLabel {color : #484D25; }")
        else:
            self.value.setStyleSheet("QLabel {color : #F75600; }")

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.label)
        v_layout.addWidget(self.value)

        self.setLayout(v_layout)


class ViewExpense(QTableWidget):
    def __init__(self,r,c):
        super().__init__(r,c)
        today = datetime.datetime.now()
        self.month = today.strftime('%B')
        self.open_sheet(self.month)
        self.show()

    def open_sheet(self,month):
        path = [month+'.csv']
        if path[0] != '':
            with open(path[0], newline='') as csv_file:
                self.setRowCount(0)
                self.setColumnCount(3)
                my_file = csv.reader(csv_file, dialect='excel')
                for row_data in my_file:
                    row = self.rowCount()
                    self.insertRow(row)
                    if len(row_data) > 3:
                        self.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QTableWidgetItem(stuff)
                        self.setItem(row, column, item)


class AddExpenseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        wid = AddExpenseWidget()
        self.setCentralWidget(wid)
        self.show()


class AddExpenseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):
        ename = QLabel('Expense Name')
        cat = QLabel('Category')
        amt = QLabel('Amount')

        category = QComboBox(self)

        for items in ContentWindow.cat_values:
            category.addItem(items["title"])


        expenseNameEdit = QLineEdit()
        amountEdit = QLineEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(ename, 1, 0)
        grid.addWidget(expenseNameEdit, 1, 1)

        grid.addWidget(cat, 2, 0)
        grid.addWidget(category, 2, 1)

        grid.addWidget(amt, 3, 0)
        grid.addWidget(amountEdit, 3, 1)

        self.setLayout(grid)


class ViewExpenseDialog(QDialog):
    def __init__(self):
        super(ViewExpenseDialog, self).__init__()
        self.view_expense = ViewExpense(10, 3)
        col_headers = ['Name', 'Category', 'Amount']
        self.view_expense.setHorizontalHeaderLabels(col_headers)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)


        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.view_expense)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Add Expense")


class Dialog(QDialog):


    def __init__(self):
        super(Dialog, self).__init__()
        self.cat_values = [
            {"title": "Groceries"},
            {"title": "House"},
            {"title": "Car"},
            {"title": "School Fees"},
            {"title": "Leisure"},
            {"title": "Sports"},
            {"title": "Travel"}
        ]

        self.createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Add Expense")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Add New Expense")

        ename = QLabel('Expense Name')
        cat = QLabel('Category')
        amt = QLabel('Amount')

        self.category = QComboBox(self)
        self.category.addItem("Select Category")
        self.category_selected = 'Select Category'

        for items in self.cat_values:
            self.category.addItem(items["title"])

        val = self.category.activated[str].connect(self.selectCat)

        self.expenseNameEdit = QLineEdit()
        self.amountEdit = QLineEdit()

        layout = QFormLayout()
        layout.addRow(ename,self.expenseNameEdit)
        layout.addRow(cat,self.category)
        layout.addRow(amt,self.amountEdit)
        self.formGroupBox.setLayout(layout)

    def selectCat(self,text):
        self.category_selected = text

    def accept(self):
        super().accept()
        self.save_sheet()

    def reject(self):
        super().reject()
        self.update()

    def save_sheet(self):
        today = datetime.datetime.now()
        month = today.strftime('%B')

        name = str(self.expenseNameEdit.text())
        category = self.category_selected
        amount = int(self.amountEdit.text())

        self.expenseNameEdit.clear()
        self.amountEdit.clear()


        with open(month+'.csv', 'a') as csvfile:
            fieldnames = ['name', 'category','amount']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'name': name, 'category': category, 'amount':amount})


class CategoryGrid(QWidget):
    def __init__(self,cat_values,debit):
        super().__init__()
        self.init_ui(cat_values,debit)


    def init_ui(self,cat_values,debit):
        cat_title=[]
        cat_pbars = []
        for cats in cat_values:
            name = cats['name'].title()
            label = QLabel(name)
            label.setFont(QFont("Times", 16))
            label.setStyleSheet("QLabel {color : #484D25; }")

            cat_title.append(label)

            pbar = QProgressBar()
            val = cats["amount"]
            if debit==0:
                val = 0
            else:
                val = (val/debit)*100
            pbar.setValue(val)
            cat_pbars.append(pbar)


        grid = QGridLayout()
        grid.setSpacing(10)

        for i in range(len(cat_title)):
            grid.addWidget(cat_title[i], i+1, 0)
            grid.addWidget(cat_pbars[i], i+1, 1)

        self.setLayout(grid)


app = QApplication(sys.argv)
window = BaseWindow()
sys.exit(app.exec_())