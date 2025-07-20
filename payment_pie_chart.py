from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import arabic_reshaper
from bidi.algorithm import get_display
from database import get_paid_vs_unpaid_counts
import matplotlib.font_manager as fm
from matplotlib import rcParams

# إعداد الخط العربي Amiri
font_path = "fonts/Amiri-Regular.ttf"  # تأكد من وجود الملف في المسار المحدد
fm.fontManager.addfont(font_path)
rcParams['font.family'] = 'Amiri'

def reshape_ar(text):
    return get_display(arabic_reshaper.reshape(text))
class PaymentPieChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نسبة التلاميذ الذين دفعوا الرسوم الدراسية والذين لم يدفعوها")
        self.setGeometry(400, 150, 500, 400)

        layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
                
        self.export_btn = QPushButton("💾 تصدير الصورة")
        self.export_btn.clicked.connect(self.export_chart)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)
        self.draw_pie()

    def draw_pie(self):
        paid, unpaid = get_paid_vs_unpaid_counts()

        labels = [reshape_ar("دفعوا"), reshape_ar("لم يدفعوا")]
        sizes = [paid, unpaid]
        colors = ['#28a745', '#dc3545']

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 12}
        )
        ax.axis('equal')
        ax.set_title(reshape_ar("نسبة التلاميذ الذين دفعوا الرسوم الدراسية والذين لم يدفعوها"), fontsize=14)
        self.canvas.draw()
    
    def export_chart(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "احفظ المخطط", "", "PNG Files (*.png)"
        )
        if path:
            self.figure.savefig(path)
