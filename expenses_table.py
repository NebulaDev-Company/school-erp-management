from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
from database import create_connection
from export_utils import export_to_pdf  # استعمل نفس دالة التصدير الموجودة
from datetime import datetime

class ExpensesTableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📋 قائمة المصروفات")
        self.setGeometry(300, 150, 600, 400)

        layout = QVBoxLayout()

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.load_data()

        self.export_btn = QPushButton("📤 PDF تصدير كـ ")
        self.export_btn.clicked.connect(self.export_pdf)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)

    def load_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item, amount, date FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["المنتج", "السعر (DA)", "التاريخ"])

        self.expense_data = []
        for i, row in enumerate(rows):
            formatted = [row[0], f"{row[1]:,.2f} DA", row[2]]
            self.expense_data.append(formatted)
            for j, cell in enumerate(formatted):
                self.table.setItem(i, j, QTableWidgetItem(str(cell)))

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "حفظ التقرير", "", "PDF Files (*.pdf)")
        if path:
            if not path.endswith(".pdf"):
                path += ".pdf"
            headers = ["المنتج", "السعر (DA)", "التاريخ"]
            export_to_pdf(path, headers, self.expense_data, report_title="📋 تقرير المصروفات", show_total=True)
