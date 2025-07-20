from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDateEdit
from PyQt5.QtCore import QDate
from database import create_connection

class AddExpenseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📝 تسجيل مصروف")
        self.setGeometry(400, 200, 300, 250)

        layout = QVBoxLayout()

        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("📦 اسم الشيء الذي تم شراؤه")
        layout.addWidget(self.item_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("💰 السعر")
        layout.addWidget(self.amount_input)

        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(QLabel("📅 تاريخ الشراء:"))
        layout.addWidget(self.date_input)

        self.save_btn = QPushButton("✅ حفظ المصروف")
        self.save_btn.clicked.connect(self.save_expense)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_expense(self):
        item = self.item_input.text()
        amount = self.amount_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not item or not amount:
            QMessageBox.warning(self, "⚠️ خطأ", "يرجى ملء جميع الحقول")
            return

        try:
            float(amount)
        except:
            QMessageBox.warning(self, "⚠️ خطأ", "السعر يجب أن يكون رقماً")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (item, amount, date) VALUES (?, ?, ?)", (item, amount, date))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "تم", "✅ تم تسجيل المصروف")
        self.close()
