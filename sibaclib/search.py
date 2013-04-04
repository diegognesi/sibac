# -*- coding: utf-8 -*-
import re, copy
from sibaclib.documenttypes import FieldType, MediaType

class BooleanOperator:
    """Enum of all boolean operators used in search expressions."""
    AND      = 1
    OR       = 2
    NOT      = 3
    AND_NOT  = 4
    OR_NOT   = 5

class ComparisonOperator:
    """Enum of all comparison operators used in search expressions."""
    EQUAL                  = 0
    LESSER                 = 1
    GREATER                = 2
    LESSER_OR_EQUAL        = 3
    GREATER_OR_EQUAL       = 4
    LIKE                   = 5

class SearchCondition:
    """Represents a single search condition.
    
    Attributes:
    
    bool_op:        Enumeration value taken from the BooleanOperator class. It is used
                    to tell how this condition is merged with the previous one in a
                    search expression. Default is None (no previous conditions).
    field           Field that must satisfy the search condition.
    comp_op         Enumeration value taken from the ComparisonOperator class.
    compare_to      The value to be compared to the field content. Must be a string.
    """
    def __init__(self, bool_op = None, field = None, comp_op = None, compare_to = None):
        """Constructor method."""
        self.bool_op = bool_op
        self.field = field
        self.comp_op = comp_op
        self.compare_to = compare_to

    def __unicode__(self):
        """Represents the condition as unicode text."""
        if self.bool_op == BooleanOperator.AND:
            op_str = "AND "
        elif self.bool_op == BooleanOperator.OR:
            op_str = "OR "
        elif self.bool_op == BooleanOperator.NOT:
            op_str = "NOT "
        elif self.bool_op == BooleanOperator.AND_NOT:
            op_str = "AND NOT "
        elif self.bool_op == BooleanOperator.OR_NOT:
            op_str = "OR NOT "
        else:
            op_str = ""
        if self.comp_op == ComparisonOperator.EQUAL:
            comp_str = "="
        elif self.comp_op == ComparisonOperator.LESSER:
            comp_str = "<"
        elif self.comp_op == ComparisonOperator.GREATER:
            comp_str = ">"
        elif self.comp_op == ComparisonOperator.LESSER_OR_EQUAL:
            comp_str = "<="
        elif self.comp_op == ComparisonOperator.GREATER_OR_EQUAL:
            comp_str = ">="
        elif self.comp_op == ComparisonOperator.LIKE:
            comp_str = "LIKE"
        return '{0}[{1}] {2} "{3}"'.format(op_str, self.field, comp_str, self.compare_to)

    def __str__(self):
        """Represents the condition as text."""
        return unicode(self).encode('utf-8')

class Parenthesis:
    """Represents a group of search conditions.
    
    Attributes:
    
    bool_op:        Enumeration value taken from the BooleanOperator class. It is used
                    to tell how this group is merged with the previous condition in a
                    search expression. Default is None (no previous conditions).
    conditions:     A list of search conditions.
    """
    def __init__(self, bool_op = None, conditions=None):
        self.bool_op = bool_op
        if conditions is None:
            self.conditions = []
        else:
            self.conditions = conditions

    def fields_contain(self, words):
        """Returns true if any of the listed word is inside a field
           name used in this Parenthesis or in a nested one.

        Arguments:

        not_allowed: A single word or a list words.
        """
        result = False
        for c in conditions:
            if hasattr(c, "conditions"):
                if c.fields_contain(words):
                    return True
            else:
                for w in words:
                    if w in c.field:
                        return True
        # No match if you arrived here!
        return False

    def __unicode__(self):
        """Represents the parenthesis as unicode text."""
        if self.bool_op == BooleanOperator.AND:
            op_str = "AND "
        elif self.bool_op == BooleanOperator.OR:
            op_str = "OR "
        elif self.bool_op == BooleanOperator.NOT:
            op_str = "NOT "
        elif self.bool_op == BooleanOperator.AND_NOT:
            op_str = "AND NOT "
        elif self.bool_op == BooleanOperator.OR_NOT:
            op_str = "OR NOT "
        else:
            op_str = ""
        return op_str + "(" + " ".join([str(c) for c in self.conditions]) + ")"

    def __str__(self):
        """Represents the parenthesis as text."""
        return unicode(self).encode('utf-8')

