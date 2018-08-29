""" Adding docstring so pylint doesn't yells
    Another line. """

import io
import numpy as np
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import pink, skyblue

def find(input_key, dictionary):
    """ Handy function to find key at the end of the rainbow
        Thanks douglasmiranda/gist:5127251 ! """
    for key, val in dictionary.iteritems():
        if key == input_key:
            yield val
        elif isinstance(val, dict):
            for result in find(input_key, val):
                yield result
        elif isinstance(val, list):
            for item in val:
                for result in find(input_key, item):
                    yield result

class FormFiller(object):
    """ Form Filler Class"""

    def __init__(self, orig_pdf_name, pagesize=letter):
        # init stream and canvas
        self.io_buffer = io.BytesIO()
        self.overlay = canvas.Canvas(self.io_buffer, pagesize)
        self.width, self.length = pagesize
        self.default_font_size = 12
        self.default_font = "Helvetica"

        #init some defualt canvas parameters
        self.overlay.setLineWidth(0.125)

        self.orig_pdf_name = orig_pdf_name
        self.fields = {}
        self.check_marks = {}

    def fill_field(self, field, value, font=None, font_size=None,
                   justification="Left"):
        """ Method to fill field with value, stays in bounding box """
        if font is None:
            font = self.default_font
        if font_size is None:
            font_size = self.default_font_size

        _x1 = float(field['bounding_box']['x1'])
        _x2 = float(field['bounding_box']['x2'])
        _y1 = float(field['bounding_box']['y1'])
        _y2 = float(field['bounding_box']['y2'])

        # field will be a 2 item dict, value and draw_bounding_boxes
        box_width = _x2 - _x1
        box_center = (_x2 + _x1) / 2
        box_height = _y2 - _y1

        # reduce font size height first to fit string within box
        while font_size > box_height:
            font_size -= 0.5

        # reduce font size further to fit within length
        string_width = self.overlay.stringWidth(value, font, font_size)
        while string_width > box_width:
            font_size -= 0.5
            string_width = self.overlay.stringWidth(value, font, font_size)

        self.overlay.setFont(font, font_size)

        if justification == "Center":
            text_line = ((_y1 + _y2) / 2) - (font_size / 2)
            self.overlay.drawCentredString(box_center, text_line, value)
        elif justification == "Left":
            self.overlay.drawString(_x1, _y1, value)


    def write_out(self, out_pdf_name):
        """ Method to write out PDF overlay out on top of orig PDF """
        # move to the beginning of the ByteIO buffer
        self.io_buffer.seek(0)
        # create pyPDF object from byte stream
        overlay_pdf_reader = PdfFileReader(self.io_buffer)
        # instantiate reader object from order form, instantiate pyPDF writer object
        existing_pdf_reader = PdfFileReader(open(self.orig_pdf_name, "rb"))
        output_pdf_writer = PdfFileWriter()
        # get original and overlay PDF pages
        original_page = existing_pdf_reader.getPage(0)
        overlay_page = overlay_pdf_reader.getPage(0)
        # merge overlay page on original PDF and add to output PDF writer
        original_page.mergePage(overlay_page)
        output_pdf_writer.addPage(original_page)
        # write output writer object to actual file
        with open(out_pdf_name, "wb") as output_stream:
            output_pdf_writer.write(output_stream)

    def draw_bounding_boxes(self, box_dict_list):
        """ Function to draw list of dict bounding boxes
         box_dict keys: x1, y1, x2, y2 """
        self.overlay.setStrokeColor(pink)
        for box_dict in box_dict_list:
            if None in box_dict.values():
                #TODO: log message about incomplete values
                continue
            else:
                try:
                    x1_x2 = [box_dict["x1"], box_dict["x2"]]
                    y1_y2 = [box_dict["y1"], box_dict["y2"]]
                    self.overlay.grid(x1_x2, y1_y2)
                    #TODO: Method to draw to canvas
                except KeyError, ex:
                    print 'Key Error "%s"' % str(ex)
        self.overlay.save()

    def draw_check_marks(self, check_mark_dict_list):
        """ Function to draw list of dict check mark points
         check_mark_dict keys: x1, y1 """
        for check_mark_dict in check_mark_dict_list:
            if None in check_mark_dict.values():
                #TODO: log message about incomplete values
                continue
            else:
                try:
                    _x1 = check_mark_dict["x1"]
                    _y1 = check_mark_dict["y1"]
                    self.overlay.drawCentredString(_x1, _y1, u'\u2713')
                except KeyError, ex:
                    print 'Key Error "%s"' % str(ex)
        self.overlay.save()

    def draw_grid(self, major_spacing=10, minor_spacing=2, major_color=pink,
                  minor_color=skyblue):
        """ Function to draw square grid overlay
        Useful for mapping out original form """
        #width, length = self.pagesize
        grid_x_minor = np.arange(0, self.width, minor_spacing)
        grid_x_minor = np.delete(grid_x_minor,
                                 np.arange(0, grid_x_minor.size, major_spacing))
        grid_x_minor = grid_x_minor.tolist()

        grid_y_minor = np.arange(0, self.length, minor_spacing)
        grid_y_minor = np.delete(grid_y_minor,
                                 np.arange(0, grid_y_minor.size, major_spacing))
        grid_y_minor = grid_y_minor.tolist()

        grid_x_major = np.arange(0, self.width, major_spacing).tolist()
        grid_y_major = np.arange(0, self.length, major_spacing).tolist()

        self.overlay.setStrokeColor(minor_color)
        self.overlay.grid(grid_x_minor, grid_y_minor)
        self.overlay.setStrokeColor(major_color)
        self.overlay.grid(grid_x_major, grid_y_major)
        self.overlay.save()

if __name__ == "__main__":
    #TEST_FORM_GRID = FormFiller("order-form.pdf")
    #TEST_FORM_GRID.draw_grid()
    #TEST_FORM_GRID.write_out("test_grid_out.pdf")
    TEST_FORM_BOXES = FormFiller("order-form.pdf")
    TEST_STRING = "TEST_TEST_TEST_TEST_TEST_TEST"
    import json
    with open("item-table.json", "r") as input_file:
        TABLE_ROW_LIST = json.load(input_file)["table"]
        DICT_LIST = []
        for row in TABLE_ROW_LIST:
            for _key, entry in row.iteritems():
                TEST_FORM_BOXES.fill_field(entry, TEST_STRING,
                                           justification="Center")
                DICT_LIST.append(entry["bounding_box"])
        TEST_FORM_BOXES.draw_bounding_boxes(DICT_LIST)
        TEST_FORM_BOXES.write_out("test_fill_boxes_out.pdf")

    #with open("field-info.json", "r") as in_file:
    #    FIELD_DICT = json.load(in_file)
    #    for KEY, VAL in FIELD_DICT.iteritems():

        #output should be list of dicts where keys are coordinates
