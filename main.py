


from flask import Flask, request, jsonify
import fitz
import logging
import string
from flask_cors import CORS
import json

from Table import TableExtraction,manual_extractor


table_extractor = TableExtraction()



app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})



@app.route('/ExtractTables', methods=['POST'])
def auto_extract():
    data = request.get_json()

    if 'pdf_path' not in data :
        return jsonify({"error": "Missing pdf"}), 400

    else :
        pdf_path = data['pdf_path']

        if 'page_nos' in data :
            page_nos = data['page_nos']

            if not isinstance(page_nos, list) :
                return jsonify({"error": "page_nos should be a list of integer."}), 400

            else:
                try :
                    extracted_tables_without,extracted_tables_with_cell_mapping = table_extractor.execute(doc_path,page_nos)
                    return jsonify(result)
                except:
                    return jsonify({"error": "Internal server error"}), 500
        else :
                try :
                    extracted_tables_without,extracted_tables_with_cell_mapping = table_extractor.execute(doc_path)
                    return jsonify(result)
                except:
                    return jsonify({"error": "Internal server error"}), 500


@app.route('/manual_extractor', methods=['POST'])
def api_process_pdf():
    data = request.get_json()

    if 'pdf_path' not in data or 'page_no' not in data or 'bbox' not in data:
        return jsonify({"error": "Missing one or more required fields."}), 400

    pdf_path = data['pdf_path']
    page_no = data['page_no']
    bbox = data['bbox']

    if not isinstance(page_no, int) or page_no < 0:
        return jsonify({"error": "page_no should be a positive integer."}), 400

    if not isinstance(bbox, list) or len(bbox) != 4:
        return jsonify({"error": "bbox should be a list of 4 integers."}), 400
    logging.info("Activating manual extraction")
    result = manual_extractor(pdf_path, page_no, bbox)
    logging.info("Manual extraction successful")
    return jsonify(result)
    
if __name__ == '__main__':
    
    
    # doc_path = "2018cafr.pdf"
    # page_nos =[2]
    # _,extracted_tables = table_extractor.execute(doc_path,page_nos)
    # result = extracted_tables

    
    # with open("output_json", "w") as json_file:
    #     json.dump(result, json_file)

    # print(result)
    

    app.run(host='0.0.0.0', port=5000)