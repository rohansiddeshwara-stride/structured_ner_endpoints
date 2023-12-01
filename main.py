


from flask import Flask, request, jsonify
import fitz
import logging
import string
from flask_cors import CORS
import json

from Table import TableExtraction


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
                    _,extracted_tables = table_extractor.execute(doc_path,page_nos)
                    return jsonify(result)
                except:
                    return jsonify({"error": "Internal server error"}), 500
        else :
                try :
                    _,extracted_tables = table_extractor.execute(doc_path)
                    return jsonify(result)
                except:
                    return jsonify({"error": "Internal server error"}), 50


    
if __name__ == '__main__':
    
    
    # doc_path = "2018cafr.pdf"
    # page_nos =[2]
    # _,extracted_tables = table_extractor.execute(doc_path,page_nos)
    # result = extracted_tables

    
    # with open("output_json", "w") as json_file:
    #     json.dump(result, json_file)

    # print(result)
    

    app.run(host='0.0.0.0', port=5000)