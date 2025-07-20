from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QDateEdit,
    QCheckBox, QScrollArea, QGroupBox
)
from PyQt5.QtCore import QDate
from database import create_table, create_connection, get_all_subjects, set_student_subjects
from datetime import datetime

class AddStudentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إضافة تلميذ")
        self.setGeometry(1000, 100, 350, 700)

        # عناصر الإدخال
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم التلميذ")

        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("القسم")

        self.birth_input = QDateEdit()
        self.birth_input.setDisplayFormat("yyyy-MM-dd")
        self.birth_input.setCalendarPopup(True)
        self.birth_input.setDate(QDate.currentDate())
        self.birth_input.setMinimumDate(QDate(1990, 1, 1))
        self.birth_input.setMaximumDate(QDate.currentDate())

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("هاتف الولي")

        self.submit_button = QPushButton("حفظ")
        self.submit_button.clicked.connect(self.save_student)

        # قائمة CheckBoxes للمواد
        self.subject_checkboxes = []
        self.subject_box = QVBoxLayout()
        self.load_subject_checkboxes()

        # نقل العنوان خارج السكرول
        subject_label = QLabel("اختر مواد الدراسة:")
        subject_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 10px;")

        group = QGroupBox()
        group.setLayout(self.subject_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(QVBoxLayout())
        scroll_content.layout().addWidget(group)
        scroll.setWidget(scroll_content)

        # التخطيط العام
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(QLabel("اسم التلميذ"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("القسم"))
        layout.addWidget(self.class_input)

        layout.addWidget(QLabel("تاريخ الميلاد"))
        layout.addWidget(self.birth_input)

        layout.addWidget(QLabel("رقم ولي الأمر"))
        layout.addWidget(self.phone_input)

        layout.addWidget(subject_label)
        layout.addWidget(scroll)
        layout.addWidget(self.submit_button)

        # تطبيق StyleSheet محلي
        self.setStyleSheet("""
            # QCheckBox {
            #     font-size: 20px;
            #     font-weight: bold;
            #     spacing: 10px;
            # }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
            }
            QLabel {
                font-size: 16px;
            }
            QLineEdit, QDateEdit, QPushButton {
                font-size: 16px;
                padding: 5px;
            }
        """)

        self.setLayout(layout)

    def load_subject_checkboxes(self):
        subjects = get_all_subjects()
        for subject_id, subject_name in subjects:
            checkbox = QCheckBox(subject_name)
            checkbox.setObjectName(str(subject_id))
            self.subject_checkboxes.append(checkbox)
            self.subject_box.addWidget(checkbox)

    def save_student(self):
        name = self.name_input.text()
        class_ = self.class_input.text()
        birthdate = self.birth_input.date().toString("yyyy-MM-dd")
        phone = self.phone_input.text()
        registration_date = datetime.now().strftime("%Y-%m-%d")

        if name == "" or class_ == "":
            QMessageBox.warning(self, "خطأ", "الاسم والقسم مطلوبان.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, class, birthdate, parent_phone, registration_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, class_, birthdate, phone, registration_date))
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # جلب المواد المختارة
        selected_subject_ids = [
            int(cb.objectName()) for cb in self.subject_checkboxes if cb.isChecked()
        ]
        if selected_subject_ids:
            set_student_subjects(student_id, selected_subject_ids)

        QMessageBox.information(self, "تم", "تم حفظ التلميذ بنجاح!")

        # تفريغ الحقول
        self.name_input.clear()
        self.class_input.clear()
        self.birth_input.setDate(QDate.currentDate())
        self.phone_input.clear()
        for cb in self.subject_checkboxes:
            cb.setChecked(False)