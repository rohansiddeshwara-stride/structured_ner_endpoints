import fitz
import cv2
import os
import numpy as np
 

from .TableDetectors import DetectTable, YoloTableDetector, LoadYolo
from .TableExtractors import ExtractDataBordered, Borderless_Table_digital
from .TableExtractors import OcrToTableTool, ExtractDataBorderedScanned

from .utils import TableLinesRemover






def return_fianl_json(tables):
  
  fianl_json = {"tables" : []}
  if tables != [None]:
    fianl_json["tables"]=tables
    # for i in range(len(tables)):

    #   table_data = tables[i]
    #   table_label = f"Table {i+1}"
    #   json = {"data" : table_data, "datapoint" : table_label}

    #   fianl_json["tables"].append(json)

  return fianl_json

def get_table(doc_path,page_no,bbox):
  doc = fitz.open(doc_path)
  zoom_x = 3.0
  zoom_y = 3.0
  table_json={}
  if page_no < len(doc):
    page = doc[page_no]
    # mat = fitz.Matrix(zoom_x, zoom_y)
    # pix = page.get_pixmap(matrix=mat)
    # pix.save("page.png")
    all_text = page.get_text("words")
    if len(all_text)>0:
      if len(extract_words(all_text,bbox)) > 0:
        gen_table = Borderless_Table_digital(bbox, page_no, doc_path)
        old_response,table_json = gen_table.execute(page_no,1)
        return old_response,table_json
      else :
        return []
        
    else:
      return []
    # image=cv2.imread("page.png")

    # cv2.rectangle(image, (round(bbox[0]*zoom_x), round(bbox[1]*zoom_y)),  (round(bbox[2]*zoom_x), round(bbox[3]*zoom_y)), (20,200,0), 2)
    # for d in table_json["data"]:
    #   for cell in d['row_value']:
    #     c=cell
    #     cv2.rectangle(image, (round(c["bbox"][0]*zoom_x), round(c["bbox"][1]*zoom_y)),  (round(c["bbox"][2]*zoom_x), round(c["bbox"][3]*zoom_y)), (0,0,255), 2)
    # cv2.imwrite("page.png",image)
  else: 
    return []

def manual_extractor(pdf_path,page_no,bbox):
  try:
    result = get_table(pdf_path,int(page_no),list(bbox))
    print(results)
    json = return_fianl_json(results)
    return json
  except Exception as e:
    print(e)


