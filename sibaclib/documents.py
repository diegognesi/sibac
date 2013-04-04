# -*- coding: utf-8 -*-
import locale, json, re
from collections import deque
from datetime import date, time, datetime
from decimal import Decimal
from sibaclib.documenttypes import CatalogationLevel, FieldType, DictionaryType
from sibaclib.errors import *
from sibaclib.search import *

class Document:
    """
    This class represents a single SIBAC document.

    This class uses the method json_decode to load the document from a json
    string, and the json_encode to produce a valid json string.
    """
    def __init__(self, dt_sid = "", doc_id = None, package_name = "", author_id = None,
                 author_name = None, creation_date = None, last_edit_date = None,
                 last_editor_id = None, last_editor_name = None,
                 cat_level=CatalogationLevel.NONE,
                 json_str = "", provider = None, media_files=None):
        self.dt_sid = dt_sid
        self.doc_id = doc_id
        self.package_name = package_name
        self.author_id = author_id
        self.author_name = author_name
        self.creation_date = creation_date
        self.last_edit_date = last_edit_date
        self.last_editor_id = last_editor_id
        self.last_editor_name = last_editor_name
        self.catalogation_level = cat_level
        self.provider = provider
        # the media_files attribute is a list of lists.
        # Each list has the following structure:
        # [simple_field_path, field_text, file_name_with_extension]
        if media_files is None:
            self.media_files = []
        else:
            self.media_files = []
        if not len(json_str) == 0:
            self.json_decode(json_str)

    def json_decode(self, json_str, content_only=True):
        """Decodes the document from a json string."""
        loaded = json.loads(json_str)
        if content_only:
            self.content = loaded
        else:
            self.dt_sid = loaded["dt_sid"]
            self.doc_id = loaded["doc_id"]
            self.package_name = loaded["package_name"]
            self.author = loaded["author"]
            self.creation_date = loaded["creation_date"]
            self.last_edit_date = loaded["last_edit_date"]
            self.last_editor_id = loaded["last_editor_id"]
            self.last_editor_name = loaded["last_editor_name"]
            self.catalogation_level = loaded["catalogation_level"]
            self.media_files = loaded["media_files"]
            self.content = loaded["content"]

    def json_encode(self, compact_encoding=True, content_only=True):
        """Encodes the document into a json string."""
        if content_only:
            dc = self.content
        else:
            dc = {}
            dc["dt_sid"] = self.dt_sid
            dc["doc_id"] = self.doc_id
            dc["package_name"] = self.package_name
            dc["author"] = self.author
            dc["creation_date"] = self.creation_date
            dc["last_edit_date"] = self.last_edit_date
            dc["last_editor_id"] = self.last_editor_id
            dc["last_editor_name"] = self.last_editor_name
            dc["catalogation_level"] = self.catalogation_level
            dc["media_files"] = self.media_files
            dc["content"] = self.content
        if compact_encoding:
            return json.dumps(dc, separators=(",",":"))
        else:
            return json.dumps(dc)

    def get_contents(self, element_path):
        """
        Returns a list of all values for the specified field.
        
        Example (supposing field_type is FieldType.INT32):
        
        my_document.get_contents("PATH.TO.A.SIMPLE.FIELD")
        ["00000001", "00000002", "bababa"]

        If the element does not exist, the returned value is None.
        """
        doc_type = self.provider.inspector.doc_types[self.dt_sid]
        complete_path = doc_type.get_complete_paths(element_path, error_if_ambiguous=True)[0]
        try:
            path_list = complete_path.split(".")
            if len(path_list) == 1 and path_list[0] == self.dt_sid:
                return self.content
            else:
                q_path = deque(path_list)
                # remove the root element, corresponding to the document type name.
                q_path.popleft()
                # The next line is necessary to create a consistent algorythm.
                curr_container = [self.content]
                while len(q_path) > 0:
                    curr_sid = q_path.popleft()
                    # Put nested contents with the specified sid in a new list.
                    new_container = [g[1] for l in curr_container for g in l if g[0] == curr_sid]
                    curr_container = new_container
            return curr_container
        except:
            return None

    def get_contents_as_values(self, field_path):
        """
        Returns a list of all values for the specified field, converted to the
        type specified by the field_type attribute of the corresponding SimpleField
        
        Example (supposing field_type is FieldType.INT32):
        my_document.get_contents("PATH.TO.A.SIMPLE.FIELD")
        ["00000001", "00000002", "bababa"]
        
        my_document.get_contents_as_values("PATH.TO.A.SIMPLE.FIELD")
        [1, 2]
        """
        string_contents = self.get_contents(field_path)
        doc_type = self.provider.inspector.doc_types[self.dt_sid]
        sf = self.provider.inspector.get_element(field_path)
        extr_rgx = sf.extraction_regex
        if len(extr_rgx) > 0:
            matches = [re.search(extr_rgx, x) for x in string_contents]
            values = [doc_type.get_val_from_text(m.group(0), sf) for m in matches if not m is None]
        else:
            values = [doc_type.get_val_from_text(x, sf) for x in string_contents]
        return [v for v in values if not v is None]

    def __iter__(self):
        return self._flatten(self.content, self.dt_sid)

    def _flatten(self, l, path):
        """
        Returns a generator that can be used to iterate over a flattened version
        of document's contents.
        """
        original_path = path
        for el in l:
            path = original_path + '.' + el[0]
            if not isinstance(el[1], basestring):
                yield [path, el[0], el[1]]
                for sub in self._flatten(el[1], path):
                    yield sub
            else:
                # el is a [sid, 'value'] list.
                yield [path, el[0], el[1]]

    def test_field_content(self, str_value, field_path, dictionaries=None):
        """
        Tests if the string str_value fits the requirements specified for
        the field pointed by the field_path property.
        
        Returns None if no error was found, else returns a
        ValidationError instance.

        dictionary is the return value of provider.get_all_terms(dt_sid).
        If dictionary is none and the field has a closed dictionary, the
        value will be checked calling provider.check_term(str_value).
        """
        sf = self.provider.inspector.doc_types[self.dt_sid].simple_fields[field_path]
        val_len = len(str_value)
        val_err = None
        if val_len == 0:
            # The value is an empty string.
            err_type = ValidationErrorType.EMPTY_ELEMENT
            err_msg = "Il campo {0} è presente ma non compilato.".format(field_path)
            val_err = ValidationError(err_type, err_msg)
        if sf.length > 0:
            if sf.fixed_length:
                if not len(str_value) == sf.length:
                    # The value is not of the necessary length.
                    err_type = ValidationErrorType.WRONG_TEXT_LEN
                    err_msg = "Il campo {0} non è della lunghezza" \
                              " specificata.".format(field_path)
                    val_err = ValidationError(err_type, err_msg)
            elif val_len > sf.length:
                # The value is too long.
                err_type = ValidationErrorType.WRONG_TEXT_LEN
                err_msg = "Il testo del campo {0} è troppo" \
                          " lungo.".format(field_path)
                val_err = ValidationError(err_type, err_msg)
        if len(sf.validation_regex) > 0 \
            and not re.match(sf.validation_regex, str_value):
            err_type = ValidationErrorType.REGEX_ERR
            err_msg = "Il testo del campo {0} non rispetta il pattern" \
                      " specificato: ".format(field_path) + sf.validation_regex
            val_err = ValidationError(err_type, err_msg)
        if sf.dictionary_type == DictionaryType.CLOSED:
            if (dictionaries is None \
                and not self.provider.check_term(str_value)) \
                or (not field_path in dictionaries or not str_value in dictionaries[field_path]):
                err_type = ValidationErrorType.WRONG_TEXT_LEN
                err_msg = "Il valore immesso nel campo {0} non è tra" \
                          " quelli del dizionario chiuso.".format(field_path)
                val_err = ValidationError(err_type, err_msg)
        return val_err

    def validate(self):
        # Tutti i campi contrassegnati con required_for_saving devono essere compilati almeno
        # una volta.
        # Quando incontra un campo semplice, deve verificare che il suo valore rispetti
        # le regole.
        # Quando incontra un campo strutturato, deve verificare che non sia vuoto
        # Non ci devono essere salti nell'annidamento, es. da "CD.TSK" a "CD.NCT.NCTN"
        # senza passare per CD.NCT
        # I campi non ripetibili non devono essere ripetuti.
        # Deve iterare sui tre livelli di validazione proposti (I, P, C) a partire dal piu'
        # elevato. Se i campi richiesti non sono sufficienti, la scheda scala al livello inferiore.
        result = DocumentValidationResult()
        doc_type = self.provider.inspector.doc_types[self.dt_sid]
        dictionaries = self.provider.get_all_terms(self.dt_sid)
        prev_path = None
        self.catalogation_level = CatalogationLevel.NONE
        for x in self:
            if not x[0] in doc_type.all_elements:
                err_msg = "L'elemento {0} non è dichiarato nella definizione del Tipo di Documento {1}.".format(x[0], self.dt_sid)
                result.validation_errors.append(ValidationError(ValidationErrorType.INEXISTENT_ELEMENT, err_msg))
                result.can_be_saved = False
            else:
                if not prev_path is None and not doc_type.can_be_preceded(x[0], prev_path):
                    err_msg = "L'elemento {0} non può seguire direttamente l'elemento {1}.".format(x[0], prev_path)
                    result.validation_errors.append(ValidationError(ValidationErrorType.INCONSISTENT_STRUCTURE, err_msg))
                    result.can_be_saved = False
                prev_path = x[0]
                if x[0] in doc_type.simple_fields:
                    field_err = self.test_field_content(x[2], x[0], dictionaries)
                    if not field_err is None:
                        result.validation_errors.append(field_err)
                        result.can_be_saved = False
                else:
                    if len(x[2]) == 0:
                        error_msg = "L'elemento {0} è vuoto.".format(x[0])
                        result.validation_errors.append(ValidationError(ValidationErrorType.EMPTY_ELEMENT, err_msg))
        # Multimedia files check
        for x in self.media_files:
            if not x[0] in doc_type.multimedia_fields:
                err_msg = "Il file {0} è associato al campo {1} che non ammette allegati.".format(x[2], x[0])
                result.validation_errors.append(ValidationError(ValidationErrorType.FIELD_HAS_NO_MEDIA, err_msg))
                result.can_be_saved = False
            elif not x[1] in self.get_contents(x[0]):
                err_msg = "Il file {0} è associato al valore '{1}' per il campo {2}, ma tale valore non è presente.".format(x[2], x[1], x[0])
                result.validation_errors.append(ValidationError(ValidationErrorType.NO_VALUE_FOR_MEDIA, err_msg))
                result.can_be_saved = False
            # TODO: check if the file doesn't exist or has been uploaded by another user.
        # Verify the presence of fields marked with required_for_saving = True.
        for req_for_saving_path in doc_type.required_fields:
            if self.get_contents(req_for_saving_path) is None:
                err_msg = "Il campo semplice/sottocampo {0} non è presente, senza la scheda non può essere salvata.".format(x[0])
                result.validation_errors.append(ValidationError(ValidationErrorType.MISSING_FIELD, err_msg))
                result.can_be_saved = False
        # Assign the right catalogation level
        all_els_set = set([x[0] for x in self])
        for level_val in doc_type.required_elements_per_level:
            missing_fields = doc_type.required_elements_per_level[level_val] - all_els_set
            if len(missing_fields) == 0:
                self.catalogation_level = level_val
                result.catalogation_level = level_val
                break
        return result

    def validate_against_expr(self, search_expr):
        if search_expr.for_storage_only():
            raise ForStorageOnlyError()
        return self._evaluate_condition_group(search_expr.where.conditions)

    def _evaluate_condition_group(self, conditions):
        # Each element of bools is a tuple: (bool_op, bool_val),
        # i.e. [(None, False), (BooleanOperator.AND, True)]
        bools = []
        for c in conditions:
            if hasattr(c, "conditions"):
                b_tuple = (c.bool_op, self._evaluate_condition_group(c.conditions))
            else:
                b_tuple = (c.bool_op, self._evaluate_condition(c))
            bools.append(b_tuple)
        result = None
        for t in bools:
            if result is None:
                # the boolean operator of the first tuple is not considered:
                # it must be None.
                result = t[1] if t[0] is not BooleanOperator.NOT else not t[0]
            else:
                op = t[0]
                if op == BooleanOperator.AND:
                    result = result and t[1]
                elif op == BooleanOperator.OR:
                    result = result or t[1]
                elif op == BooleanOperator.AND_NOT:
                    result = result and not t[1]
                elif op == BooleanOperator.OR_NOT:
                    result = result or not t[1]
        return result
            
    def _evaluate_condition(self, condition):
        field_path = condition.field
        field_vals = None
        op = condition.comp_op
        comp_val = condition.compare_to
        doc_type = self.provider.inspector.doc_types[self.dt_sid]
        complete_path = doc_type.get_complete_paths(pure_path, error_if_ambiguous=True)[0]
        if field_path.endswith("._as_value"):
            simple_field = doc_type.simple_fields[complete_path]
            comp_val = doc_type.get_val_from_text(comp_val, simple_field)
            field_vals = self.get_contents_as_values(complete_path)
        elif field_path.endswith("._package_name"):
            field_vals = [self.package_name]
        elif field_path.endswith("._count"):
            field_vals = [len(self.get_contents(complete_path))]
            comp_val = int(comp_val)
        elif field_path.endswith("._author_id"):
            field_vals = [self.author_id]
        else:
            field_vals = self.get_contents(complete_path)
        if op == ComparisonOperator.EQUAL:
            if isinstance(comp_val, basestring):
                #String comparison is case-insensitive.
                field_vals = [x.upper() for x in field_vals]
                comp_val = comp_val.upper()
            def comp(field_val, comp_val): return field_val == comp_val
        elif op == ComparisonOperator.LESSER:
            def comp(field_val, comp_val): return field_val < comp_val
        elif op == ComparisonOperator.GREATER:
            def comp(field_val, comp_val): return field_val > comp_val
        elif op == ComparisonOperator.LESSER_OR_EQUAL:
            def comp(field_val, comp_val): return field_val <= comp_val
        elif op == ComparisonOperator.GREATER_OR_EQUAL:
            def comp(field_val, comp_val): return field_val >= comp_val
        elif op == ComparisonOperator.LIKE:
            def comp(field_val, comp_val): return comp_val.upper() in field_val.upper()
        return any([comp(x, comp_val) for x in field_vals])

