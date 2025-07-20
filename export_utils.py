from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import arabic_reshaper 
from bidi.algorithm import get_display
import os

def export_to_pdf(filename, headers, data, report_title="تقرير", show_total=False):
    def reshape_arabic(text):
        return get_display(arabic_reshaper.reshape(text))

    def wrap_text(text, max_width, c, is_materials=False):
        c.setFont("Arabic", 10)
        words = text.split(",") if is_materials else text.split()
        lines = []
        current_line = []

        if is_materials:
            for i, word in enumerate(words):
                word = word.strip()
                if not current_line or len(current_line) < 2:
                    current_line.append(word)
                if len(current_line) == 2 or i == len(words) - 1:
                    lines.append(", ".join(current_line))
                    current_line = []
                if i < len(words) - 1 and len(current_line) == 0:
                    lines.append("")  # سطر فارغ بين الكتل
        else:
            current_width = 0
            for word in words:
                word_width = c.stringWidth(word + " ", "Arabic", 10)
                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
            if current_line:
                lines.append(" ".join(current_line))

        return lines

    try:
        font_path = "fonts/Amiri-Regular.ttf"
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"ملف الخط غير موجود: {font_path}")

        output_dir = os.path.dirname(filename)
        if output_dir and not os.access(output_dir, os.W_OK):
            raise PermissionError(f"لا توجد أذونات كتابة في المسار: {output_dir}")

        if not headers:
            raise ValueError("قائمة رؤوس الأعمدة فارغة")

        pdfmetrics.registerFont(TTFont('Arabic', font_path))

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        margin = 40
        top_margin = 70
        bottom_margin = 50
        y = height - top_margin

        line_height = 15  # ارتفاع النص
        cell_padding = 10   # هامش داخلي أعلى وأسفل
        col_width = (width - 2 * margin) / len(headers)

        c.setFont("Arabic", 12)
        school_name = reshape_arabic("Nebula School")
        current_date = reshape_arabic(datetime.today().strftime("%Y-%m-%d"))
        c.drawRightString(width - margin, height - 30, school_name)
        c.drawRightString(margin + 50, height - 30, current_date)

        c.setFont("Arabic", 14)
        c.drawCentredString(width / 2, height - 50, reshape_arabic(report_title))

        def draw_headers():
            nonlocal y
            c.setFont("Arabic", 10)
            c.setFillColor(colors.black)
            for i, header in enumerate(headers):
                x = margin + i * col_width
                c.rect(x, y - line_height - cell_padding, col_width, line_height + 2 * cell_padding, stroke=1, fill=1)
                c.setFillColor(colors.white)
                c.drawRightString(x + col_width - 5, y - line_height + 2, reshape_arabic(header))
                c.setFillColor(colors.black)
            y -= line_height + 2 * cell_padding

        draw_headers()

        for row in data:
            if not row:
                continue

            # 1. لفّ الأسطر في كل خلية وحساب أكبر عدد أسطر
            wrapped_rows = []
            max_lines = 1
            materials_index = headers.index("الطالب") if "الطالب" in headers else -1
            for i, cell in enumerate(row):
                cell_text = reshape_arabic(str(cell)) if cell else ""
                wrapped_text = wrap_text(cell_text, col_width - 10, c, is_materials=(i == materials_index))
                wrapped_rows.append(wrapped_text)
                max_lines = max(max_lines, len(wrapped_text))

            current_row_height = max_lines * line_height + 2 * cell_padding

            # 2. هل نحتاج لصفحة جديدة؟
            if y - current_row_height < bottom_margin:
                c.showPage()
                y = height - top_margin
                c.setFont("Arabic", 12)
                c.drawCentredString(width / 2, height - 50, reshape_arabic(report_title))
                draw_headers()

            # 3. رسم الخلايا والنص داخلها
            for i, wrapped_text in enumerate(wrapped_rows):
                x = margin + i * col_width
                c.rect(x, y - current_row_height, col_width, current_row_height, stroke=1, fill=0)

                # محاذاة النصوص عموديًا في منتصف الخلية مع هامش
                total_text_height = len(wrapped_text) * line_height
                vertical_offset = (current_row_height - total_text_height) / 2
                for j, line in enumerate(wrapped_text):
                    text_y = y - vertical_offset - (j * line_height)
                    c.drawRightString(x + col_width - 5, text_y, line)

            y -= current_row_height

        # المجموع إذا لزم
        if show_total:
            try:
                amount_index = -1
                for i, h in enumerate(headers):
                    if "المبلغ" in h or "المدفوع" in h or "السعر" in h:
                        amount_index = i
                        break

                if amount_index != -1:
                    total = 0.0
                    for row in data:
                        try:
                            value = str(row[amount_index]).replace("DA", "").replace(",", "").strip()
                            total += float(value)
                        except:
                            continue

                    formatted_total = "{:,.2f} DA".format(total)

                    if y < bottom_margin + 40:
                        c.showPage()
                        y = height - top_margin
                        draw_headers()

                    c.setFont("Arabic", 12)
                    c.drawRightString(width - margin, y - 15, reshape_arabic(f"المجموع: {formatted_total}"))
            except Exception as e:
                print(f"⚠️ خطأ أثناء حساب المجموع: {e}")

        c.save()
        print(f"✅ PDF تم حفظه بنجاح في: {filename}")

    except Exception as e:
        print(f"❌ خطأ أثناء التصدير إلى PDF: {e}")
        raise

    
def export_to_excel(filename, headers, data):
    try:
        wb = Workbook()
        ws = wb.active

        # إضافة رؤوس الأعمدة
        ws.append(headers)

        total = 0.0

        for row in data:
            ws.append(row)

            # استخراج المبلغ من العمود الأخير (مع إزالة DA والفواصل)
            try:
                value = row[-1].replace("DA", "").replace(",", "").strip()
                total += float(value)
            except:
                pass

        # ترك سطر فارغ ثم كتابة المجموع
        ws.append([])
        ws.append(["", "", f"💰 مجموع المدفوعات: {total:,.2f} DA"])

        wb.save(filename)
        print("✅ Excel تم حفظه بنجاح")
    except Exception as e:
        print("❌ خطأ أثناء إنشاء Excel:", e)