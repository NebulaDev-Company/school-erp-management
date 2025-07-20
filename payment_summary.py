from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFileDialog, QHBoxLayout, QPushButton, QMessageBox
)
from database import get_total_payments_per_student
from export_utils import export_to_pdf, export_to_excel

class PaymentSummaryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 ملخص المدفوعات")
        self.setGeometry(350, 150, 500, 400)

        layout = QVBoxLayout()

        # 🔍 حقل البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث باسم التلميذ...")
        self.search_input.textChanged.connect(self.search_table)

        # 📤 زر التصدير
        export_btn = QPushButton("📤 تصدير تقرير")
        export_btn.clicked.connect(self.export_report)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(export_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "الاسم", "إجمالي المدفوع"])

        # 🧩 إضافة العناصر إلى التخطيط
        layout.addWidget(QLabel("📋 مجموع ما دفعه كل تلميذ"))
        layout.addWidget(self.search_input)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        data = get_total_payments_per_student()
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for col, value in enumerate(row_data):
                if col == 2:
                    try:
                        value = "{:,.2f} DA".format(float(value))
                    except:
                        pass
                self.table.setItem(row_number, col, QTableWidgetItem(str(value)))


        # 💰 حساب مجموع المدفوعات
        total = sum(float(row[2]) for row in data if row[2])
        formatted_total = "{:,.2f} DA".format(total)

        # 🔄 عرض أو تحديث Label المجموع
        if hasattr(self, 'total_label'):
            self.total_label.setText(f"💰 مجموع المدفوعات: {formatted_total}")
        else:
            self.total_label = QLabel(f"💰 مجموع المدفوعات: {formatted_total}")
            self.layout().addWidget(self.total_label)

    def search_table(self):
        keyword = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            match = keyword in name_item.text().lower() if name_item else False
            self.table.setRowHidden(row, not match)

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

        # تصدير حسب النوع
        if name.endswith(".pdf"):
            export_to_pdf(name, headers, data, report_title="تقرير المدفوعات", show_total=True)
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى PDF بنجاح.")
        elif name.endswith(".xlsx"):
            export_to_excel(name, headers, data)
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى Excel بنجاح.")
