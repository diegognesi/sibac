from datetime import date
from collections import OrderedDict
import locale
from sibaclib.errors import *

class FieldType:
    """
    This class is used to specify the data type for an ICCD field.

    Example:
    s = SimpleField()
    s.sid = "NCTN"
    s.field_type = FieldType.INT32
    """
    BOOLEAN = 1                  # True or False values
    BYTE = 2                     # 1 byte unsigned numeric values.
    INT16 = 3                    # 2 bytes signed values
    INT32 = 4                    # 4 bytes signed values
    INT64 = 5                    # 8 bytes signed values
    SINGLE = 6                   # 4 bytes floating point values
    DOUBLE = 7                   # 8 bytes floating point values
    DECIMAL = 10                 # currency values.
    DATE = 11                    # date (day of the year)
    TIME = 12                    # time (hour of the day)
    DATETIME = 13                # date & hour
    STRING = 14                  # text

class CatalogationLevel:
    """
    This class is used to specify the catalogation level at which the field is required
    for validating the document.

    Example:
    s.SimpleField()
    s.sid = "NCTN"
    s.level = CatalogationLevel.I
    """
    NONE = 0  #The field is not required
    I = 1     #The field is required at the level 'I' (see ICCD documentation)
    P = 2     #The field is required at the level 'P' (see ICCD documentation)
    C = 3     #The field is required at the level 'C' (see ICCD documentation)

class DictionaryType:
    """
    This class is used to specify if a field is bound to a dictionary,
    and if the dictionary id open or closed (see ICCD documentation).

    Example:
    s.SimpleField()
    s.sid = "NCTR"
    s.dictionary_type = DictionaryType.CLOSED
    """
    NONE = 0
    OPEN = 1
    CLOSED = 2

class MediaType:
    """
    This class is used to specify if the value of the field is bound
    to a multimedia file, and which file type.

    Example:
    s.SimpleField()
    s.sid = "FTAN"
    s.media_type = MediaType.PICTURE
    """
    NONE = 0
    PICTURE = 1
    SOUND = 2
    MOVIE = 3

class ElementBase(object):
    """
    This class defines the attributes shared bu every document and every element
    (paragraph, simple fields, structured fields and subfields) inside a document.
    
    The properties are:

    sid: The id of the element, i.e. "SI", "CD", "NCTN", "NCTR", "FTAN", etc.
    alt: A short sescription, i.e. "Scheda di Sito Archeologico", "Cordici", etc.
    compliant: True if the document or the document element is part of an ICCD standard.
    """
    def __init__(self):
        self.sid = ""
        self.alt = ""
        self.compliant = True

