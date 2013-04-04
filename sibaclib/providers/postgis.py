import imp
import os
import psycopg2
from sibaclib.documenttypes import FieldType

class SibacProvider:
    """
    This class allows to create, edit, query or delete a SIBAC Postgis database.
    """

    def __init__(self, settings, app_path, dt_inspector):
        """Class constructor"""
        self.inspector = dt_inspector
        self.settings = settings
        self._set_connection_string()

    def _set_connection_string(self):
        ds_info = self.settings.SIBACDATASOURCE
        conn_model = "host='{0}' port='{1}' dbname='{2}' user='{3}' password='{4}'"
        self._connection_string = conn_model.format(ds_info["HOST"],
                                                    ds_info["PORT"],
                                                    ds_info["DBNAME"],
                                                    ds_info["USER"],
                                                    ds_info["PASSWORD"])

    def _get_connection(self):
        """Returns a connection to the database"""
        return psycopg2.connect(self._connection_string)

    def _execute_ddl(self, sql_ddl, *params):
        """
        Executes a ddl statement or an instruction that doesn't returns values.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            if len(params) == 1 and isinstance(params[0], dict):
                # params[0] is a dictionary containing named args.
                cursor.execute(sql_ddl, params[0])
            elif len(params) > 0:
                cursor.execute(sql_ddl, params)
            else:
                cursor.execute(sql_ddl)
            conn.commit()
            cursor.close()
        finally:
            if not conn is None:
                conn.close() 

    def _execute_scalar(self, sql_str, *params):
        """
        Executes a query that returns only one value.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            if len(params) > 0:
                cursor.execute(sql_str, params)
            else:
                cursor.execute(sql_str)
            value = cursor.fetchone()
            if not value is None:
                value = value[0]
            conn.commit()
            cursor.close()
            return value
        finally:
            if not conn is None:
                conn.close()

    def _execute_list(self, sql_str, *params):
        """
        Executes a query and get a list of values in the first
        column of the resultset. If no record is found, returns an empty list.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            if len(params) > 0:
                cursor.execute(sql_str, params)
            else:
                cursor.execute(sql_str)
            value = cursor.fetchall()
            if not value is None:
                v2 = [x[0] for x in value]
                value = v2
            conn.commit()
            cursor.close()
            return value
        finally:
            if not conn is None:
                conn.close()

    def _execute_fetchall(self, sql_str, *params):
        """
        Executes a query and get a list of tuples representing
        the resultset. If no record is found, returns an empty list.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            if len(params) > 0:
                cursor.execute(sql_str, params)
            else:
                cursor.execute(sql_str)
            value = cursor.fetchall()
            conn.commit()
            cursor.close()
            return value
        finally:
            if not conn is None:
                conn.close()

    def _execute_many(self, sql_str, touple_of_dicts):
        """Executes the psycopg2 executemany() method."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executemany(sql_str, touple_of_dicts)
            conn.commit()
            cursor.close()
        finally:
            if not conn is None:
                conn.close()


    def _create_common_tables(self):
        users_table_name = self.settings.SIBACDATASOURCE['USERS_TABLE']
        users_id_field_name = self.settings.SIBACDATASOURCE['USERS_ID_FIELD']
        if len(users_table_name) > 0:
            usr_ref_string = " REFERENCES {0}({1}) ON DELETE SET NULL ON UPDATE CASCADE"
            usr_ref_string = usr_ref_string.format(users_table_name, users_id_field_name)
        else: 
            usr_ref_string = ""
        """Creates the tables shared by all documents."""
        ddl_string = """CREATE TABLE packages (
  name text PRIMARY KEY,
  description text NOT NULL,
  author text NOT NULL,
  iccd_version text NOT NULL,
  financier text NOT NULL,
  creation_date timestamp NOT NULL,
  iccd_esc text NOT NULL,
  iccd_ecp text NOT NULL,
  iccd_epr text,
  edit_date timestamp,
  author_id integer""" + usr_ref_string + """,
  last_editor_id integer""" + usr_ref_string + """);
