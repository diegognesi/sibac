from datetime import date
from sibaclib.doctypes.documenttypes import *


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
    ]
}