class DocumentType(ElementBase):
    """
    The instances class represent the structure of a document to manage.
    This class inherits from ElementBase and defines some new attributes.

    author:            The author of the SIBAC standard (not the author of
                       the corresponding ICCD standard, if present)
    version:           A string in the format "v.s.b.", i.e. "1.00".
    iccd_version:      The version of the ICCD standard corresponding to the
                       DocumentType instance, i.e. "3.00".
    creation_date:     A datetime.date instance. Default value is date.today().
    std_extension:     Extension of the files exported, if they contain only
                       compliant fields.
    ext_extension:     Extension of Extension of the files exported, if they contain
                       also non-compliant fields.
    paragraphs:        A list of Paragraph instances.
    """

    def __init__(self):
        super(DocumentType, self).__init__()
        self.author = ""
        self.version = ""
        self.iccd_version = ""
        self.creation_date = date.today()
        self.std_extension = ""
        self.ext_extension = ""
        self.public_by_default = False
        self.paragraphs = []
        self.all_elements = OrderedDict()
        self.simple_fields = OrderedDict()
        self.multimedia_fields = OrderedDict()
        self.required_fields = OrderedDict()
        self.required_elements_per_level = OrderedDict()

    @staticmethod
    def from_dict(values_dict):
        """
        This static method is used to create a DocumentType instance from a dictionary.


        Usage:

        si = {
            "sid": "SI",
            "alt": "Scheda di Sito Archeologico",
            "compliant": True,
            "author": "Diego Gnesi Bartolani",
            "creation_date": date(2012, 11, 2),
            "std_extension": "",
            "ext_extension": "cbc",
            "paragraphs": [
                {
                    "sid": "CD",
                    "alt": "Codici",
                    "level": CatalogationLevel.I,
                    "fields" : [
                        { "sid": "TSK", "alt": "Tipo scheda", "level": CatalogationLevel.I, "length": 4, "dictionary_type": DictionaryType.CLOSED },
                        { "sid": "LIR", "alt": "Livello ricerca", "level": CatalogationLevel.I, "length": 5, "dictionary_type": DictionaryType.CLOSED },
                        { "sid": "NCT", "alt": "Numero catalogo generale", "level": CatalogationLevel.I, "fields" : [
                            { "sid": "NCTR", "alt": "Codice regione", "level": CatalogationLevel.I, "length": 2, "fixed_length": True, "dictionary_type": DictionaryType.CLOSED },
                            { "sid": "NCTN", "alt": "Numero catalogo generale", "level": CatalogationLevel.I, "length": 8, "fixed_length": True, "field_type": FieldType.INT32 },
                            { "sid": "NCTS", "alt": "Suffisso numero catalogo generale", "level": CatalogationLevel.I, "length": 2, "validation_expression": "[a-zA-Z]+" }
                        ] },
                        { "sid": "ESC", "alt": "Ente schedatore", "level": CatalogationLevel.I, "length": 25, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "ESC", "alt": "Ente competente", "level": CatalogationLevel.I, "repeatable": True, "length": 25, "dictionary_type": DictionaryType.OPEN }
                    ]
                },
                { ...another paragraph...},
                { ...another paragraph...}
            ]
        }
        
        my_doct_ype = DocumentType.from_dict(si)
        """
        new_dt = DocumentType()
        new_dt.__dict__.update(values_dict)
        if hasattr(new_dt, "paragraphs"):
            old_paras = new_dt.paragraphs
            new_paras = []
            for p_dict in old_paras:
                p = Paragraph()
                p.__dict__.update(p_dict)
                new_fields = []
                # Convert every nested dictionary in the 'fields' list.
                for field_dict in p.fields:
                    new_fields.append(DocumentType._field_from_dict(field_dict))
                p.fields = new_fields
                new_paras.append(p)
            new_dt.paragraphs = new_paras
            DocumentType._add_attributes_to_elements(new_dt, "", None)
            for a_para in new_dt.paragraphs:
                DocumentType._add_can_be_repeated_attribute(a_para)
            new_dt.update_all_elements_attribute()
            new_dt.update_simple_fields_attribute()
        return new_dt

    @staticmethod
    def _field_from_dict(values_dict):
        """
        Recursive method that creates instances of simple fields or structured fiels
        from a dictionary. This method is private and called by from_dict() method.
        """
        if "fields" in values_dict:
            # The field to process is a structured field
            ret_val = StructuredField()
            ret_val.__dict__.update(values_dict)
            # Call itself for every subfield
            new_fields = []
            for subfield_dict in ret_val.fields:
                new_fields.append(DocumentType._field_from_dict(subfield_dict))
            ret_val.fields = new_fields
        else:
            # The field to process is a simple field
            ret_val = SimpleField()
            ret_val.__dict__.update(values_dict)
        return ret_val
    
    @staticmethod
    def _add_attributes_to_elements(element, current_path, parent_element):
        """
        This method adds the following attributes to each document element:
        - parent          -> Reference to 
        - complete_path   -> I.e. 'SI.CD.NCT.NCTN'
        - can_be_repeated -> True if the element is repeatable or is contained
                             in a repeatable element (directly or indirectly).
        """
        if isinstance(element, DocumentType):
            element.complete_path = element.sid
            for p in element.paragraphs:
                DocumentType._add_attributes_to_elements(p,
                                                         element.sid,
                                                         element)
        else:
            element.parent_element = parent_element
            current_path += "." + element.sid
            element.complete_path = current_path
            if hasattr(element, "fields"):
                for f in element.fields:
                    DocumentType._add_attributes_to_elements(f,
                                                             current_path,
                                                             element)

    @staticmethod
    def _add_can_be_repeated_attribute(element):
        """
        This method adds the can_be_repeated attribute to the specified element in
        a document type and to all the nested elements (if the exist). The attribute
        is True if the element is repeatable or is contained in a repeatable element
        (directly or indrectly).
        """
        if element.repeatable:
            element.can_be_repeated = True
        else:
            if hasattr(element, "parent_element") and hasattr(element.parent_element,
                                                               "parent_element"):
                element.can_be_repeated = element.parent_element.can_be_repeated
            else:
                element.can_be_repeated = False
        if hasattr(element, "fields"):
            for f in element.fields:
                DocumentType._add_can_be_repeated_attribute(f)

    def update_all_elements_attribute(self, current_element=None, req_dict=None):
        """
        Updates the "all_elements" attribute.
        """
        if current_element is None:
            self.all_elements.clear()
            self.required_elements_per_level.clear()
            req_dict = OrderedDict()
            c_levs = [getattr(CatalogationLevel, x) for x in dir(CatalogationLevel) if not x[0]=="_" and not x=="NONE"]
            c_levs.sort(reverse=True)
            for c_lev in c_levs:
                req_dict[c_lev] = []
            for p in self.paragraphs:
                self.update_all_elements_attribute(p, req_dict=req_dict)
            for k in req_dict:
                self.required_elements_per_level[k] = set(req_dict[k])
        else:
            self.all_elements[current_element.complete_path] = current_element
            if not current_element.level == CatalogationLevel.NONE:
                req_dict[current_element.level].append(current_element.complete_path)
            if hasattr(current_element, "fields"):
                for f in current_element.fields:
                    self.update_all_elements_attribute(f, req_dict=req_dict)

    def update_simple_fields_attribute(self):
        """
        Updates the simple_fields and the "multimedia_fields" attributes.
        """
        self.simple_fields.clear()
        self.multimedia_fields.clear()
        self.required_fields.clear()
        all_elem = self.all_elements
        for el_key in all_elem:
            curr_el = all_elem[el_key]
            if isinstance(curr_el, SimpleField):
                self.simple_fields[el_key] = curr_el
                if not curr_el.media_type == MediaType.NONE:
                    self.multimedia_fields[el_key] = curr_el
                if curr_el.required_for_saving:
                    self.required_fields[el_key] = curr_el

    def can_be_preceded(self, element_path, prev_element_path):
        """
        True if, in a document, the element specified in element_path
        can be immediately preceded by the element specified by
        the prev_element_path parameter.
        """
        keys = self.all_elements.keys()
        ind_el = keys.index(element_path)
        ind_prev = keys.index(prev_element_path)
        if ind_el > ind_prev:
            return True
        elif ind_el == ind_prev:
            # Same element. Verify that is repeatable and is not a
            # paragraph or a structured field, otherwise is empty.
            el = self.all_elements[element_path]
            if el.repeatable and not hasattr(el, "fields"):
                return True
            else:
                return False
        else: # ind_el < ind_prev
            # Test if there is a repetition.
            p_el = self.all_elements[element_path].parent_element
            # Split the previous element path and remove the first and the
            # last entries, respectively the document type sid and the field sid.
            splitted_prev = prev_element_path.split('.')[1:-1]
            test_passed = False
            while hasattr(p_el, "repeatable"):
                if p_el.repeatable and p_el.sid in splitted_prev:
                    test_passed = True
                    break
                p_el = p_el.parent_element
            return test_passed

    def get_complete_paths(self, element_path, error_if_ambiguous):
        """Returns a list of paths of one or more elements, knowing
        only the sid (i.e. "NCTN") or a partial path (i.e. "NCT.NCTN").
        """
        if "._" in element_path:
            pure_path = element_path[:element_path.index("._")]
        else:
            pure_path = element_path
        paths = [k for k in self.all_elements if k == pure_path or \
            k.endswith("." + pure_path)]
        if self.sid == pure_path:
            paths.append(self.sid)
        if error_if_ambiguous:
            paths_number = len(paths)
            if paths_number == 0:
                raise ElementNotDefined(pure_path)
            elif paths_number > 1:
                raise AmbiguousElementPath(pure_path)
        return paths

    def get_val_from_text(self, str_val, simple_field):
        """
        Converts a text to it's corresponding value, of the type
        specified by the field_type property of the simple_field
        element.
        
        Returns None if the cast fails.
        """
        ft = simple_field.field_type
        en = simple_field.english_notation
        try:
            if ft == FieldType.BOOLEAN:
                return_val = bool(str_val)
            elif ft == FieldType.BYTE:
                return_val = int(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.INT16:
                return_val = int(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.INT32:
                return_val = int(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.INT64:
                return_val = long(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.SINGLE:
                return_val = float(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.DOUBLE:
                return_val = float(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.DECIMAL:
                return_val = Decimal(self._replace_decimal_signs(str_val, en))
            elif ft == FieldType.DATE:
                if len(simple_field.datetime_format) > 0:
                    return_val = date.strptime(str_val, simple_field.datetime_format)
                else:
                    return_val = date.strptime(str_val)
            elif ft == FieldType.TIME:
                if len(simple_field.datetime_format) > 0:
                    return_val = time.strptime(str_val, simple_field.datetime_format)
                else:
                    return_val = time.strptime(str_val)
            elif ft == FieldType.DATETIME:
                if len(simple_field.datetime_format) > 0:
                    return_val = date.strptime(str_val, simple_field.datetime_format).date()
                else:
                    return_val = date.strptime(str_val).date()
            elif ft == FieldType.STRING:
                return_val = str_val
        except:
                return_val = None
        return return_val

    def _replace_decimal_signs(self, str_val, use_english_notation):
        """
        Returns a string that can be passed to int(), float() etc.

        This method examinate the local settings and the value
        of the use_english_notation parameter to create a string that
        should not raise exception during the conversion to a numeric
        format.
        """
        lc_using_point = locale.localeconv()["decimal_point"] == "."
        if use_english_notation:
            if lc_using_point:
                result = str_val
            else:
                result = str_val.replace(",", "_").replace(".", ",").replace("_", ".")
        else:
            if lc_using_point:
                result = str_val.replace(",", "_").replace(".", ",").replace("_", ".")
            else:
                result = str_val
        return result

class DocumentElementBase(ElementBase):
    """
    This class inherits from ElementBase and defines new attributes.
    All document element classes (Paragraph, SimpleField and StructuredField)
    inherit (dicrectly or indirectly) from this class.

    The attributes defined by this class are:

    repeatable:     True if the element can appear more than one time in a single
                    document. The default value is False.
    level:          The catalogation level at which the field is required for
                    validating the document.
                    Use the CatalogationLevel attributes to specify the values.
    parent_element: The parent element in the document type tree.
    """
    def __init__(self):
        super(DocumentElementBase, self).__init__()
        self.repeatable = False
        self.level = CatalogationLevel.NONE
        self.parent_element = None

class SimpleField(DocumentElementBase):
    """
    This class inherits from DocumentElementBase and defines new attributes.

    required_for_saving: True if the field must be present in order to save the current
                         document. Default value is False.
    field_type:          The data type stored in the field. Use the FieldType class
                         attributes to specify values. Default value is FieldType.STRING.
    validation_regex:    The regular expression used to validate the field. Default value
                         is "", that means no validation with regex.
    extraction_regex:    The regular expression used to extract field's value before
                         trying to convert to another data type. Default value is "", so
                         no extraction is performed, and the whole string will be
                         converted.
    english_notation:    True if the decimal separator is a point instead of a comma.
    length:              The maximum length of the string accepted for this field.
                         The default value is 0, so there is no limit to respect.
    fixed_length:        If True, the length attribute will specify the only accepted
                         length for the values of this field. The default value is False.
    dctionary_type:      A value from the DictionaryType attribute. This attribute
                         specifies if the field is bound to a dictionary, and if the
                         dictionary is open or closed (see ICCD docs).
    media_type:          A value from the MediaType attribute. This attribute
                         specifies if the field is bound to a multimedia file, and which
                         type of multimedia file is.
    unique:              True if the values of this field must be unique for all
                         documents. If the field is repeatable, then the sequence of the
                         values must be unique. Default value is False.
    uniqueness_group:    To test the uniqueness constraint for a combination of one or 
                         more fields, set unique=True for all the fields and set the
                         uniqueness_group to the same integer value. Default is 0 (no
                         group).
    """
    def __init__(self):
        super(SimpleField, self).__init__()
        self.required_for_saving = False
        self.field_type = FieldType.STRING
        self.validation_regex = ""
        self.extraction_regex = ""
        self.datetime_format = ""
        self.english_notation = ""
        self.length = 0
        self.fixed_length = False
        self.dictionary_type = DictionaryType.NONE
        self.media_type = MediaType.NONE
        self.unique = False
        self.uniqueness_group = 0

class FieldsContainerBase(DocumentElementBase):
    """
    This class inherits from DocumentElementBase and defines the attribute fields.
    This attribute points to a list of SimpleField or StructuredField instances.
    The classes Paragraph and StructuredField inherit from this class.
    """
    def __init__(self):
        super(FieldsContainerBase, self).__init__()
        self.fields = []

class StructuredField(FieldsContainerBase):
    """
    This class inherits from FieldsContainerBase and represents a structured field
    (see ICCD docs).
    """
    def __init__(self):
        super(StructuredField, self).__init__()

class Paragraph(FieldsContainerBase):
    """
    This class inherits from FieldsContainerBase and represents a paragraph
    (see ICCD docs).
    """
    def __init__(self):
        super(Paragraph, self).__init__()


