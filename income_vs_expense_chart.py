from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QFileDialog, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database import get_monthly_income_and_expenses_by_year
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.font_manager as fm
from matplotlib import rcParams

# إعداد الخط
font_path = "fonts/Amiri-Regular.ttf"
fm.fontManager.addfont(font_path)
rcParams['font.family'] = 'Amiri'

def reshape_ar(text):
    return get_display(arabic_reshaper.reshape(text))

class IncomeVsExpenseChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" مقارنة المصاريف والمداخيل الشهرية")
        self.setGeometry(300, 150, 800, 500)

        layout = QVBoxLayout()

        self.year_selector = QComboBox()
        self.year_selector.addItems(["2023", "2024", "2025"])
        self.year_selector.currentTextChanged.connect(self.update_chart)

        layout.addWidget(QLabel("📅 اختر السنة:"))
        layout.addWidget(self.year_selector)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.export_btn = QPushButton("💾 تصدير الرسم كـ PNG")
        self.export_btn.clicked.connect(self.export_chart)
        layout.addWidget(self.export_btn)
        
        self.setLayout(layout)
        self.update_chart()

    def update_chart(self):
        year = self.year_selector.currentText()
        income, expenses = get_monthly_income_and_expenses_by_year(year)

        months = [
            reshape_ar("جانفي"), reshape_ar("فيفري"), reshape_ar("مارس"),
            reshape_ar("أفريل"), reshape_ar("ماي"), reshape_ar("جوان"),
            reshape_ar("جويلية"), reshape_ar("أوت"), reshape_ar("سبتمبر"),
            reshape_ar("أكتوبر"), reshape_ar("نوفمبر"), reshape_ar("ديسمبر")
        ]

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        bar_width = 0.35
        x = list(range(12))

        ax.bar([i - bar_width/2 for i in x], income, width=bar_width, label=reshape_ar(" المداخيل"), color="#4CAF50")
        ax.bar([i + bar_width/2 for i in x], expenses, width=bar_width, label=reshape_ar(" المصاريف"), color="#F44336")

        ax.set_title(reshape_ar(f" مقارنة المداخيل والمصاريف - {year}"))
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45)
        ax.set_ylabel(reshape_ar("المبلغ (DA)"))
        ax.set_xlabel(reshape_ar("الشهر"))
        ax.legend()

        self.canvas.draw()
    def export_chart(self):
        path, _ = QFileDialog.getSaveFileName(
            self, reshape_ar("احفظ الرسم"), "", "PNG Files (*.png)"
        )
        if path:
            if not path.endswith(".png"):
                path += ".png"
            self.figure.savefig(path)
