from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QComboBox, QDateEdit
from PyQt5.QtCore import QDate

from database import get_all_students, save_payment, create_payment_table

create_payment_table()
class AddPaymentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📥 تسجيل دفع")
        self.setGeometry(600, 200, 300, 250)

        self.student_combo = QComboBox()
        self.load_students()

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("المبلغ")

        self.date_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())  # اليوم تلقائيًا
        

        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("ملاحظة (اختياري)")

        save_button = QPushButton("💾 حفظ الدفع")
        save_button.clicked.connect(self.save_payment)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("اسم التلميذ"))
        layout.addWidget(self.student_combo)

        layout.addWidget(QLabel("المبلغ"))
        layout.addWidget(self.amount_input)

        layout.addWidget(QLabel("تاريخ الدفع"))
        layout.addWidget(self.date_input)

        layout.addWidget(QLabel("ملاحظة"))
        layout.addWidget(self.note_input)

        layout.addWidget(save_button)
        self.setLayout(layout)

    def load_students(self):
        students = get_all_students()
        for student in students:
            self.student_combo.addItem(f"{student[1]} (ID: {student[0]})", student[0])

    def save_payment(self):
        from database import save_payment

        student_id = self.student_combo.currentData()
        amount = self.amount_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")
        note = self.note_input.text()

        if not amount or not date:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال المبلغ والتاريخ.")
            return

        try:
            amount = float(amount)
            formatted_amount = "{:.2f} DA".format(amount)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "المبلغ غير صحيح.")
            return


        save_payment(student_id, amount, date, note)
        QMessageBox.information(self, "تم", "تم حفظ الدفع بنجاح.")
        self.close()
