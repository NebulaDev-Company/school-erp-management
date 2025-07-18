import sys
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout
)
from database import create_table
from add_student import AddStudentWindow
from student_table import StudentsTableWindow
from add_payment import AddPaymentWindow
from payments_table import PaymentsTableWindow
from payment_summary import PaymentSummaryWindow
from students_without_payment import StudentsWithoutPaymentWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المدرسة")
        self.setGeometry(100, 100, 800, 600)

        self.add_student_button = QPushButton("إضافة تلميذ")
        self.add_student_button.clicked.connect(self.open_add_student_window)

        self.view_students_button = QPushButton("عرض قائمة التلاميذ")
        self.view_students_button.clicked.connect(self.open_students_table_window)

        self.payment_button = QPushButton("📥 تسجيل دفع")
        self.payment_button.clicked.connect(self.open_payment_window)

        self.view_payments_button = QPushButton("💳 عرض المدفوعات")
        self.view_payments_button.clicked.connect(self.open_payments_window)

        self.summary_button = QPushButton("📊 ملخص المدفوعات")
        self.summary_button.clicked.connect(self.open_summary_window)
        
        self.no_payment_button = QPushButton("🚫 من لم يدفع إطلاقًا")
        self.no_payment_button.clicked.connect(self.open_no_payment_window)

        layout = QVBoxLayout()
        layout.addWidget(self.add_student_button)
        layout.addWidget(self.view_students_button)
        layout.addWidget(self.payment_button)
        layout.addWidget(self.view_payments_button)
        layout.addWidget(self.summary_button)
        layout.addWidget(self.no_payment_button)
        
        self.setLayout(layout)

    def open_add_student_window(self):
        self.add_student_window = AddStudentWindow()
        self.add_student_window.show()

    def open_students_table_window(self):
        self.students_table_window = StudentsTableWindow()
        self.students_table_window.show()

    def open_payment_window(self):
        self.payment_window = AddPaymentWindow()
        self.payment_window.show()

    def open_payments_window(self):
        self.payments_window = PaymentsTableWindow()
        self.payments_window.show()


    def open_summary_window(self):
        self.summary_window = PaymentSummaryWindow()
        self.summary_window.show()

    def open_no_payment_window(self):
        self.no_payment_window = StudentsWithoutPaymentWindow()
        self.no_payment_window.show()


if __name__ == "__main__":
    create_table()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# to run the program
# source venv/bin/activate
# python main.py
