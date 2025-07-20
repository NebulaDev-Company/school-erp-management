from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt
from database import create_subjects_table, create_teachers_table, create_teacher_subject_table, create_student_subject_table, get_all_subjects, get_all_teachers, add_teacher, update_teacher, delete_teacher, get_teacher_subject, set_teacher_subject
from export_utils import export_to_pdf
import arabic_reshaper
from bidi.algorithm import get_display

def reshape_ar(text):
    return get_display(arabic_reshaper.reshape(text))

class TeachersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة الأساتذة")
        self.setGeometry(300, 150, 800, 500)

        self.selected_teacher_id = None

        # عناصر الإدخال
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم الأستاذ")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف")

        self.subject_combo = QComboBox()
        self.load_subjects()

        self.active_checkbox = QCheckBox("معني بالمدرسة")
        self.active_checkbox.setChecked(True)

        self.add_btn = QPushButton("➕ إضافة / تعديل")
        self.add_btn.clicked.connect(self.add_or_update_teacher)

        self.clear_btn = QPushButton("🧹 تفريغ الحقول")
        self.clear_btn.clicked.connect(self.clear_fields)

        self.export_btn = QPushButton("📄 طباعة PDF")
        self.export_btn.clicked.connect(self.export_report)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الاسم", "الهاتف", "المادة", "معني؟", "🗑️"])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 100)
        self.table.cellClicked.connect(self.load_selected_teacher)

        # تخطيط
        layout = QVBoxLayout()

        # تخطيط أفقي لشريط البحث وفلتر المواد
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث عن أستاذ...")
        self.search_input.textChanged.connect(self.load_teachers)
        search_layout.addWidget(self.search_input)

        self.subject_filter = QComboBox()
        self.subject_filter.addItem("📚 الكل")  # الخيار الافتراضي
        subjects = get_all_subjects()
        for subj in subjects:
            self.subject_filter.addItem(subj[1], subj[0])  # الاسم، والـ id
        self.subject_filter.setFixedWidth(150)  # جعل الحجم صغيرًا نوعًا ما
        self.subject_filter.currentIndexChanged.connect(self.load_teachers)
        search_layout.addWidget(self.subject_filter)

        self.only_active_checkbox = QCheckBox("عرض المعنيين فقط")
        self.only_active_checkbox.setChecked(False)
        self.only_active_checkbox.stateChanged.connect(self.load_teachers)

        self.only_inactive_checkbox = QCheckBox("عرض غير المعنيين فقط")
        self.only_inactive_checkbox.setChecked(False)
        self.only_inactive_checkbox.stateChanged.connect(self.load_teachers)

        layout.addLayout(search_layout)
        layout.addWidget(self.only_active_checkbox)
        layout.addWidget(self.only_inactive_checkbox)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.subject_combo)
        form_layout.addWidget(self.active_checkbox)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.export_btn)

        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_teachers()

    def load_subjects(self):
        self.subject_combo.clear()
        subjects = get_all_subjects()
        for subj in subjects:
            self.subject_combo.addItem(subj[1], subj[0])

    def load_teachers(self):
        self.table.setRowCount(0)
        keyword = self.search_input.text().strip().lower()
        only_active = self.only_active_checkbox.isChecked()
        only_inactive = self.only_inactive_checkbox.isChecked()
        selected_subject_id = self.subject_filter.currentData()  # المادة المختارة

        for row_data in get_all_teachers():
            teacher_id, name, phone, active = row_data

            if only_active and not active:
                continue
            if only_inactive and active:
                continue
            if keyword and keyword not in name.lower():
                continue

            subject_id = get_teacher_subject(teacher_id, return_id=True)
            if selected_subject_id and subject_id != selected_subject_id:
                continue

            subject_name = get_teacher_subject(teacher_id)

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(name))
            self.table.setItem(row_position, 1, QTableWidgetItem(phone))
            self.table.setItem(row_position, 2, QTableWidgetItem(subject_name or ""))
            self.table.setItem(row_position, 3, QTableWidgetItem("YES" if active else "NO"))

            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.clicked.connect(lambda _, id=teacher_id: self.confirm_delete(id))
            self.table.setCellWidget(row_position, 4, delete_btn)

    def fill_fields_for_edit(self, teacher_id):
        self.selected_teacher_id = teacher_id
        teachers = [t for t in get_all_teachers() if t[0] == teacher_id]
        if teachers:
            tid, name, phone, active = teachers[0]
            self.name_input.setText(name)
            self.phone_input.setText(phone)
            self.active_checkbox.setChecked(bool(active))
            subject_id = get_teacher_subject(teacher_id, return_id=True)
            if subject_id:
                index = self.subject_combo.findData(subject_id)
                if index != -1:
                    self.subject_combo.setCurrentIndex(index)

    def clear_fields(self):
        self.selected_teacher_id = None
        self.name_input.clear()
        self.phone_input.clear()
        self.subject_combo.setCurrentIndex(0)
        self.active_checkbox.setChecked(True)

    def add_or_update_teacher(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        subject_id = self.subject_combo.currentData()
        active = 1 if self.active_checkbox.isChecked() else 0

        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الأستاذ")
            return

        if self.selected_teacher_id:
            update_teacher(self.selected_teacher_id, name, phone, active)
            set_teacher_subject(self.selected_teacher_id, subject_id)
        else:
            new_id = add_teacher(name, phone, active)
            set_teacher_subject(new_id, subject_id)

        self.clear_fields()
        self.load_teachers()

    def load_selected_teacher(self, row, _):
        teacher_id = get_all_teachers()[row][0]
        self.fill_fields_for_edit(teacher_id)

    def export_report(self):
        name, _ = QFileDialog.getSaveFileName(
            self,
            "اختر مكان الحفظ",
            "teachers_list.pdf",
            "PDF Files (*.pdf)"
        )

        if not name:
            return

        if not name.endswith(".pdf"):
            name += ".pdf"

        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount() - 1)]  # استثناء عمود الحذف
        data = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            row_data = []
            for col in range(self.table.columnCount() - 1):  # استثناء عمود الحذف
                item = self.table.item(row, col)
                if item is None:
                    print(f"⚠️ تحذير: خلية فارغة في الصف {row}, العمود {col}")
                    row_data.append("")
                else:
                    row_data.append(item.text())
            if not any(row_data):  # تحقق إذا كان الصف فارغًا بالكامل
                print(f"⚠️ تحذير: صف فارغ تم تجاهله في الصف {row}")
                continue
            data.append(row_data)

        try:
            print(f"📤 محاولة تصدير التقرير إلى: {name}")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            export_to_pdf(
                name,
                headers,
                data,
                report_title="قائمة الأساتذة",
                show_total=False
            )
            QMessageBox.information(self,"تم", "تم تصدير التقرير إلى PDF بنجاح")
        except Exception as e:
            print(f"❌ خطأ أثناء تصدير التقرير: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ أثناء تصدير التقرير: {e}")

    def confirm_delete(self, teacher_id):
        confirm = QMessageBox.question(self, "تأكيد الحذف", "❗ هل تريد حذف هذا الأستاذ؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            delete_teacher(teacher_id)
            self.load_teachers()
            self.clear_fields()