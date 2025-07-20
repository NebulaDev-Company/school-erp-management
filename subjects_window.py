# file: subjects_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
import sqlite3

class SubjectsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📚 إدارة المواد")
        self.setGeometry(300, 200, 400, 400)
        layout = QVBoxLayout()

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("اسم المادة")
        layout.addWidget(self.subject_input)

        add_btn = QPushButton("➕ إضافة مادة")
        add_btn.clicked.connect(self.add_subject)
        layout.addWidget(add_btn)

        self.subject_list = QListWidget()
        layout.addWidget(self.subject_list)

        delete_btn = QPushButton("🗑️ حذف المادة المحددة")
        delete_btn.clicked.connect(self.delete_subject)
        layout.addWidget(delete_btn)

        self.setLayout(layout)
        self.load_subjects()

    def load_subjects(self):
        self.subject_list.clear()
        conn = sqlite3.connect("school.db")
        c = conn.cursor()
        c.execute("SELECT id, name FROM subjects")
        for row in c.fetchall():
            self.subject_list.addItem(f"{row[0]} - {row[1]}")
        conn.close()

    def add_subject(self):
        name = self.subject_input.text().strip()
        if not name:
            QMessageBox.warning(self, "تحذير", "⚠️ أدخل اسم المادة.")
            return
        conn = sqlite3.connect("school.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
            self.load_subjects()
            self.subject_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "خطأ", "❌ هذه المادة موجودة مسبقًا.")
        conn.close()

    def delete_subject(self):
        selected = self.subject_list.currentItem()
        if not selected:
            return
        subject_id = selected.text().split(" - ")[0]
        conn = sqlite3.connect("school.db")
        c = conn.cursor()
        c.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
        self.load_subjects()