CREATE TABLE sibac_main (
  id SERIAL PRIMARY KEY,
  package_name text NOT NULL REFERENCES packages(name) ON UPDATE CASCADE ON DELETE CASCADE,
  dt_sid text NOT NULL,
  full_who text NOT NULL,
  full_what text NOT NULL,
  full_where text NOT NULL,
  full_from_where text NOT NULL,
  full_when text NOT NULL,
  full_doc text NOT NULL,
  entire_document text NOT NULL,
  creation_date timestamp NOT NULL,
  edit_date timestamp NOT NULL DEFAULT CURRENT_DATE,
  author_id integer""" + usr_ref_string + """,
  last_editor_id integer """ + usr_ref_string + """\n);
SELECT AddGeometryColumn('sibac_main', 'points_data', {0}, 'MULTIPOINT', 2);
SELECT AddGeometryColumn('sibac_main', 'lines_data', {0}, 'MULTILINESTRING', 2);
SELECT AddGeometryColumn('sibac_main', 'polys_data', {0}, 'MULTIPOLYGON', 2);"""
        ddl_string = ddl_string.format(self.settings.GEOREFERENCING["EPSGID"])
        if self.settings.SIBACDATASOURCE['FULLTEXT'] == True:
            ddl_full_text_model = """
CREATE INDEX who_index ON sibac_main USING gin(to_tsvector('{0}', full_who));
CREATE INDEX what_index ON sibac_main USING gin(to_tsvector('{0}', full_what));
CREATE INDEX where_index ON sibac_main USING gin(to_tsvector('{0}', full_where));
CREATE INDEX from_where_index ON sibac_main USING gin(to_tsvector('{0}', full_from_where));
CREATE INDEX when_index ON sibac_main USING gin(to_tsvector('{0}', full_when));
CREATE INDEX doc_index ON sibac_main USING gin(to_tsvector('{0}', full_doc));"""
            ddl_string += ddl_full_text_model.format(self.settings.SIBACDATASOURCE["FULLTEXT_LANG"])
        self._execute_ddl(ddl_string)

    def _drop_common_tables(self):
        """Drops the tables shared by all documents."""
        drop_ddl = """DROP TABLE IF EXISTS sibac_main;
