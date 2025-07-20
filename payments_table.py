from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QLabel
from database import get_all_payments

class PaymentsTableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💰 قائمة المدفوعات")
        self.setGeometry(300, 100, 600, 400)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث باسم التلميذ...")
        self.search_input.textChanged.connect(self.search_payments)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["الاسم", "المبلغ", "التاريخ", "ملاحظة"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("قائمة المدفوعات:"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        payments = get_all_payments()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(payments):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def search_payments(self):
        keyword = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            match = keyword in name_item.text().lower() if name_item else False
            self.table.setRowHidden(row, not match)
