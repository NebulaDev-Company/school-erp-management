# students_late_this_month.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit
from database import get_students_missing_payment_this_month

class StudentsLateThisMonthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📆 تلاميذ لم يدفعوا هذا الشهر")
        self.setGeometry(350, 150, 600, 400)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث عن تلميذ...")
        self.search_input.textChanged.connect(self.search_table)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "الاسم", "القسم", "تاريخ الميلاد", "هاتف الولي"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📋 تلاميذ لم يسددوا هذا الشهر"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        students = get_students_missing_payment_this_month()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(students):
            self.table.insertRow(row_number)
            for col, value in enumerate(row_data):
                self.table.setItem(row_number, col, QTableWidgetItem(str(value)))

    def search_table(self):
        keyword = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            match = keyword in name_item.text().lower() if name_item else False
            self.table.setRowHidden(row, not match)