class OrderingCondition:
    """An ordering condition, composed by a field name and a sorting direction.

    Attributes:

    field:      A string equal to the field name (if unambigous) or to the field
                complete path (i.e. 'RA.CD.NCT.NCTN').
    ascendant:  True (default) to sort results in an ascending order. 
    """
    def __init__(self, field = None, ascendant=True):
        self.field = field
        self.ascendant = ascendant

    def __unicode__(self):
        """Represents the ordering condition as unicode text."""
        if self.ascendant:
            format_str = "{0} ASC"
        else:
            format_str = "{0} DESC"
        return format_str.format(self.field)

    def __str__(self):
        """Represents the ordering condition as text."""
        return unicode(self).encode('utf-8')

class SearchExpression:
    """An graph of objects that describes the query to perform against the
    storage.

    Attributes:

    select:          A list of field names or paths, i.e. ["NCTN", "NCTS"].
    from_doc:        The sid (sibac-id) of the document type. I.e. "RA".
    where:           An instance of the Parenthesis class.
    order_by:        A list of field names or paths.
    """
    def __init__(self, expr_str=""):
        """Class constructor.
        
        Usage:
        se = SearchExpression()
        se2 = SearchExpression('SELECT * FROM RA WHERE PVCP = "AN"')
        """
        if not (expr_str == None or expr_str == ""):
            self._set_from_string(expr_str)
        else:
            self.clear()

    def clear(self):
        """Clears this search expression instance."""
        self.select = []
        self.from_doc = ""
        self.where = Parenthesis()
        self.order_by = []

    def _set_from_string(self, expr_str):
        """Private method, called by __init__() to set the expression
           properties from a string.
        """
        self.clear()
        # Tokenize 
        splitter = re.compile(r'"(?:[^\\"]|\\.)*"|<=|>=|<|>|=|\[[a-z_.]+\]|[a-z_.]+|\*|\(|\)', re.IGNORECASE)
        tokens = splitter.findall(expr_str)
        interpreter = None
        for t in tokens:
            tup = t.upper()
            if tup == "SELECT":
                interpreter = _SelectTokensInterpreter(self)
            elif tup == "FROM":
                interpreter = _FromTokensInterpreter(self)
            elif tup == "WHERE":
                interpreter = _WhereTokensInterpreter(self)
            elif tup == "ORDER_BY":
                interpreter = _OrderByTokensInterpreter(self)
            else:
                interpreter.read(self._remove_brackets(t))

    def _remove_brackets(self, token):
        """Removes square brackets from a field name."""
        if token[0] == "[" and token[-1] == "]":
            return token[1:-1]
        else:
            return token

    def for_storage_only(self):
        """Returns True if the expression can be used only for saved documents.

        If False, it means that this search expression cannot be used as
        an argument for the validate_against_expr method of the
        sibaclib.documents.Document class or to set permissions for a user.
        """
        not_allowed = get_for_storage_only_metafields()
        # Search on 'SELECT' part.
        for word in not_allowed:
            for selected in self.select:
                if word in selected:
                    return False
        # Search on 'WHERE' part.
        if self.where.fields_contain(not_allowed):
            return False
        # Search on 'ORDER_BY' part.
        for word in not_allowed:
            for ordered in self.order_by and word in ordered.field:
                return False
        # If you arrived here, that's ok!
        return True

    def get_for_storage_only_metafields(self):
        result = [
                "_id",
                "_count",
                "_attachment_count",
                "_points",
                "_lines",
                "_polygons",
                "_area",
                "_perimeter",
                "_in_box",
                "_in_circle",
                "_whithin_polygon",
                "_creation_date",
                "_last_edit_date",
                "_author",
                "_author_id",
                "_last_editor",
                "_last_editor_id",
                "_who",
                "_what",
                "_when",
                "_where",
                "_from_where"
            ]
        return result

    def get_accepted_metafields(self):
        """Returns a list of accepted metafields."""
        accepted = [
                "_id",
                "_as_val",
                "_count",
                "_attachment_count",
                "_points",
                "_lines",
                "_polygons",
                "_area",
                "_perimeter",
                "_in_box",
                "_in_circle",
                "_whithin_polygon",
                "_creation_date",
                "_last_edit_date",
                "_author",
                "_author_id",
                "_last_editor",
                "_last_editor_id",
                "_who",
                "_what",
                "_when",
                "_where",
                "_from_where",
                "_package_name"
            ]
        return accepted
    
    @staticmethod
    def validate_expression_string(search_expression_str, provider, allow_for_storage_only = False):
        """Validates an expression string.

        This method returns a tuple composed by a SearchExpressionValidationResult instance and
        and an instance of the SearchExpression class. If the validation process returns errors,
        the second element of the tuple will be None.
        """
        se = None
        try:
            se = SearchExpression(search_expression_str)
        except:
            errors = ["Errore durante il parsing dell'espressione. Controlla la sintassi."]
        if not se is None:
            doc_type_sid = se.from_doc
            if not doc_type_sid in provider.inspector.doc_types:
                errors = ["Il tipo di documento specificato nella clausola FROM non esiste."]
            else:
                doc_type = provider.inspector.doc_types[doc_type_sid]
                val_res = se.validate(doc_type, allow_for_storage_only)
                errors = val_res.errors
        is_valid = len(errors) == 0
        return SearchExpressionValidationResult(is_valid, errors), se

    def validate(self, document_type, allow_for_storage_only = False):
        """Validates the search expression.

        Returns an instance of the SearchExpressionValidationResult class.

        Arguments:

        document_type:          An instance of sibaclib.documenttypes.DocumentType.

        allow_for_storage_only: true if the expression will be valid also if
                                it contains expressions that can be used
                                only against saved documents.
        """
        errors = []
        accepted_metas = self.get_accepted_metafields
        for_storage_only = self.get_for_storage_only_metafields()
        # Validate 'SELECT' part
        for s in self.select:
            if not s == "*":
                self._validate_field(document_type, s, errors, allow_for_storage_only)
        # Validate 'FROM' part
        if not self.from_doc == document_type.sid:
            errors.append("Tipo di document specificato nella clausola FROM non corrispondente a quello utilizzato per la validazione.")
        # Validate 'WHERE' part
        if len(self.where.conditions) > 0:
            # This closure creates a 'flat' view on search conditions and paragraph
            def check_where_conditions(parenthesis):
                is_first = True
                for c in parenthesis.conditions:
                    # Check boolean operators.
                    bool_is_not_or_none = (c.bool_op is None or c.bool_op == BooleanOperator.NOT)
                    if is_first and not bool_is_not_or_none:
                        errors.append("La prima condizione in un'espressione di ricerca o in una parentesi non ammette operatori booleani diversi da NOT.")
                    if not is_first and bool_is_not_or_none:
                        errors.append("Una condizione di ricerca che non sia la prima dell'espressione o della parentesi in cui è inserita non ammette l'operatore booleano nullo o l'operatore NOT.")
                    if hasattr(c, "conditions"):
                        check_where_conditions(c)
                    else:
                        # Validate field
                        field_name, metafield_name, paths, is_doc, err_count = self._validate_field(document_type, c.field, errors, allow_for_storage_only)
                        if (err_count == 0):
                            is_simple_field = paths[0] in document_type.simple_fields
                            is_doc_type = field_name == document_type.sid
                            is_para_or_struc = not (is_simple_field or is_doc_type)
                            # Validate comparison_operator
                            if c.comp_op == ComparisonOperator.LESSER or \
                                c.comp_op == ComparisonOperator.GREATER or \
                                c.comp_op == ComparisonOperator.LESSER_OR_EQUAL or \
                                c.comp_op == ComparisonOperator.GREATER_OR_EQUAL:
                                std_message = "Gli operatori <, >, <=, >= non possono essere usati sull'elemento {0}."
                                if is_para_or_struct:
                                    if not metafield_name == "_count":
                                        errors.append(std_message.format(c.field))
                                if is_doc_type:
                                    allowed_mf_list = ["_id", "_creation_date", "_last_edit_date",
                                                       "_author", "_author_id", "_last_editor",
                                                       "_last_editor_id", "_package_name"]
                                    if not metafield_name in allowed_mf_list:
                                        errors.append(std_message.format(c.field))
                            if c.comp_op == ComparisonOperator.LIKE:
                                std_message = "L'operatore LIKE non può essere usato sull'elemento {0}."
                                if not is_simple_field:
                                    errors.append(std_message.format(c.field))
                                else:
                                    if not (metafield_name is None or \
                                        document_type.simple_fields[paths[0]].field_type == FieldType.STRING):
                                        errors.append(std_message.format(c.field))
                            # Validate compare_to:
                            cto = c.compare_to
                            if not cto:
                                errors.append("Una condizione di ricerca è priva di termine di paragone.")
                            else:
                                if metafield_name == "_as_val" and document_type.get_val_from_text(c.compare_to, document_type.simple_fields[paths[0]]) is None:
                                    errors.append("Tentativo di conversione fallito rispetto al tipo di dati di {1}.".format(c.compare_to, field_name))
                                        
                    is_first = False
            check_where_conditions(self.where)
        # Validate 'ORDER_BY' part
        for o in self.order_by:
            _validate_field(document_type, s.name, errors, allow_for_storage_only)
        is_valid = len(errors) == 0
        return SearchExpressionValidationResult(is_valid, errors)

    def _validate_field(self, document_type, field, errors, allow_for_storage_only):
        if "._" in field:
            underscore_index = field.index("._")
            field_name = field[:underscore_index]
            metafield_name = field[underscore_index + 1:]
        else:
            field_name = field
            metafield_name = None
        is_doc = field_name == document_type.sid
        err_count = len(errors)
        # Check if the field (or doc_type) exists and is not ambiguous.
        paths = document_type.get_complete_paths(field_name, False)
        if len(paths) == 0:
            errors.append("L'elemento {0} non è stato riconosciuto.".format(field_name))
        elif len(paths) > 1:
            joined_paths = "; ".join(paths)
            err_msg = "L'elemento {0} è ambiguo e potrebbe essere riferito a: {1}.".format(field_name, joined_paths)
            errors.append(err_msg)
        else:
            # Check if the metafield exists.
            if not metafield_name is None:
                if metafield_name == "_attachment_count" and paths[0] in document_type.simple_fields:
                    if document_type.simple_fields[paths[0]].media_type == MediaType.NONE:
                        errors.append("Il campo semplice {0} non può essere usato per il metacampo '_attachment_count' perché non può avere allegati.".format(field_name))
                if not metafield_name in self.get_accepted_metafields():
                    errors.append("Il metacampo {0} non esiste.").format(metafield_name)
                if not allow_for_storage_only and metafield_name in self.get_for_storage_only_metafields():
                    errors.append("Il metacampo {0} non può essere usato per validare documenti non ancora salvati o per attribuire permessi utente.".format(metafield_name))
                # Check if the metafield can be applied to the field.
                is_meta_for_doc = not metafield_name in ["_count", "_attachment_count", "_as_val"]
                if is_doc and not is_meta_for_doc:
                    errors.append("Il metacampo {0} non può essere usato sul tipo di documento.".format(metafield_name))
                if not is_doc and is_meta_for_doc:
                    errors.append("Il metacampo {0} può essere usato solo sul tipo di documento e non su altri nomi di campo.".format(metafield_name))
                # Only _count can be used on paragraphs or structured fields.
                if paths[0] in [p.sid for p in document_type.paragraphs] and not metafield_name == "_count":
                    errors.append("Il metacampo {0} non può essere usato su elementi diversi dai campi semplici.".format(metafield_name))
            else:
                if not paths[0] in document_type.simple_fields:
                    errors.append("Il tipo di documento e il nome di campi strutturati o paragrafi non possono essere utilizzati in un'espressione di ricerca senza associarli a metacampi.")
        # The last argument tells how many errors we had on this field.
        return field_name, metafield_name, paths, is_doc, len(errors) - err_count

    @staticmethod
    def merge(expr_1, expr_2, bool_op = BooleanOperator.AND):
        """Returs a deep copy of the first expression, where the conditions
        are merged to the conditions of the second expression.

        Usage:
        se = SearchExpression('SELECT * FROM RA WHERE PVCP="AN" OR PVCP="MC"')
        se2 = SearchExpression('SELECT * FROM RA WHERE OGTD="Anfora"')
        se3 = SearchExpression.merge(se, se2)
        print se3
        'SELECT * FROM [RA] WHERE ([PVCP]="AN" OR [PVCP]="MC") AND OGTD="Anfora"'
        """
        new_expr = copy.deepcopy(expr_1)
        p1 = Parenthesis()
        p1.conditions = new_expr.where.conditions
        p2 = Parenthesis(bool_op = bool_op)
        p2.conditions = copy.deepcopy(expr_2.where.conditions)
        new_expr.where = Parenthesis(conditions = [p1, p2])
        new_expr.simplify()
        return new_expr

    def simplify(self, conditions = None):
        """Removes exceeding parentheses.

        Usage:
        my_expression.simplify()
        """
        if conditions is None:
            conditions = self.where.conditions
        for i in range(len(conditions)):
            while hasattr(conditions[i], "conditions") \
                and len(conditions[i].conditions) == 1:
                new_cond = copy.deepcopy(conditions[i].conditions[0])
                new_cond.bool_op = conditions[i].bool_op
                conditions[i] = new_cond
            if hasattr(conditions[i], "conditions"):
                self.simplify(conditions[i].conditions)

    def __unicode__(self):
        """Returns an unicode representation of this search expression."""
        fields_str = ["[" + f + "]" if not f == "*" else "*" for f in self.select]
        expr_str = "SELECT {0} FROM [{1}]".format(", ".join(fields_str), self.from_doc)
        if len(self.where.conditions) > 0:
            expr_str += " WHERE " + " ".join([str(c) for c in self.where.conditions])
        if len(self.order_by) > 0:
            expr_str += "ORDER_BY" + " ".join([str(o) for o in self.order_by])
        return expr_str

    def __str__(self):
        """Returns a string representation of this search expression."""
        return unicode(self).encode('utf-8')

