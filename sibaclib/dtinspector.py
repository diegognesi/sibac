import glob
import os.path
import imp
from collections import deque
from sibaclib.documenttypes import *

class DocumentTypesInspector:
    def __init__(self, document_types_folder):
        self.doc_types = {}
        search_path = os.path.join(document_types_folder, "*.py")
        files = glob.glob(search_path)
        for a_file in files:
            f_name = os.path.basename(a_file)
            if not f_name.startswith("__"):
                mod_name = os.path.splitext(f_name)
                #imp_mod = imp.load_source(f_name, a_file)
                imp_mod = imp.load_source('', a_file)
                if hasattr(imp_mod, "document_type_def"):
                    dt = DocumentType.from_dict(imp_mod.document_type_def)
                    self.doc_types[dt.sid] = dt

    def get_element(self, element_path):
        # Returns a field, paragraph or document type definition.
        #
        # Usage:
        # inspector_instance.get_element("SI.CD.NCT.NCTN")
        i = element_path.find('.')
        if i < 0:
            # element_path does not contain dots: it must be a DocumentType sid.
            return self.doc_types[element_path]
        else:
            dt_sid = element_path[:i]
            return self.doc_types[dt_sid].all_elements[element_path]

    def get_doc_type_sid(self, element_path):
        i = element_path.find('.')
        if i < 0:
            # element_path does not contain dots: it must be a DocumentType sid.
            return element_path
        else:
            return element_path[:i]
