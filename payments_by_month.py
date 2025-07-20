from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QFileDialog
)
from export_utils import export_to_pdf, export_to_excel
from database import get_payments_by_month, get_monthly_total, get_yearly_total

class PaymentsByMonthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📅 مدفوعات حسب الشهر")
        self.setGeometry(400, 150, 600, 400)

        layout = QVBoxLayout()

        # اختيار الشهر والسنة
        filter_layout = QHBoxLayout()

        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "01 - جانفي", "02 - فيفري", "03 - مارس", "04 - أفريل", "05 - ماي", "06 - جوان",
            "07 - جويلية", "08 - أوت", "09 - سبتمبر", "10 - أكتوبر", "11 - نوفمبر", "12 - ديسمبر"
        ])
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("مثال: 2025")

        self.show_button = QPushButton("📤 عرض النتائج")
        self.show_button.clicked.connect(self.load_data)

        filter_layout.addWidget(QLabel("🗓️ الشهر:"))
        filter_layout.addWidget(self.month_combo)
        filter_layout.addWidget(QLabel("السنة:"))
        filter_layout.addWidget(self.year_input)
        filter_layout.addWidget(self.show_button)

        layout.addLayout(filter_layout)

        # الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["الاسم", "المبلغ", "التاريخ", "ملاحظة"])
        layout.addWidget(self.table)

        self.total_label = QLabel("💰 مجموع الشهر: 0.00 DA")
        self.year_total_label = QLabel("📆 مجموع السنة: 0.00 DA")
        layout.addWidget(self.total_label)
        layout.addWidget(self.year_total_label)
        
        export_btn = QPushButton("📤 تصدير")
        export_btn.clicked.connect(self.export_report)
        layout.addWidget(export_btn)

        self.setLayout(layout)

    def load_data(self):
        month_index = self.month_combo.currentIndex() + 1
        year = self.year_input.text()

        if not year.isdigit():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال سنة صحيحة (مثلاً: 2025)")
            return

        payments = get_payments_by_month(month_index, int(year))

        self.table.setRowCount(0)
        for row_number, row_data in enumerate(payments):
            self.table.insertRow(row_number)
            for col, value in enumerate(row_data):
                self.table.setItem(row_number, col, QTableWidgetItem(str(value)))

        # ✅ عرض المجموع
        month_total = get_monthly_total(month_index, year)
        year_total = get_yearly_total(year)

        self.total_label.setText(f"💰 مجموع الشهر: {month_total:,.2f} DA")
        self.year_total_label.setText(f"📆 مجموع السنة: {year_total:,.2f} DA")

    def export_report(self):
        name, ext = QFileDialog.getSaveFileName(
            self,
            "اختر مكان الحفظ",
            "",
            "PDF Files (*.pdf);;Excel Files (*.xlsx)"
        )

        if not name:
            return

        # فرض الامتداد الصحيح حسب نوع الملف المختار
        if "pdf" in ext and not name.endswith(".pdf"):
            name += ".pdf"
        elif "xlsx" in ext and not name.endswith(".xlsx"):
            name += ".xlsx"

        # استخراج البيانات من الجدول
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        data = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        report_title = f"تقرير مدفوعات {self.month_combo.currentText()} {self.year_input.text()}"
        
        # تصدير حسب النوع
        if name.endswith(".pdf"):
            export_to_pdf(name, headers, data, report_title, show_total=True)
            
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى PDF بنجاح.")
        elif name.endswith(".xlsx"):
            export_to_excel(name, headers, data)
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى Excel بنجاح.")


