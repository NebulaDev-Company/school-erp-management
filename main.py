import sys
import os
import shutil
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGroupBox, QFrame, QStackedWidget, QMessageBox, QFileDialog,
    QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from database import (create_table, create_expenses_table, create_subjects_table,
    create_teachers_table, create_teacher_subject_table, create_student_subject_table)
from add_student import AddStudentWindow
from student_table import StudentsTableWindow
from add_payment import AddPaymentWindow
from payments_table import PaymentsTableWindow
from payment_summary import PaymentSummaryWindow
from students_without_payment import StudentsWithoutPaymentWindow
from students_late_this_month import StudentsLateThisMonthWindow
from payments_by_month import PaymentsByMonthWindow
from charts_window import ChartsWindow
from payment_pie_chart import PaymentPieChartWindow
from yearly_comparison_chart import YearlyComparisonChart
from students_monthly_chart import StudentsMonthlyChart
from add_expense import AddExpenseWindow
from expenses_table import ExpensesTableWindow
from income_vs_expense_chart import IncomeVsExpenseChart
from subjects_window import SubjectsWindow
from teachers_window import TeachersWindow
from archived_students_window import ArchivedStudentsWindow

class MainDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المدرسة")
        self.setGeometry(100, 100, 900, 600)
        self.is_dark = True

        self.stack = QStackedWidget()
        self.dashboard_page = QWidget()
        self.init_dashboard_ui()
        self.init_settings_ui()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.settings_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.apply_theme()

    def init_dashboard_ui(self):
        self.theme_button = QPushButton("☀")
        self.theme_button.setStyleSheet("font-size: 18px; padding: 5px 15px; border-radius: 10px;")
        self.theme_button.clicked.connect(self.toggle_theme)

        self.settings_button = QPushButton("⚙ الإعدادات")
        self.settings_button.setStyleSheet("font-size: 16px; padding: 5px 15px; border-radius: 8px;")
        self.settings_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_page))

        self.school_name_label = QLabel("🏫 Nebula School")
        self.school_name_label.setStyleSheet("font-size: 28px; font-weight: bold; margin: 15px; text-align: center;")
        self.school_name_label.setAlignment(Qt.AlignCenter)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.settings_button)
        top_bar.addStretch()
        top_bar.addWidget(self.theme_button)

        layout = QVBoxLayout()
        layout.addWidget(self.school_name_label)
        layout.addLayout(top_bar)
        layout.addWidget(self.build_scroll_area())
        self.dashboard_page.setLayout(layout)

    def init_settings_ui(self):
        self.settings_page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("⚙ الإعدادات")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        back_button = QPushButton("⬅ العودة للرئيسية")
        back_button.setStyleSheet("font-size: 16px; padding: 10px 20px; border-radius: 8px;")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.dashboard_page))
        layout.addWidget(back_button)

        backup_btn = QPushButton("📦 النسخ الاحتياطي للبيانات")
        backup_btn.setStyleSheet("font-size: 16px; padding: 10px 20px; border-radius: 8px;")
        backup_btn.clicked.connect(self.backup_database)
        layout.addWidget(backup_btn)

        restore_btn = QPushButton("♻ استرجاع نسخة محفوظة")
        restore_btn.setStyleSheet("font-size: 16px; padding: 10px 20px; border-radius: 8px;")
        restore_btn.clicked.connect(self.restore_database)
        layout.addWidget(restore_btn)

        layout.addStretch()
        self.settings_page.setLayout(layout)

    def build_scroll_area(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)

        container_layout.addWidget(self.build_section("👥 التلاميذ", [
            ("+ إضافة تلميذ", self.open_add_student_window),
            ("👨‍🏫 عرض قائمة التلاميذ", self.open_students_table_window),
            ("📦 عرض التلاميذ المؤرشفين", self.open_archived_students_window)
        ]))

        container_layout.addWidget(self.build_section("💵 المدفوعات", [
            ("📥 تسجيل دفع", self.open_payment_window),
            ("💳 عرض المدفوعات", self.open_payments_window),
            ("📊 ملخص المدفوعات", self.open_summary_window)
        ]))

        container_layout.addWidget(self.build_section("📅 التقارير الشهرية", [
            ("🚫 من لم يدفع إطلاقًا", self.open_no_payment_window),
            ("📆 من لم يدفع هذا الشهر", self.open_late_this_month_window),
            ("📆 مدفوعات شهر معين", self.open_monthly_window)
        ]))

        container_layout.addWidget(self.build_section("📈 الإحصائيات", [
            ("📈 تقارير بيانية", self.open_charts_window),
            ("📊 نسبة الدفع", self.open_pie_chart_window),
            ("📊 مقارنة سنوات", self.open_yearly_comparison_chart),
            ("📊 تلاميذ جدد بالأشهر", self.open_students_monthly_chart)
        ]))

        container_layout.addWidget(self.build_section("🧾 المصروفات", [
            ("+ إضافة مصروف", self.open_add_expense_window),
            ("📋 عرض المصروفات", self.open_expenses_table_window),
            ("📊 مقارنة المصاريف والمداخيل", self.open_income_vs_expense_chart)
        ]))

        container_layout.addWidget(self.build_section("👨‍🏫 الأساتذة والمواد", [
            ("👨‍🏫 إدارة الأساتذة", self.open_teachers_window),
            ("📚 إدارة المواد", self.open_subjects_window),
        ]))

        container_layout.addStretch()
        scroll_area.setWidget(container)
        return scroll_area

    def build_section(self, title, buttons):
        box = QGroupBox()
        box.setTitle(title)
        box.setStyleSheet("font-size: 18px; font-weight: bold; border: 2px solid #555; border-radius: 12px; padding: 10px; qproperty-cursor: PointingHandCursor;")
        layout = QVBoxLayout()
        layout.setSpacing(5)

        for label, callback in buttons:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            base_style = """
                font-size: 14px;
                padding: 8px 15px; border-radius: 8px; qproperty-cursor: PointingHandCursor;
                transition: all 0.3s;
            """
            if self.is_dark:
                btn.setStyleSheet(base_style + """
                    background: #444; color: #e0e0e0; border: 1px solid #555;
                """ + """
                    &:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #666);
                        border: 1px solid #777;
                    }
                """)
            else:
                btn.setStyleSheet(base_style + """
                    background: #e0e0e0; color: #333; border: 1px solid #ccc;
                """ + """
                    &:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d0d0d0, stop:1 #c0c0c0);
                        border: 1px solid #aaa;
                    }
                """)
            layout.addWidget(btn)

        box.setStyleSheet(box.styleSheet() + """
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 5px 10px;
                border-radius: 8px;
                background: #444;
                color: #e0e0e0;
                border: 1px solid #555;
            }
            QGroupBox::title:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #666);
                border: 1px solid #777;
            }
        """ if self.is_dark else """
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 5px 10px;
                border-radius: 8px;
                background: #080000FF;
                color: #333;
                border: 1px solid #ccc;
            }
            QGroupBox::title:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d0d0d0, stop:1 #c0c0c0);
                border: 1px solid #aaa;
            }
        """)
        box.setLayout(layout)
        return box

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    def apply_theme(self):
        base_style = """
            QWidget {
                font-family: 'Cairo', sans-serif;
            }
            QScrollArea {
                border: none;
            }
            QGroupBox {
                border-radius: 12px;
                margin-top: 1ex;
            }
            QPushButton {
                padding: 10px;
                border-radius: 8px;
                transition: all 0.3s;
            }
            QCheckBox {
                font-size: 12px;
                font-weight: bold;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
            }
        """
        if self.is_dark:
            self.theme_button.setText("☀")
            style = base_style + """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2e2e2e, stop:1 #252525);
                    color: #e0e0e0;
                }
                QPushButton {
                    background: #444;
                    border: 1px solid #555;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #666);
                    border: 1px solid #777;
                }
                QGroupBox {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a3a, stop:1 #2e2e2e);
                    border: 2px solid #555;
                }
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #e0e0e0;
                }
                QCheckBox {
                    font-size: 12px;
                    # background: #444;
                    # color: #e0e0e0;
                }
                QCheckBox::indicator {
                    border: 2px solid #999999;
                    background: #555;
                }
                QCheckBox::indicator:checked {
                    background: #777;
                    border: 2px solid #999999;
                }
                QCheckBox::indicator:unchecked:hover {
                    border: 2px solid #777777;
                }
            """
        else:
            self.theme_button.setText("🌙")
            style = base_style + """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f0f0, stop:1 #e0e0e0);
                    color: #333;
                }
                QPushButton {
                    background: #e0e0e0;
                    border: 1px solid #ccc;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d0d0d0, stop:1 #c0c0c0);
                    border: 1px solid #aaa;
                }
                QGroupBox {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
                    border: 2px solid #ccc;
                }
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                }
                QCheckBox {
                    background: #ffffff;
                    color: #333;
                }
                QCheckBox::indicator {
                    border: 2px solid #cccccc;
                    background: #f0f0f0;
                }
                QCheckBox::indicator:checked {
                    background: #aaaaaa;
                    border: 2px solid #cccccc;
                }
                QCheckBox::indicator:unchecked:hover {
                    border: 2px solid #aaaaaa;
                }
                QComboBox {
                    background: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 3px;
                    border-radius: 4px;
                    background: #f0f0f0;
                }
            """
        self.setStyleSheet(style)
        self.dashboard_page.setStyleSheet(style)
        self.settings_page.setStyleSheet(style)

    def backup_database(self):
        try:
            db_path = "school.db"
            backup_path, _ = QFileDialog.getSaveFileName(self, "احفظ النسخة الاحتياطية", "", "Database Files (*.db)")
            if backup_path:
                if not backup_path.endswith(".db"):
                    backup_path += ".db"
                shutil.copyfile(db_path, backup_path)
                self.show_message("✅ تم حفظ النسخة الاحتياطية بنجاح.")
        except Exception as e:
            self.show_message(f"❌ فشل في النسخ الاحتياطي: {e}")

    def restore_database(self):
        try:
            db_path = "school.db"
            restore_path, _ = QFileDialog.getOpenFileName(self, "اختر النسخة الاحتياطية للاسترجاع", "", "Database Files (*.db)")
            if restore_path:
                shutil.copyfile(restore_path, db_path)
                self.show_message("✅ تم استرجاع البيانات بنجاح. أعد تشغيل التطبيق لرؤية التغييرات.")
        except Exception as e:
            self.show_message(f"❌ فشل في استرجاع البيانات: {e}")

    def show_message(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("تنبيه")
        msg.setText(text)
        msg.setStyleSheet(f"background-color: {'#333' if self.is_dark else '#f0f0f0'}; color: {'#e0e0e0' if self.is_dark else '#333'}; font-family: 'Cairo';")
        msg.exec_()

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

    def open_charts_window(self):
        self.charts_window = ChartsWindow()
        self.charts_window.show()
        self.charts_window.setStyleSheet(self.styleSheet())

    def open_pie_chart_window(self):
        self.pie_chart_window = PaymentPieChartWindow()
        self.pie_chart_window.show()
        self.pie_chart_window.setStyleSheet(self.styleSheet())

    def open_yearly_comparison_chart(self):
        self.yearly_comparison_chart = YearlyComparisonChart()
        self.yearly_comparison_chart.show()
        self.yearly_comparison_chart.setStyleSheet(self.styleSheet())

    def open_students_monthly_chart(self):
        self.students_monthly_chart = StudentsMonthlyChart()
        self.students_monthly_chart.show()
        self.students_monthly_chart.setStyleSheet(self.styleSheet())

    def open_add_expense_window(self):
        self.add_expense_window = AddExpenseWindow()
        self.add_expense_window.show()
        self.add_expense_window.setStyleSheet(self.styleSheet())

    def open_expenses_table_window(self):
        self.expenses_table_window = ExpensesTableWindow()
        self.expenses_table_window.show()
        self.expenses_table_window.setStyleSheet(self.styleSheet())

    def open_income_vs_expense_chart(self):
        self.income_vs_expense_chart = IncomeVsExpenseChart()
        self.income_vs_expense_chart.show()
        self.income_vs_expense_chart.setStyleSheet(self.styleSheet())

    def open_subjects_window(self):
        self.subjects_window = SubjectsWindow()
        self.subjects_window.show()
        self.subjects_window.setStyleSheet(self.styleSheet())

    def open_teachers_window(self):
        self.teachers_window = TeachersWindow()
        self.teachers_window.show()
        self.teachers_window.setStyleSheet(self.styleSheet())

    def open_archived_students_window(self):
        self.archived_window = ArchivedStudentsWindow()
        self.archived_window.show()
        self.archived_window.setStyleSheet(self.styleSheet())

if __name__ == "__main__":
    create_table()
    create_expenses_table()
    create_subjects_table()
    create_teachers_table()
    create_teacher_subject_table()
    create_student_subject_table()
    app = QApplication(sys.argv)
    window = MainDashboard()
    window.show()
    sys.exit(app.exec_())
# to run the program
# source venv/bin/activate
# python main.py
