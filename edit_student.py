from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QCheckBox
)
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtCore import QDate
from database import update_student, update_student, get_all_subjects, get_subjects_for_student, set_student_subjects
class EditStudentWindow(QWidget):
    def __init__(self, student_data, refresh_callback):
        super().__init__()
        self.setWindowTitle("تعديل بيانات التلميذ")
        self.setGeometry(500, 150, 300, 250)

        self.student_id = student_data[0]
        self.refresh_callback = refresh_callback

        layout = QVBoxLayout()  # ✅ أنشأناه أولاً

        self.name_input = QLineEdit(student_data[1])
        self.class_input = QLineEdit(student_data[2])
        self.birth_input = QDateEdit()
        self.birth_input.setDisplayFormat("yyyy-MM-dd")
        self.birth_input.setCalendarPopup(True)

        date_str = student_data[3]
        if date_str:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            if qdate.isValid():
                self.birth_input.setDate(qdate)
            else:
                self.birth_input.setDate(QDate.currentDate())
        else:
            self.birth_input.setDate(QDate.currentDate())

        self.phone_input = QLineEdit(student_data[4])

        layout.addWidget(QLabel("الاسم"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("القسم"))
        layout.addWidget(self.class_input)

        layout.addWidget(QLabel("تاريخ الميلاد"))
        layout.addWidget(self.birth_input)

        layout.addWidget(QLabel("هاتف الولي"))
        layout.addWidget(self.phone_input)

        # ✅ المواد الدراسية داخل QScrollArea
        layout.addWidget(QLabel("المواد الدراسية"))
        from PyQt5.QtWidgets import QScrollArea, QWidget
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        subjects_layout = QVBoxLayout()
        self.subject_checkboxes = []
        all_subjects = get_all_subjects()
        student_subjects = get_subjects_for_student(self.student_id)

        for subject_id, subject_name in all_subjects:
            checkbox = QCheckBox(subject_name)
            checkbox.setChecked(subject_name in student_subjects)
            checkbox.subject_id = subject_id
            self.subject_checkboxes.append(checkbox)
            subjects_layout.addWidget(checkbox)

        scroll_widget.setLayout(subjects_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)  # يسمح بتغيير حجم المحتوى
        scroll_area.setFixedHeight(100)  # تحديد ارتفاع ثابت للمربع
        layout.addWidget(scroll_area)

        save_button = QPushButton("💾 حفظ التعديلات")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_changes(self):
        update_student(
            self.student_id,
            self.name_input.text(),
            self.class_input.text(),
            self.birth_input.date().toString("yyyy-MM-dd"),
            self.phone_input.text()
        )
        selected_subject_ids = [
            cb.subject_id for cb in self.subject_checkboxes if cb.isChecked()
        ]

        # تعيين المواد الجديدة للتلميذ
        set_student_subjects(self.student_id, selected_subject_ids)

        QMessageBox.information(self, "تم", "تم حفظ التعديلات.")
        self.refresh_callback()  # إعادة تحميل الجدول
        self.close()