class _SelectTokensInterpreter:
    """Class used by SearchExpression._set_from_string() method."""
    def __init__(self, search_expression):
        self.se = search_expression

    def read(self, token):
        self.se.select.append(token)

class _FromTokensInterpreter:
    """Class used by SearchExpression._set_from_string() method."""
    def __init__(self, search_expression):
        self.se = search_expression

    def read(self, token):
        self.se.from_doc = token

class _WhereTokensInterpreter:
    """Class used by SearchExpression._set_from_string() method."""
    def __init__(self, search_expression):
        self.se = search_expression
        self.stack = [search_expression.where]
        self.current_bool_op = None
        self.tokens = []

    def read(self, token):
        tup = token.upper()
        if tup == "AND":
            self.current_bool_op = BooleanOperator.AND
        elif tup == "OR":
            self.current_bool_op = BooleanOperator.OR
        elif tup == "NOT":
            if self.current_bool_op is None:
                self.current_bool_op is BooleanOperator.NOT
            elif self.current_bool_op == BooleanOperator.AND:
                self.current_bool_op = BooleanOperator.AND_NOT
            elif self.current_bool_op == BooleanOperator.OR:
                self.current_bool_op = BooleanOperator.OR_NOT
        elif tup == "(":
            p = Parenthesis(bool_op = self.current_bool_op)
            self.stack.append(p)
            self.current_bool_op = None
        elif tup == ")":
            p = self.stack.pop()
            self.stack[-1].conditions.append(p)
        else:
            self.tokens.append(token)
            if self._process_tokens():
                self.current_bool_op = None
                self.tokens = []

    def _process_tokens(self):
        l_toks = len(self.tokens)
        if l_toks == 3:
            up_comp = self.tokens[1].upper()
            if up_comp == "=":
                comp = ComparisonOperator.EQUAL
            elif up_comp == "<":
                comp = ComparisonOperator.LESSER
            elif up_comp == ">":
                comp = ComparisonOperator.GREATER
            elif up_comp == "<=":
                comp = ComparisonOperator.LESSER_OR_EQUAL
            elif up_comp == ">=":
                comp = ComparisonOperator.GREATER_OR_EQUAL
            elif up_comp == "LIKE":
                comp = ComparisonOperator.LIKE
            sc = SearchCondition(self.current_bool_op, self.tokens[0], comp, self.tokens[2][1:-1])
            self.stack[-1].conditions.append(sc)
            return True
        else:
            return False

class _OrderByTokensInterpreter:
    """Class used by SearchExpression._set_from_string() method."""
    def __init__(self, search_expression):
        self.se = search_expression
        self.curr_ascendant = True

    def read(self, token):
        tup = token.upper()
        if tup == "ASC":
            self.curr_ascendant = True
        elif tup == "DESC":
            self.curr_ascendant = False
        else:
            oc = OrderingCondition(token, self.curr_ascendant)
            self.se.order_by.append(oc)
            self.curr_ascendant = True

class SearchExpressionValidationResult:
    """Instance of this class are returned by the SearchExpression.validate method.

    Attributes:

    is_valid:            True if the search expression is valid.
    errors:              A list of string containing errors.
    """
    def __init__(self, is_valid=True, errors=None):
        self.is_valid = is_valid
        if (errors is None):
            self.errors = []
        else:
            self.errors = errors
