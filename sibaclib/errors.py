# -*- coding: utf-8 -*-

class SearchExpressionError(Exception):
    """Generic error while using a SearcExpression instance."""
    pass

class ForStorageOnlyError(SearchExpressionError):
    """Metafields not allowed in the current context."""
    pass

class ElementNotDefined(SearchExpressionError):
    """The specified elememnt doesn't appear in the document type."""
    def __init__(self, element_path):
        self.element_path = element_path

    def __unicode__(self):
        return element_path

    def __str__(self):
        return unicode(element_path).encode("utf-8")

class AmbiguousElementPath(SearchExpressionError):
    """The specified path can refer to more than one element."""
    def __init__(self, element_path):
        self.element_path = element_path

    def __unicode__(self):
        return element_path

    def __str__(self):
        return unicode(element_path).encode("utf-8")
