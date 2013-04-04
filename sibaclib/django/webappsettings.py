from django.utils import simplejson

class ApplicationPermissions:
    """Application security settings and default permissions on documents.
    
    Attributes:

    registration_mode:    "SELF" if a user can autonomously register,
                          "SELF_WITH_EMAIL" if a user can autonomously
                          register, but the registration must be confirmed
                          going to a link sended via e-mail.
                          "BY_ADMINS" if only administrators can register,
                          a new user. Default is "SELF".
    document_permissions: a dictionary of DocumentPermissions instance.
                          Dictionary keys must be equal to the dt_sid
                          property of DocumentPermissions instances.
                          The defualt value is an empty dictionary.
    """
    def __init__(self, registration_mode = "SELF", document_permissions = None):
        """Class constructor."""
        self.registration_mode = registration_mode
        if not document_permissions is None:
            self.permissions = document_permissions
        else:
            self.permissions = {}

class DocumentPermissions:
    """Default permissions on a document.
    
    Attributes:
    
    dt_sid:                 Sibac ID of the DocumentType
    is_active:              True if non-admin users can access to the documents.
                            Default is True.
    access_level:           "PUBLIC" if all users can access to the documents.
                            "REGISTERED" if the access is limited to registerd users.
                            "EXPLICIT" if the access is limited to registerd users
                            with explicit permissions.
    watermark_by_default:   True if a watermark will be automatically added to
                            attachments that support it when they are displayed.
                            Default value is False.
    w_access_level:         "PUBLIC" if all users can create and edit documents.
                            "REGISTERED" if editing is limited to registerd users.
                            "EXPLICIT" if editing is limited to registerd users
                            with explicit permissions.
    visible_paragraphs      The list of paragraphs visible by default.
    default_expression      The search expression string that will limit non-admins
                            searches applied by default.
    """
    def __init__(self, dt_sid, is_active=True, access_level="PUBLIC",
                 watermark_by_default=False, w_access_level="REGISTERED"):
        self.dt_sid = dt_sid
        self.is_active = is_active
        self.access_level = access_level
        self.watermark_by_default = watermark_by_default
        self.w_access_level = w_access_level
        self.visible_paragraphs = ["*"]
        self.default_expression = None

    def visible_paragraphs_abbr_string(self, max_paragraphs=5):
        """Converts into an abbreviated string the list of visible paragraphs.

        Arguments:

        max_paragraphs: max number of paragraphs to show.

        Returned value:

        A string like this:
        "CD, RV, AC, OG. LC, ecc."
        """
        paras_num = len(self.visible_paragraphs)
        if paras_num == 0:
            return ""
        elif self.visible_paragraphs[0] == "*":
            return "*"
        else:            
            joined = ", ".join(self.visible_paragraphs[:max_paragraphs])
            if paras_num > max_paragraphs:
                joined += ", ecc."
            return joined

    def default_expression_abbr_string(self, max_chars=20):
        """Return a Search expression abbreviated to the max_chars char number plus "..."."""
        if self.default_expression:
            if len(self.default_expression) > max_chars:
                return self.default_expression[:max_chars] + "..."
            else:
                return self.default_expression
        else:
            return ""

class EmailSettings:
    """Email settings"""
    def __init__(self, email_from=None, host=None, port=None, username=None,
                 password=None, use_tls=None):
        self.email_from = email_from
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

class WebAppSettings:
    """Settings of a web running sibaclib

    Attributes:

    title:             Site's title (string)
    subtitle:          Site's subtitle (string)
    url:               Site's url (string)
    description:       Site's description (string)
    keywords:          Site's keywords (string)
    email:             Instance of EmailSettings
    app_permissions:   Instance of ApplicationPermissions
    """
    def __init__(self, title = None, subtitle = None, url = None,
                 keywords = None, description = None, email = None, app_permissions = None):
        self.title = title
        self.subtitle = subtitle
        self.url = url
        self.description = description
        if email is None:
            self.email = EmailSettings()
        else:
            self.email = email
        if app_permissions is None:
            self.app_permissions = ApplicationPermissions()
        else:
            self.app_permissions = app_permissions

    def to_json(self):
        dt_permissions = [{"dt_sid": k,
            "is_active": v.is_active,
            "access_level": v.access_level,
            "watermark_by_default": v.watermark_by_default,
            "w_access_level": v.w_access_level,
            "visible_paragraphs": v.visible_paragraphs,
            "default_expression": v.default_expression} for k, v in self.app_permissions.permissions.iteritems()]
        data = {
          "title": self.title,
          "subtitle": self.subtitle,
          "url": self.url,
          "description": self.description,
          "keywords": self.keywords,
          "email": {
            "email_from": self.email.email_from,
            "username": self.email.username,
            "password": self.email.password,
            "host": self.email.host,
            "port": self.email.port,
            "use_tls": self.email.use_tls
          },
          "app_permissions": {
            "registration_mode": self.app_permissions.registration_mode,
            "permissions": dt_permissions
          }
        }
        return simplejson.dumps(data)

    @staticmethod
    def from_json(json_str):
        data = simplejson.loads(json_str)
        setts = WebAppSettings()
        setts.title = data["title"]
        setts.subtitle = data["subtitle"]
        setts.url = data["url"]
        setts.description = data["description"]
        setts.keywords = data["keywords"]
        setts.email.email_from = data["email"]["email_from"]
        setts.email.username = data["email"]["username"]
        setts.email.password = data["email"]["password"]
        setts.email.host = data["email"]["host"]
        setts.email.port = data["email"]["port"]
        setts.email.use_tls = data["email"]["use_tls"]
        setts.app_permissions.registration_mode = data["app_permissions"]["registration_mode"]
        for prm in data["app_permissions"]["permissions"]:
            dp = DocumentPermissions(prm["dt_sid"])
            dp.is_active = prm["is_active"]
            dp.access_level = prm["access_level"]
            dp.watermark_by_default = prm["watermark_by_default"]
            dp.w_access_level = prm["w_access_level"]
            dp.visible_paragraphs = prm["visible_paragraphs"]
            dp.default_expression = prm["default_expression"]
            setts.app_permissions.permissions[dp.dt_sid] = dp
        return setts