class TableExtraction():
  def __init__(self):
    self.MODEL = LoadYolo()
    self.table_detector = DetectTable()

  def execute(self,doc_path,page_nos=None):
    self.doc_path = doc_path
    self.document = fitz.open(self.doc_path)

    if page_nos :
      for page_no in page_nos:

        if page_no > -1 and page_no < len(self.document):

            self.tables= {}
            self.extracted_table_list=[]
            self.extrated_table_list_with_cell_bbox =[]  

            pages_dict = self.get_pdf_searchable_pages(self.doc_path)

            # pages_dict['digital']=list(range(45,51))
            t =page_no -1
            if t in pages_dict['digital']:

                zoom_x = 1.0
                zoom_y = 1.0
                page = self.document[page_no]
                mat = fitz.Matrix(zoom_x, zoom_y)
                pix = page.get_pixmap(matrix=mat)
                pix.save("page.png")
                table_list,_ = self.table_detector.extract_table_bbox("page.png")
                # print(table_list)
                if len(table_list)< 1:
                    table_list= YoloTableDetector("page.png",self.MODEL)

                if len(table_list)>0:
                  page_image=cv2.imread('page.png')
                  for table_no,bbox in enumerate(table_list):
                    cropped_image=self.extract_bounding_box(bbox,page_image)

                    if self.is_bodered(cropped_image):
                        extract_data = ExtractDataBordered(page_image, page_no,bbox,table_no,self.doc_path)
                        data,table_with_cell_mapping = extract_data.execute(page_no,table_no)
                        if data["data"] != [[" "]]:
                          self.extracted_table_list.append(data)

                          json = {"data" : table_with_cell_mapping, "datapoint" : f"Table {len(self.extrated_table_list_with_cell_bbox) + 1}"}
                          self.extrated_table_list_with_cell_bbox.append(table_with_cell_mapping)

                    else :
                        table_gen = Borderless_Table_digital(bbox,page_no,self.doc_path)
                        data,table_with_cell_mapping= table_gen.execute(page_no,table_no)
                        if data["data"] != [[" "]]:
                          self.extracted_table_list.append(data)

                          json = {"data" : table_with_cell_mapping, "datapoint" : f"Table {len(self.extrated_table_list_with_cell_bbox) + 1}"}
                          self.extrated_table_list_with_cell_bbox.append(table_with_cell_mapping)

            # if page_no in pages_dict['scanned']:
            #     page_no-=1
            #     zoom_x = 2.0
            #     zoom_y = 2.0
            #     page = self.document[page_no]
            #     mat = fitz.Matrix(zoom_x, zoom_y)
            #     pix = page.get_pixmap(matrix=mat)
            #     pix.save("page.png")
            #     table_list,_ = self.table_detector.extract_table_bbox("page.png")
            #     # print(table_list)
            #     if len(table_list)>0:
            #       page_image=cv2.imread('page.png')
            #       for table_no,bbox in enumerate(table_list):
            #         cropped_image=self.extract_bounding_box(bbox,page_image)

            #         if self.is_bodered(cropped_image):
            #             extract_data = ExtractDataBorderedScanned(page_image, page_no,bbox,table_no,self.doc_path)
            #             data= extract_data.execute(page_no,table_no)
            #             if data["data"] != [[" "]]:
            #               print("3", data)
            #               self.extracted_table_list.append(data)

            #         else :
            #           lines_remover = TableLinesRemover(cropped_image)
            #           image_without_lines = lines_remover.execute()
            #           ocr_tool = OcrToTableTool(image_without_lines,cropped_image,page_no,table_no,bbox)
            #           data= ocr_tool.execute()
            #           if data["data"] != [[" "]]:
            #             print("4", data)
            #             self.extracted_table_list.append(data)
        else  :
          print(f"page_no {page_no}. not in document")
        
      return self.extracted_table_list,return_fianl_json(self.extrated_table_list_with_cell_bbox)

    else :
      pages_dict = self.get_pdf_searchable_pages(self.doc_path)
      self.tables= {}

      self.extracted_table_list=[]

      self.extrated_table_list_with_bbox =[]
      # pages_dict['digital']=list(range(45,51))
      t =page_no -1
      for t in pages_dict['digital']:

          
          zoom_x = 1.0
          zoom_y = 1.0
          page = self.document[page_no]
          mat = fitz.Matrix(zoom_x, zoom_y)
          pix = page.get_pixmap(matrix=mat)
          pix.save("page.png")
          table_list,_ = self.table_detector.extract_table_bbox("page.png")
          # print(table_list)
          if len(table_list)< 1:
              table_list= YoloTableDetector("page.png",self.MODEL)
          if len(table_list)>0:
            page_image=cv2.imread('page.png')
            for table_no,bbox in enumerate(table_list):
              cropped_image=self.extract_bounding_box(bbox,page_image)

              if self.is_bodered(cropped_image):
                  extract_data = ExtractDataBordered(page_image, page_no,bbox,table_no,self.doc_path)
                  data,table_with_cell_mapping = extract_data.execute(page_no,table_no)
                  if data["data"] != [[" "]]:
                    self.extracted_table_list.append(data)

                    json = {"data" : table_with_cell_mapping, "datapoint" : f"Table {len(self.extrated_table_list_with_bbox) + 1}"}
                    self.extrated_table_list_with_cell_bbox.append(table_with_cell_mapping)

              else :
                  table_gen = Borderless_Table_digital(bbox,page_no,self.doc_path)
                  data,table_with_cell_mapping= table_gen.execute(page_no,table_no)
                  if data["data"] != [[" "]]:
                    self.extracted_table_list.append(data)

                    json = {"data" : table_with_cell_mapping, "datapoint" : f"Table {len(self.extrated_table_list_with_bbox) + 1}"}
                    self.extrated_table_list_with_cell_bbox.append(table_with_cell_mapping)


      # for page_no in pages_dict['scanned']:
      #     page_no-=1
      #     zoom_x = 2.0
      #     zoom_y = 2.0
      #     page = self.document[page_no]
      #     mat = fitz.Matrix(zoom_x, zoom_y)
      #     pix = page.get_pixmap(matrix=mat)
      #     pix.save("page.png")
      #     table_list,_ = self.table_detector.extract_table_bbox("page.png")
      #     # print(table_list)
      #     if len(table_list)>0:
      #       page_image=cv2.imread('page.png')
      #       for table_no,bbox in enumerate(table_list):
      #         cropped_image=self.extract_bounding_box(bbox,page_image)

      #         if self.is_bodered(cropped_image):
      #             extract_data = ExtractDataBorderedScanned(page_image, page_no,bbox,table_no,self.doc_path)
      #             data= extract_data.execute(page_no,table_no)
      #             if data["data"] != [[" "]]:
      #               print("3", data)
      #               self.extracted_table_list.append(data)

      #         else :
      #           lines_remover = TableLinesRemover(cropped_image)
      #           image_without_lines = lines_remover.execute()
      #           ocr_tool = OcrToTableTool(image_without_lines,cropped_image,page_no,table_no,bbox)
      #           data= ocr_tool.execute()
      #           if data["data"] != [[" "]]:
      #             print("4", data)
      #             self.extracted_table_list.append(data)




      return self.extracted_table_list,return_fianl_json(self.extrated_table_list_with_cell_bbox)

  def extract_bounding_box(self,bbox,image):
      x1, y1, x2, y2 = bbox
      height=abs(y2-y1)
      width=abs(x2-x1)
      extracted_image = image[y1:y1+height, x1:x1+width]
      # cv2_imshow(extracted_image)
      return extracted_image

  def get_pdf_searchable_pages(self,fname):
    # pip install pdfminer
    from pdfminer.pdfpage import PDFPage
    searchable_pages = []
    non_searchable_pages = []
    page_num = 0
    with open(fname, 'rb') as infile:

        for page in PDFPage.get_pages(infile):
            page_num += 1
            if 'Font' in page.resources.keys():
                searchable_pages.append(page_num)
            else:
                non_searchable_pages.append(page_num)
    if page_num > 0:
        return {'digital':searchable_pages,"scanned":non_searchable_pages}
    else:
        print(f"Not a valid document")

  def extract_table_digital_borderless(self,page_no,bbox_list):
    doc_path=self.doc_path

    for i,j in enumerate(bbox_list):
      table_gen = GenerateTable(j,page_no,doc_path)
      table = table_gen.execute(page_no,i)

  def is_bodered(self,image):

    # cv2_imshow(image)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresholded_image = cv2.threshold(grey, 250, 255, cv2.THRESH_BINARY)[1]
    inverted_image = cv2.bitwise_not(thresholded_image)

    hor = np.array([[1,1,1,1,1,1,1]])
    vertical_lines_eroded_image = cv2.erode(inverted_image, hor, iterations=15)
    vertical_lines_eroded_image = cv2.dilate(vertical_lines_eroded_image, hor, iterations=15)
    # cv2_imshow(vertical_lines_eroded_image)
    r_contours, hierarchy = cv2.findContours(vertical_lines_eroded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    ver = np.array([[1],
                [1],
                [1],
                [1],
                [1],
                [1],
                [1]])
    horizontal_lines_eroded_image = cv2.erode(inverted_image, ver, iterations=15)
    horizontal_lines_eroded_image = cv2.dilate(horizontal_lines_eroded_image, ver, iterations=15)
    c_contours, hierarchy = cv2.findContours(horizontal_lines_eroded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # cv2_imshow(horizontal_lines_eroded_image)

    combined_image = cv2.add(vertical_lines_eroded_image, horizontal_lines_eroded_image)
    # cv2_imshow(combined_image)

    rows, columns = self.get_rows_and_columns(r_contours, c_contours)
    # print(rows, columns)
    if len(rows) > 2 and len(columns) > 2:
    # if (len(rows) <= 2 and len(columns) >2) or (len(rows) > 2 and len(columns) <= 2):
      if self.intersects(rows, columns):
        return True
    return False

  def intersects(self,rows, columns):
    i = 0
    # print(len(rows), len(columns))
    for xr0, yr0, xr1, yr1 in rows:
      for xc0, yc0, xc1, yc1 in columns:
        # print(xr0, yr0, xr1, yr1, xc0, yc0, xc1, yc1)
        if xr0 <= xc0 and yr0 >= yc0 and xr1 >= xc1 and yr1 <= yc1:
          i+=1
    cal_i = (len(rows) * len(columns))*2/3
    # print(i, cal_i)
    return True if i >= cal_i else False

  def get_rows_and_columns(self,r_c, c_c):
    row_range = []
    for line in r_c:
      sorted_data = sorted(line, key=lambda x: x[0][0])
      row_range.append([sorted_data[0][0][0], sorted_data[0][0][1], sorted_data[-1][0][0], sorted_data[-1][0][1]])
    row_range.sort()

    column_range = []
    for line in c_c:
      sorted_data = sorted(line, key=lambda x: x[0][1])
      column_range.append([sorted_data[0][0][0], sorted_data[0][0][1], sorted_data[-1][0][0], sorted_data[-1][0][1]])
    column_range.sort()

    return row_range, column_range

  def read_pdf(self,is_scanned=False):



    zoom_x = 1.0 if not is_scanned else 2.0
    zoom_y = 1.0 if not is_scanned else 2.0

    if is_scanned == False or is_scanned == True :
      no_of_pages = len(self.document)
      for page_no in range(no_of_pages):
        page = self.document[page_no]
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        pix.save("page.png")

        table_list = table_detector.execute("page.png","tables_cropped",page_no)
        os.remove("page.png")
        if len(table_list)>=1:
          self.tables[page_no] = table_list


    elif isinstance(is_scanned, (list)):
      digital_list = is_scanned[0]
      scanned_list = is_scanned[1]
      for page_no in digital_list:
        zoom_x = 1.0
        zoom_y = 1.0
        page = self.document[page_no]
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        pix.save("page.png")
        table_list = table_detector.execute("page.png","tables_cropped_digital",page_no)
        if len(table_list)>=1:
          self.tables[page_no] = table_list
      for page_no in scanned_list:
        zoom_x = 2.0
        zoom_y = 2.0
        page = self.document[page_no]
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        pix.save("page.png")
        table_list = self.table_detector.execute("page.png","tables_cropped_scanned",page_no)
        if len(table_list)>=1:
          self.tables[page_no] = table_list

    return self.tables

