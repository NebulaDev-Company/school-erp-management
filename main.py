import sys
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from database import create_table
from add_student import AddStudentWindow
from student_table import StudentsTableWindow
from add_payment import AddPaymentWindow
from payments_table import PaymentsTableWindow
from payment_summary import PaymentSummaryWindow
from students_without_payment import StudentsWithoutPaymentWindow
from students_late_this_month import StudentsLateThisMonthWindow
from payments_by_month import PaymentsByMonthWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المدرسة")
        self.setGeometry(100, 100, 800, 600)
        self.is_dark = True

        self.theme_button = QPushButton("☀️")
        self.theme_button.clicked.connect(self.toggle_theme)

        self.school_name_label = QLabel("🏫 Nebula School")
        self.school_name_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.school_name_label.setAlignment(Qt.AlignCenter)

        self.add_student_button = QPushButton("➕ إضافة تلميذ")
        self.add_student_button.clicked.connect(self.open_add_student_window)

        self.view_students_button = QPushButton("👨‍🏫 عرض قائمة التلاميذ")
        self.view_students_button.clicked.connect(self.open_students_table_window)

        self.payment_button = QPushButton("📥 تسجيل دفع")
        self.payment_button.clicked.connect(self.open_payment_window)

        self.view_payments_button = QPushButton("💳 عرض المدفوعات")
        self.view_payments_button.clicked.connect(self.open_payments_window)

        self.summary_button = QPushButton("📊 ملخص المدفوعات")
        self.summary_button.clicked.connect(self.open_summary_window)

        self.no_payment_button = QPushButton("🚫 من لم يدفع إطلاقًا")
        self.no_payment_button.clicked.connect(self.open_no_payment_window)

        self.late_this_month_button = QPushButton("📆 من لم يدفع هذا الشهر")
        self.late_this_month_button.clicked.connect(self.open_late_this_month_window)
        
        self.monthly_button = QPushButton("📆 مدفوعات شهر معين")
        self.monthly_button.clicked.connect(self.open_monthly_window)

        # Layout for buttons
        inner_widget = QFrame()
        inner_layout = QVBoxLayout(inner_widget)
        for btn in [
            self.add_student_button, self.view_students_button, self.payment_button,
            self.view_payments_button, self.summary_button, self.no_payment_button,
            self.late_this_month_button, self.monthly_button
        ]:
            inner_layout.addWidget(btn)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner_widget)

        # Main layout
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.theme_button)

        layout = QVBoxLayout()
        layout.addWidget(self.school_name_label)
        layout.addLayout(top_layout)
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.apply_dark_mode()

    def toggle_theme(self):
        if self.is_dark:
            self.apply_light_mode()
            self.theme_button.setText("🌙")
        else:
            self.apply_dark_mode()
            self.theme_button.setText("☀️")
        self.is_dark = not self.is_dark

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: white;
                font-family: Cairo;
            }
            QPushButton {
                background-color: #444;
                border: none;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

    def apply_light_mode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                color: black;
                font-family: Cairo;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)

    def open_add_student_window(self):
        self.add_student_window = AddStudentWindow()
        self.add_student_window.show()
        self.add_student_window.setStyleSheet(self.styleSheet())

    def open_students_table_window(self):
        self.students_table_window = StudentsTableWindow()
        self.students_table_window.show()
        self.students_table_window.setStyleSheet(self.styleSheet())

    def open_payment_window(self):
        self.payment_window = AddPaymentWindow()
        self.payment_window.show()
        self.payment_window.setStyleSheet(self.styleSheet())

    def open_payments_window(self):
        self.payments_window = PaymentsTableWindow()
        self.payments_window.show()
        self.payments_window.setStyleSheet(self.styleSheet())

    def open_summary_window(self):
        self.summary_window = PaymentSummaryWindow()
        self.summary_window.show()
        self.summary_window.setStyleSheet(self.styleSheet())

    def open_no_payment_window(self):
        self.no_payment_window = StudentsWithoutPaymentWindow()
        self.no_payment_window.show()
        self.no_payment_window.setStyleSheet(self.styleSheet())

    def open_late_this_month_window(self):
        self.late_window = StudentsLateThisMonthWindow()
        self.late_window.show()
        self.late_window.setStyleSheet(self.styleSheet())
        
    def open_monthly_window(self):
        self.monthly_window = PaymentsByMonthWindow()
        self.monthly_window.show()
        self.monthly_window.setStyleSheet(self.styleSheet())


if __name__ == "__main__":
    create_table()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# to run the program
# source venv/bin/activate
# python main.py
