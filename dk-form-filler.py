from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import pink, skyblue

# DK form, table bot left corner x=28pt y=77, row height = 16.5
# bottom left corner of quantity: x=40.5

inch = 72 # number of points in an inch
x_len = 8.5
y_len = 11
grid_size = 0.125

x_len_points = 8.5 * inch
y_len_points = 11 * inch

grid_x = np.arange(0, x_len_points, 10)
grid_y = np.arange(0, y_len_points, 10)

grid_x_list = grid_x.tolist()
grid_y_list = grid_y.tolist()
#print(grid_y_list)

grid_x_minor = np.arange(0, x_len_points, 2)
grid_x_minor  = np.delete(grid_x_minor, np.arange(0, grid_x_minor.size, 10)).tolist()

grid_y_minor = np.arange(0, y_len_points, 2)
grid_y_minor  = np.delete(grid_y_minor, np.arange(0, grid_y_minor.size, 10)).tolist()

# creates ann overlay using Reportlab
# instantiate byte object buffer
buffer = io.BytesIO()
overlay = canvas.Canvas(buffer, pagesize=letter)
overlay.setLineWidth(0.125)
overlay.setStrokeColor(skyblue)
overlay.grid(grid_x_minor, grid_y_minor)
overlay.setStrokeColor(pink)
overlay.grid(grid_x_list, grid_y_list)
overlay.setFont("Helvetica", 5)

for y in grid_y_list:
    overlay.drawString(0, (y-2), str(y))
    overlay.drawCentredString(545, (y-2), str(y))

for x in grid_x_list:
    overlay.drawString((x-3), 0, str(int(x)))
    overlay.drawString((x-3), 715, str(int(x)))

overlay.save()

# move to the beginning of the ByteIO buffer
buffer.seek(0)
# create pyPDF object from byte stream
overlay_pdf_reader = PdfFileReader(buffer)

# instantiate reader object from order form, instantiate pyPDF writer object
existing_pdf_reader = PdfFileReader(open("order-form.pdf", "rb"))
output_pdf_writer = PdfFileWriter()

# get original and overlay PDF pages
original_page = existing_pdf_reader.getPage(0)
overlay_page = overlay_pdf_reader.getPage(0)

# merge overlay page on original PDF and add to output PDF writer
original_page.mergePage(overlay_page)
output_pdf_writer.addPage(original_page)

# write output writer object to actual file
output_stream = open("dimensioning_output_small.pdf", "wb")
output_pdf_writer.write(output_stream)
output_stream.close()
