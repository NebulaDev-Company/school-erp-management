from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.font_manager as fm
from matplotlib import rcParams
from database import get_new_students_monthly_by_years

# 📌 خط عربي
font_path = "fonts/Amiri-Regular.ttf"
fm.fontManager.addfont(font_path)
rcParams['font.family'] = 'Amiri'

def reshape_ar(text):
    return get_display(arabic_reshaper.reshape(text))

class StudentsMonthlyChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 التلاميذ الجدد حسب الأشهر")
        self.setGeometry(350, 150, 800, 500)

        layout = QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.export_btn = QPushButton("💾 تصدير الرسم")
        self.export_btn.clicked.connect(self.export_chart)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)
        self.plot()

    def plot(self):
        years = ["2023", "2024", "2025"]  # يمكنك جعلها ديناميكية لاحقًا
        data = get_new_students_monthly_by_years(years)

        months = [
            reshape_ar("جانفي"), reshape_ar("فيفري"), reshape_ar("مارس"),
            reshape_ar("أفريل"), reshape_ar("ماي"), reshape_ar("جوان"),
            reshape_ar("جويلية"), reshape_ar("أوت"), reshape_ar("سبتمبر"),
            reshape_ar("أكتوبر"), reshape_ar("نوفمبر"), reshape_ar("ديسمبر")
        ]

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        for year in years:
            ax.plot(months, data[year], label=reshape_ar(f"سنة {year}"), marker='o')

        ax.set_title(reshape_ar("📈 عدد التلاميذ الجدد حسب الأشهر"))
        ax.set_ylabel(reshape_ar("عدد التلاميذ"))
        ax.set_xlabel(reshape_ar("الشهر"))
        ax.legend()
        ax.tick_params(axis='x', labelrotation=45)

        self.canvas.draw()

    def export_chart(self):
        path, _ = QFileDialog.getSaveFileName(
            self, reshape_ar("احفظ الرسم"), "", "PNG Files (*.png)"
        )
        if path:
            if not path.endswith(".png"):
                path += ".png"
            self.figure.savefig(path)