DROP TABLE IF EXISTS packages"""
        self._execute_ddl(drop_ddl);

    def _get_column_name(self, simple_field, as_value=False):
        """
        Returns the name that a simple field corresponding to a column
        has in the search table.
        """
        if as_value:
            return simple_field.complete_path.replace(".", "_") + "__val"
        else:
            return simple_field.complete_path.replace(".", "_") + "__str"

    def _get_db_field_declaration(self, simple_field, as_value=False):
        """
        Returns the declaration of a simple field for a DDL CREATE TABLE instruction.
        """
        f_name = self._get_column_name(simple_field, as_value)
        if as_value:
            f_name += " " + self._data_type_mappings[simple_field.field_type]
        else:
            f_name += " text"
        if simple_field.can_be_repeated:
            f_name += "[]"
        if simple_field.unique and not simple_field.uniqueness_group == 0:
            f_name += " UNIQUE"
        return f_name

    _data_type_mappings = {
                              FieldType.BOOLEAN: 'boolean',
                              FieldType.BYTE: 'smallint',
                              FieldType.INT16: 'smallint',
                              FieldType.INT32: 'integer',
                              FieldType.INT64: 'bigint',
                              FieldType.SINGLE: 'real',
                              FieldType.DOUBLE: 'double precision',
                              FieldType.DECIMAL: 'numeric',
                              FieldType.DATE: 'date',
                              FieldType.TIME: 'time',
                              FieldType.DATETIME: 'datetime',
                              FieldType.STRING: 'text',
                         }

    def _create_search_table(self, document_type):
        """
        This method creates the search table for a specific document type.
        """
        uniqueness_groups = {}
        ddl = """CREATE TABLE {0}_search (
  id integer NOT NULL PRIMARY KEY REFERENCES sibac_main (id) ON UPDATE CASCADE ON DELETE CASCADE,""".format(document_type.sid)
        for fsid in document_type.simple_fields:
            curr_field = document_type.simple_fields[fsid]
            if curr_field.unique and not curr_field.uniqueness_group == 0:
                if curr_field.uniqueness_group in uniqueness_groups:
                    uniqueness_groups[curr_field.uniqueness_group].append(self._get_column_name(curr_field))
                else:
                    uniqueness_groups[curr_field.uniqueness_group] = [self._get_column_name(curr_field)]
            ddl += "  " + self._get_db_field_declaration(curr_field, False) + ",\n"
            if not curr_field.field_type == FieldType.STRING:
                ddl += "  " + self._get_db_field_declaration(curr_field, True) + ",\n"
        for k in uniqueness_groups:
            ddl += "UNIQUE ({0}),\n".format(','.join(uniqueness_groups[k]))
        ddl = ddl[:-2] + "\n);"
        self._execute_ddl(ddl);

    def _create_multimedia_files_tables(self, document_type):
        """
        This method creates a table for each simple field associated to
        multimedia files.
        """
        for fsid in document_type.multimedia_fields:
            ddl = """CREATE TABLE {0}__media (
  doc_id integer NOT NULL REFERENCES sibac_main (id) ON UPDATE CASCADE ON DELETE CASCADE,
  field_str text NOT NULL,
  file_name text NOT NULL,
  PRIMARY KEY (doc_id, field_str, file_name)
)"""
            self._execute_ddl(ddl.format(fsid).replace(".", "_"))

    def _remove_multimedia_files_tables(self, document_type):
        """
        This method removes all the tables associated to a multimedial field
        in the specified document type.
        """
        for fsid in document_type.multimedia_fields:
            self._execute_ddl("DROP TABLE IF EXISTS {0}__media;".format(fsid).replace(".","_"))

    # Public interface methods.
    # If you wish to create another provider, make sure that your class
    # will expose the methods declared below.
    
    def initialize_storage(self):
        """This method creates the database tables."""
        self.initialize_settings()
        self.initialize_dictionaries()
        self._create_common_tables()

    def clear_storage(self):
        """This method deletes all objects from the database."""
        self.clear_settings()
        self.clear_dictionaries()
        self._drop_common_tables()

    def initialize_settings(self):
        """Creates the table used to store editable settings."""
        ddl_string = """CREATE TABLE sibac_settings (
  sett_key text NOT NULL PRIMARY KEY,
  sett_value text
        );"""
        self._execute_ddl(ddl_string)

    def clear_settings(self):
        """Drop the settings table if it not exists."""
        ddl_string = "DROP TABLE IF EXISTS sibac_settings;"
        self._execute_ddl(ddl_string)

    def initialize_dictionaries(self):
        """Creates the dictionary table."""
        ddl_string = """CREATE TABLE sibac_dictionaries (
  dt_sid text NOT NULL,
  f_sid text NOT NULL,
  term text NOT NULL,
  term_url text,
  PRIMARY KEY (dt_sid, f_sid, term)
  );"""
        self._execute_ddl(ddl_string)

    def clear_dictionaries(self):
        """Drop the dictionary table if it not exists."""
        ddl_string = "DROP TABLE IF EXISTS sibac_dictionaries;"
        self._execute_ddl(ddl_string)

    def initialize_doc_type(self, dt_sid):
        """Creates the database entities concerning a specific document type."""
        doc_type = self.inspector.doc_types[dt_sid]
        self._create_search_table(doc_type)
        self._create_multimedia_files_tables(doc_type)

    def remove_doc_type(self, dt_sid):
        """Removes the database entities concerning a specific document type."""
        ddl = "DROP TABLE IF EXISTS {0}_search;".format(dt_sid)
        self._execute_ddl(ddl);
        doc_type = self.inspector.doc_types[dt_sid]
        self._remove_multimedia_files_tables(doc_type)
        pass

    def initialize_all_doc_types(self):
        """Creates the database entities concerning all document types."""
        for sid in self.inspector.doc_types:
            self.initialize_doc_type(sid)

    def remove_all_doc_types(self):
        """Removes the database entities concerning all document types."""
        for sid in self.inspector.doc_types:
            self.remove_doc_type(sid)

    def change_setting(self, key, value):
        """Adds or updates a setting.

        Both key and value must be strings. It's also possibile to set a value
        to None."""
        sql_str = """UPDATE sibac_settings SET sett_value=%(val)s WHERE sett_key=%(key)s;
INSERT INTO sibac_settings (sett_key, sett_value)
SELECT %(key)s, %(val)s
WHERE NOT EXISTS (SELECT 1 FROM sibac_settings WHERE sett_key=%(key)s);"""
        param_dict = {"key": key, "val": value}
        self._execute_ddl(sql_str, param_dict)

    def delete_setting(self, key, delete_if_none=False):
        """Delete a setting from the table.

        If the second argument is True, the setting will be deleted only if
        it's value is None."""
        if delete_if_none:
            sql_str = "DELETE FROM sibac_settings WHERE sett_key=%s AND sett_value IS NULL"
        else:
            sql_str = "DELETE FROM sibac_settings WHERE sett_key=%s"
        self._execute_ddl(sql_str, key)

    def get_setting(self, key):
        """Returns the value for the given key, or None if the key doesn't exist."""
        sql_str = """SELECT sett_value FROM sibac_settings WHERE sett_key=%s"""
        return self._execute_scalar(sql_str, key)

    def get_all_settings(self):
        """Returns a dictionary of settings."""
        sql_str = """SELECT sett_key, sett_value FROM sibac_settings"""
        tuples = self._execute_fetchall(sql_str)
        result = {}
        for t in tuples:
            result[t[0]] = t[1]
        return result

    def delete_all_settings(self, delete_if_none=False):
        """Delete all settings from the table.

        If the second argument is True, the settings will be deleted only if
        their values are None."""
        if delete_if_none:
            sql_str = "DELETE FROM sibac_settings WHERE sett_value IS NULL"
        else:
            sql_str = "DELETE FROM sibac_settings"
        self._execute_ddl(sql_str)

    def change_all_settings(self, settings_dict):
        """Sets all settings."""
        tuple_of_dicts = tuple([{"k": k, "v": settings_dict[k]} for k in settings_dict])
        sql_str = """UPDATE sibac_settings SET sett_value=%(v)s WHERE sett_key=%(k)s;
INSERT INTO sibac_settings (sett_key, sett_value)
SELECT %(k)s, %(v)s
WHERE NOT EXISTS (SELECT 1 FROM sibac_settings WHERE sett_key=%(k)s);"""
        self._execute_many(sql_str, tuple_of_dicts)
        

    def add_term(self, field_path, term, url=None):
        """
        Add a term to the dictionary.

        It's your matter to ensure that the field supports dictionaries in the
        document type definition.
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        sql_str = "INSERT INTO sibac_dictionaries (dt_sid, f_sid, term, term_url) VALUES (%s, %s, %s, %s)"
        self._execute_ddl(sql_str, dt_sid, norm_path, term, url)

    def remove_term(self, field_path, term):
        """
        Remove a term from the dictionary.

        This function will return True if the term has been correctly removed,
        False if the term doesn't exist in the database.
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        sql_str = "DELETE FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s AND term=%s"
        self._execute_ddl(sql_str, dt_sid, norm_path, term)

    def remove_all_terms(self, field_path):
        """
        Removes all terms for the given field.
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        sql_str = "DELETE FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s"
        self._execute_ddl(sql_str, dt_sid, norm_path)

    def remove_all_terms_for_doc_type(self, dt_sid):
        """
        Romoves all terms for all the fields of the specified Document Type
        """
        sql_str = "DELETE FROM sibac_dictionaries WHERE dt_sid=%s"
        self._execute_ddl(sql_str, dt_sid)

    def check_term(self, field_path, term):
        """
        This method returns a boolean value that specifies if a term exists in the
        dictionaries tables.
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        sql_str = "SELECT EXISTS (SELECT true FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s AND term=%s);"
        return self._execute_scalar(sql_str, dt_sid, norm_path, term)

    def get_terms(self, field_path, starts_with=None):
        """
        This method returns a list terms.

        Usage:

        provider.get_terms("SI.CD.TSK")
        ["SI"]
        
        or

        provider.get_terms("SI.CD.ECP", "S")
        ["S01", "S02", ...]
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        if starts_with is None:
            sql_str = "SELECT term FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s"
            params = (dt_sid, norm_path)
        else:
            sql_str = "SELECT term FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s AND term ILIKE %s"
            params = (dt_sid, norm_path, starts_with.replace("%", "\%").replace("_", "\_") + "%")
            print params
        return self._execute_list(sql_str, *params)

    def get_terms_with_urls(self, field_path, starts_with=None):
        """
        This method returns a list of terms.

        Usage:

        provider.get_terms("SI.CD.TSK")
        ["SI"]
        
        or

        provider.get_terms("SI.CD.ECP", "S")
        ["S01", "S02", ...]
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        if starts_with is None:
            sql_str = "SELECT term, term_url FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s"
            params = (dt_sid, norm_path)
        else:
            sql_str = "SELECT term, term_url FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s AND term ILIKE %s"
            params = (dt_sid, norm_path, starts_with.replace("%", "\\%").replace("_", "\_") + "%")
        return self._execute_fetchall(sql_str, *params)

    def get_all_terms(self, dt_sid):
        """
        This method returns a dictionary containing lists of terms grouped
        by field id.

        Usage:

        provider.get_all_terms("SI")
        {"SI.CD.TSK": ["SI"], "SI.CD.LIR": ["I", "P", "C"], ...}
        """
        sql_str = "SELECT f_sid, term FROM sibac_dictionaries WHERE dt_sid=%s ORDER BY f_sid, term"
        dataset = self._execute_fetchall(sql_str, dt_sid)
        ret_dict = {}
        for row in dataset:
            k = row[0]
            v = row[1]
            if k in ret_dict:
                ret_dict[k].append(v)
            else:
                ret_dict[k] = [v]
        return ret_dict

    def get_all_terms_url(self, dt_sid):
        """
        This method returns a dictionary containing lists of tuples (term, url) grouped
        by field id.

        Usage:

        provider.get_all_terms("SI")
        {"SI.CD.TSK": [("SI", "http://www.x.yy"), ...], "SI.CD.LIR": [("I", "http://..."), ...]
        """
        sql_str = "SELECT f_sid, term, term_url FROM sibac_dictionaries WHERE dt_sid=%s ORDER BY f_sid, term"
        dataset = self._execute_fetchall(sql_str, dt_sid)
        ret_dict = {}
        for row in dataset:
            k = row[0]
            t = (row[1], row[2])
            if k in ret_dict:
                ret_dict[k].append(t)
            else:
                ret_dict[k] = [t]
        return ret_dict

    def get_term_url(self, field_path):
        """
        Gets an url corresponding to the specific term.

        If the term doesn't exist or doesn't have an url, this method
        returns None
        """
        dt_sid = self.inspector.get_doc_type_sid(field_path)
        norm_path = field_path.replace('.', '_')
        sql_str = "SELECT term_url FROM sibac_dictionaries WHERE dt_sid=%s AND f_sid=%s"
        self._execute_scalar(sql_str, dt_sid, norm_path)
