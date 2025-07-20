from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import arabic_reshaper
from bidi.algorithm import get_display
from database import get_monthly_income_by_year
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm

# إعداد الخط العربي Amiri
font_path = "fonts/Amiri-Regular.ttf"  # تأكيد المسار إلى ملف الخط
fm.fontManager.addfont(font_path)
rcParams['font.family'] = 'Amiri'

def reshape_ar(text):
    return get_display(arabic_reshaper.reshape(text))

class ChartsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("التقارير البيانية")
        self.setGeometry(350, 150, 700, 500)

        layout = QVBoxLayout()

        self.year_selector = QComboBox()
        self.year_selector.addItems(["2022", "2023", "2024", "2025"])
        self.year_selector.currentTextChanged.connect(self.update_chart)
        layout.addWidget(QLabel("اختر السنة:"))
        layout.addWidget(self.year_selector)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.update_chart()
        
        self.export_btn = QPushButton("💾 تصدير الصورة")
        self.export_btn.clicked.connect(self.export_chart)
        layout.addWidget(self.export_btn)

    def update_chart(self):
        year = self.year_selector.currentText()
        monthly_data = get_monthly_income_by_year(year)

        months = [
            reshape_ar("يناير"), reshape_ar("فبراير"), reshape_ar("مارس"),
            reshape_ar("أفريل"), reshape_ar("ماي"), reshape_ar("جوان"),
            reshape_ar("جويلية"), reshape_ar("أوت"), reshape_ar("سبتمبر"),
            reshape_ar("أكتوبر"), reshape_ar("نوفمبر"), reshape_ar("ديسمبر")
        ]

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(months, monthly_data, color="#007ACC")
        ax.set_title(reshape_ar(f"مداخيل سنة {year}")) 
        ax.set_ylabel(reshape_ar("المبلغ (DA)"))
        ax.set_xlabel(reshape_ar("الشهر"))
        ax.tick_params(axis='x', labelrotation=45)

        self.canvas.draw()
    def export_chart(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "احفظ المخطط", "", "PNG Files (*.png)"
        )
        if path:
            self.figure.savefig(path)
