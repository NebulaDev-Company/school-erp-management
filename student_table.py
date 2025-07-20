from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QFileDialog,
    QComboBox
)
from database import( get_all_students, delete_student, update_student, 
    get_all_students, delete_student, update_student, get_subjects_for_student, 
    archive_student, get_all_subjects, get_students_by_subject
)

from edit_student import EditStudentWindow
from export_utils import export_to_pdf, export_to_excel
class StudentsTableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("قائمة التلاميذ")
        self.setGeometry(450, 100, 600, 400)

        # تخطيط أفقي لشريط البحث وفلتر المواد
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث عن تلميذ...")
        self.search_input.textChanged.connect(self.search_students)
        search_layout.addWidget(self.search_input)

        self.subject_filter = QComboBox()
        self.subject_filter.addItem("📚 الكل")
        subjects = get_all_subjects()
        for sub in subjects:
            self.subject_filter.addItem(sub[1], sub[0])  # الاسم، ثم ID في data
        self.subject_filter.setFixedWidth(150)  # جعل الحجم صغيرًا نوعًا ما
        self.subject_filter.currentIndexChanged.connect(self.filter_by_subject)
        search_layout.addWidget(self.subject_filter)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "الاسم", "القسم", "تاريخ الميلاد", "هاتف الولي", "تاريخ التسجيل", "المواد"])

        self.delete_button = QPushButton("🗑️ حذف المحدد")
        self.delete_button.clicked.connect(self.delete_selected)

        self.edit_button = QPushButton("✏️ تعديل المحدد")
        self.edit_button.clicked.connect(self.edit_selected)

        export_btn = QPushButton("📤 تصدير تقرير")
        export_btn.clicked.connect(self.export_report)

        self.archive_button = QPushButton("📦 أرشفة المحدد")
        self.archive_button.clicked.connect(self.archive_selected)

        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addWidget(self.table)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.delete_button)
        btns_layout.addWidget(self.edit_button)
        btns_layout.addWidget(self.archive_button)
        btns_layout.addWidget(export_btn)        

        layout.addLayout(btns_layout)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        students = get_all_students()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(students):
            self.table.insertRow(row_number)
            student_id = row_data[0]

            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            # 📘 إحضار المواد
            subjects = get_subjects_for_student(student_id)
            subject_names = ", ".join(subjects)
            self.table.setItem(row_number, 6, QTableWidgetItem(subject_names))

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
            f"هل أنت متأكد أنك تريد حذف التلميذ: {student_name}؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            delete_student(student_id)
            QMessageBox.information(self, "تم", "تم حذف التلميذ.")
            self.load_data()

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

    def export_report(self):
        name, ext = QFileDialog.getSaveFileName(
            self,
            "اختر مكان الحفظ",
            "students_list.pdf",
            "PDF Files (*.pdf);;Excel Files (*.xlsx)"
        )
        
        if not name:
            return

        # فرض الامتداد الصحيح
        if "pdf" in ext and not name.endswith(".pdf"):
            name += ".pdf"
        elif "xlsx" in ext and not name.endswith(".xlsx"):
            name += ".xlsx"

        # استخراج رؤوس الأعمدة والبيانات
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

        # التصدير حسب النوع
        if name.endswith(".pdf"):
            export_to_pdf(name, headers, data, report_title="تقرير التلاميذ")
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى PDF بنجاح.")
        elif name.endswith(".xlsx"):
            export_to_excel(name, headers, data)
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى Excel بنجاح.")
            
    def archive_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطأ", "يرجى تحديد صف للأرشفة.")
            return

        student_id = self.table.item(selected, 0).text()
        student_name = self.table.item(selected, 1).text()

        confirm = QMessageBox.question(
            self,
            "تأكيد الأرشفة",
            f"هل تريد أرشفة التلميذ: {student_name}؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            from database import archive_student
            archive_student(student_id)
            QMessageBox.information(self, "تم", "تم أرشفة التلميذ.")
            self.load_data()
            
    def filter_by_subject(self):
        selected_id = self.subject_filter.currentData()

        if selected_id is None:
            # عرض كل التلاميذ
            self.load_data()
        else:
            students = get_students_by_subject(selected_id)
            self.table.setRowCount(0)

            for row_number, row_data in enumerate(students):
                self.table.insertRow(row_number)
                student_id = row_data[0]

                for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

                subjects = get_subjects_for_student(student_id)
                subject_names = ", ".join(subjects)
                self.table.setItem(row_number, 6, QTableWidgetItem(subject_names))