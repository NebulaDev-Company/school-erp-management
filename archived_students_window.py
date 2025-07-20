from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QFileDialog,
    QComboBox
)
from database import (
    get_all_students, delete_student, update_student,
    get_subjects_for_student, unarchive_student, get_all_subjects
)
from edit_student import EditStudentWindow
from export_utils import export_to_pdf, export_to_excel

class ArchivedStudentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 التلاميذ المؤرشفين")
        self.setGeometry(450, 100, 600, 400)

        # تخطيط أفقي لشريط البحث وفلتر المواد
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث عن تلميذ مؤرشف...")
        self.search_input.textChanged.connect(self.search_students)
        search_layout.addWidget(self.search_input)

        self.subject_filter = QComboBox()
        self.subject_filter.addItem("📚 الكل")  # الخيار الافتراضي
        subjects = get_all_subjects()
        for subj in subjects:
            self.subject_filter.addItem(subj[1], subj[0])  # الاسم والمفتاح الأساسي
        self.subject_filter.setFixedWidth(150)  # جعل الحجم صغيرًا نوعًا ما
        self.subject_filter.currentIndexChanged.connect(self.load_data)
        search_layout.addWidget(self.subject_filter)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "الاسم", "القسم", "تاريخ الميلاد", "هاتف الولي", "تاريخ التسجيل", "المواد"])

        self.delete_button = QPushButton("🗑️ حذف المحدد")
        self.delete_button.clicked.connect(self.delete_selected)

        self.edit_button = QPushButton("✏️ تعديل المحدد")
        self.edit_button.clicked.connect(self.edit_selected)

        self.restore_button = QPushButton("♻️ استرجاع المحدد")
        self.restore_button.clicked.connect(self.restore_selected)

        export_btn = QPushButton("📤 تصدير تقرير")
        export_btn.clicked.connect(self.export_report)

        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addWidget(self.table)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.delete_button)
        btns_layout.addWidget(self.edit_button)
        btns_layout.addWidget(self.restore_button)
        btns_layout.addWidget(export_btn)

        layout.addLayout(btns_layout)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        students = get_all_students(archived_only=True)
        selected_subject_id = self.subject_filter.currentData()  # ← المادة المختارة

        self.table.setRowCount(0)
        for row_number, row_data in enumerate(students):
            student_id = row_data[0]

            # إحضار المواد المرتبطة بالتلميذ
            subjects = get_subjects_for_student(student_id)
            if selected_subject_id and selected_subject_id != 0:  # 0 تعني "الكل"
                subject_names = [s for s in subjects]
                if not any(get_all_subjects()[i][0] == selected_subject_id and get_all_subjects()[i][1] in subject_names for i in range(len(get_all_subjects()))):
                    continue  # تجاوز التلميذ إن لم يدرس المادة المختارة

            self.table.insertRow(self.table.rowCount())
            for column_number, data in enumerate(row_data):
                self.table.setItem(self.table.rowCount() - 1, column_number, QTableWidgetItem(str(data)))
            self.table.setItem(self.table.rowCount() - 1, 6, QTableWidgetItem(", ".join(subjects)))

    def search_students(self):
        keyword = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item and keyword in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def delete_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطأ", "يرجى تحديد صف للحذف.")
            return

        student_id = self.table.item(selected, 0).text()
        student_name = self.table.item(selected, 1).text()

        confirm = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل أنت متأكد أنك تريد حذف التلميذ المؤرشف: {student_name}؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            delete_student(student_id)
            QMessageBox.information(self, "تم", "تم حذف التلميذ.")
            self.load_data()

    def edit_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطأ", "يرجى تحديد صف للتعديل.")
            return

        student_data = []
        for column in range(self.table.columnCount()):
            item = self.table.item(selected, column)
            student_data.append(item.text() if item else "")

        self.edit_window = EditStudentWindow(student_data, self.load_data)
        self.edit_window.show()

    def restore_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطأ", "يرجى تحديد تلميذ لاسترجاعه.")
            return

        student_id = self.table.item(selected, 0).text()
        student_name = self.table.item(selected, 1).text()

        confirm = QMessageBox.question(
            self,
            "تأكيد الاسترجاع",
            f"هل تريد استرجاع التلميذ: {student_name}؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            unarchive_student(student_id)
            QMessageBox.information(self, "تم", "تم استرجاع التلميذ.")
            self.load_data()

    def export_report(self):
        name, ext = QFileDialog.getSaveFileName(
            self,
            "اختر مكان الحفظ",
            "archived_students.pdf",
            "PDF Files (*.pdf);;Excel Files (*.xlsx)"
        )
        if not name:
            return

        if "pdf" in ext and not name.endswith(".pdf"):
            name += ".pdf"
        elif "xlsx" in ext and not name.endswith(".xlsx"):
            name += ".xlsx"

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

        if name.endswith(".pdf"):
            export_to_pdf(name, headers, data, report_title="تقرير التلاميذ المؤرشفين")
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى PDF.")
        elif name.endswith(".xlsx"):
            export_to_excel(name, headers, data)
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى Excel.")