class DocumentValidationResult:
    """
    An instance of this class is returned by the validate() method of the
    Document class.
    
    Here's the attributes exposed by the instances of this class.

    can_be_saved:                 Boolean value that specify if the document can be saved.
    catalogation_level:           Value taken from the enumeration
                                  sibaclib.documenttypes.CatalogationLevel that specifies
                                  the maximum catalogation level reached by this document.
    validation_errors:            A list of ValidationError instance.
    """
    def __init__(self):
        self.can_be_saved = True
        self.catalogation_level = CatalogationLevel.NONE
        self.validation_errors = []

class ValidationError:
    """
    This class describes the errors occurred during the validation
    of a documemnt.

    Attributes:

    error_type:       an enumerated value from ValidationErrorType.
    error_message:    the error message.
    """
    def __init__(self, error_type, error_message):
        self.error_type = error_type
        self.error_message = error_message

class ValidationErrorType:
    """
    This enumeration classifes the errors occurred during the validation
    of a documemnt.
    """
    NONE                     = 0
    EMPTY_ELEMENT            = 1  # A simple field with no value or a paragraph or
                                  # structured field without content.
    INCONSISTENT_STRUCTURE   = 2  # The order of the elements is not respected.
    INCONSISTENT_LEVEL       = 3  # True if there is a field that specifies the
                                  # catalogation level of the document and that
                                  # specifies a level that is not the real one,
                                  # i.e. "C" id the real level is "I".
    MISSING_FIELD            = 4  # A field for which required_for_saving is True
                                  # that is absent.

    INEXISTENT_ELEMENT       = 5  # The element does not exist in the document type.
    WRONG_TEXT_LEN           = 6  # Text is too long (> simple_field.max_length)
                                  # or fixed_length is True and
                                  # len(text) != simple_field.max_length
    REGEX_ERR                = 7  # Failed the test against a regular expression.
    NOT_IN_DICTIONARY        = 8  # A field was compiled using a term that is not
                                  # in the dictionary, and the dictionary_type
                                  # attribute for that field is
                                  # DictionaryType.Closed
    FIELD_HAS_NO_MEDIA       = 9  # A file is associated to a field that doesn't
                                  # accept files.
    NO_VALUE_FOR_MEDIA       = 10 # The file is attached to a value that doesn't
                                  # esist.
    FILE_NOT_FOUND           = 11 # The file doesn't exist.
