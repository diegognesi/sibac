# -*- coding: utf-8 -*-
from datetime import date
from sibaclib.documenttypes import *

document_type_def = {
    "sid": "SI",
    "alt": "Scheda di Sito Archeologico",
    "compliant": True,
    "author": "Diego Gnesi Bartolani",
    "creation_date": date(2012, 11, 2),
    "std_extension": "",
    "ext_extension": "cbc",
    "paragraphs": [
        { "sid": "CD", "alt": "Codici", "level": CatalogationLevel.I,
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
        { "sid": "RV", "alt": "Relazioni",
            "fields" : [
                { "sid": "RVE", "alt": "Struttura complessa",
                    "fields": [
                        { "sid": "RVEL", "alt": "Livello", "length": 25, "level": CatalogationLevel.I },
                        { "sid": "RVER", "alt": "Codice bene radice", "length": 25 },
                        { "sid": "RVES", "alt": "Codice bene componente", "length": 25, "repeatable": True }
                    ]
                },
                { "sid": "RSE", "alt": "Relazioni dirette", "repeatable": True,
                    "fields": [
                        { "sid": "RSER", "alt": "Tipo relazione", "length": 70, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.CLOSED },
                        { "sid": "RSET", "alt": "Tipo scheda", "length": 10, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "RSEC", "alt": "Codice bene", "length": 25, "level": CatalogationLevel.I }
                    ]
                },
                { "sid": "ROZ", "alt": "Altre relazioni", "length": 25, "repeatable": True }
            ]
        },
        { "sid": "AC", "alt": "Altri codici",
            "fields": [
                { "sid": "ACC", "alt": "Altro codice bene", "length": 25, "repeatable": True },
                { "sid": "ACS", "alt": "Schede correlate", "repeatable": True,
                    "fields": [
                        { "sid": "ACSE", "alt": "Ente", "length": 25, "level": CatalogationLevel.I },
                        { "sid": "ACSC", "alt": "Codice", "length": 25, "level": CatalogationLevel.I },
                        { "sid": "ACSS", "alt": "Specifiche", "length": 100 }
                    ]
                }
            ]
        },
        { "sid": "OG", "alt": "Oggetto", "level": CatalogationLevel.I,
            "fields": [
                { "sid": "OGT", "alt": "Oggetto", "level": CatalogationLevel.I,
                    "fields": [
                        { "sid": "OGTD", "alt": "Definizione", "length": 200, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "OGTT", "alt": "Precisazione tipologica", "length": 200, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "OGTA", "alt": "Livello di individuazione", "length": 100, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "OGTN", "alt": "Denominazione e numero sito", "length":  70 },
                        { "sid": "OGTY", "alt": "Denominazione tradizionale e/o storica", "length": 100 }
                    ]
                }
            ]
        },
        { "sid": "LC", "alt": "Localizzazione geografico-amministrativa", "level": CatalogationLevel.I, "repeatable": True,
            "fields": [
                { "sid": "PVC", "alt": "Localizzazione geografico-amministrativa", "level": CatalogationLevel.I, "repeatable": True,
                    "fields": [
                        { "sid": "PVCS", "alt": "Stato", "length": 50, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "PVCR", "alt": "Regione", "length": 25, "level": CatalogationLevel.I, "repeatable": True, "dictionary_type": DictionaryType.CLOSED },
                        { "sid": "PVCP", "alt": "Provincia", "length": 3, "level": CatalogationLevel.I, "repeatable": True, "dictionary_type": DictionaryType.CLOSED },
                        { "sid": "PVCC", "alt": "Comune", "length": 50, "level": CatalogationLevel.I, "repeatable": True, "dictionary_type": DictionaryType.CLOSED },
                        { "sid": "PVCL", "alt": "Località", "length": 50, "repeatable": True },
                        { "sid": "PVCI", "alt": "Indirizzo", "length": 250 },
                        { "sid": "PVCV", "alt": "Altre vie di comunicazione", "length": 1000 }
                    ]
                },
                { "sid": "PVL", "alt": "Altra località", "length": 250, "repeatable": True },
                { "sid": "PVE", "alt": "Diocesi", "length": 50, "dictionary_type": DictionaryType.OPEN }
            ]
        },
        { "sid": "CS", "alt": "Localizzazione catastale", "repeatable": True,
            "fields": [
                { "sid": "CTL", "alt": "Tipo di localizzazione", "length": 40, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.CLOSED },
                { "sid": "CTS", "alt": "Localizzazione catastale", "level": CatalogationLevel.I, "repeatable": True,
                    "fields": [
                        { "sid": "CTSC", "alt": "Comune", "length": 50, "level": CatalogationLevel.I, "dictionary_type": DictionaryType.OPEN },
                        { "sid": "CTSF", "alt": "Foglio/Data", "length": 25, "level": CatalogationLevel.I, "repeatable": True },
                        { "sid": "CTSN", "alt": "Particelle", "length": 500, "level": CatalogationLevel.I, "repeatable": True },
                        { "sid": "CTSP", "alt": "Proprietari", "length": 500, "repeatable": True },
                        { "sid": "CTSE", "alt": "Particelle ed altri elementi di confine", "length": 1000 }
                    ]
                }
            ]
        }
    ]
}
