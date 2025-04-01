# import flask
# # import flask.config

# import pyodbc

# # from .compat import basestring


# class Config(flask.config.Config):
#     '''
#     Flask-compatible case-insensitive Config classt.

#     See :type:`flask.config.Config` for more info.
#     '''
#     def __init__(self, root, defaults=None):
#         if defaults:
#             defaults = self.gendict(defaults)
#         super(Config, self).__init__(root, defaults)

#     @classmethod
#     def genkey(cls, k):
#         '''
#         Key translation function.

#         :param k: key
#         :type k: str
#         :returns: uppercase key
#         ;rtype: str
#         '''
#         return k.upper() if isinstance(k, basestring) else k

#     @classmethod
#     def gendict(cls, *args, **kwargs):
#         '''
#         Pre-translated key dictionary constructor.

#         See :type:`dict` for more info.

#         :returns: dictionary with uppercase keys
#         :rtype: dict
#         '''
#         gk = cls.genkey
#         return dict((gk(k), v) for k, v in dict(*args, **kwargs).items())

#     def __getitem__(self, k):
#         return super(Config, self).__getitem__(self.genkey(k))

#     def __setitem__(self, k, v):
#         super(Config, self).__setitem__(self.genkey(k), v)

#     def __delitem__(self, k):
#         super(Config, self).__delitem__(self.genkey(k))

#     def get(self, k, default=None):
#         return super(Config, self).get(self.genkey(k), default)

#     def pop(self, k, *args):
#         return super(Config, self).pop(self.genkey(k), *args)

#     def update(self, *args, **kwargs):
#         super(Config, self).update(self.gendict(*args, **kwargs))


# class Flask(flask.Flask):
#     '''
#     Flask class using case-insensitive :type:`Config` class.

#     See :type:`flask.Flask` for more info.
#     '''
#     config_class = Config
import flask

class Config(flask.Config):
    # מחלקת תצורה מותאמת ל-Flask, אשר מתייחסת לשמות משתנים ללא תלות באותיות גדולות/קטנות.
    def __init__(self, root, defaults=None):
        defaults = self._gendict(defaults) if defaults else {}
        super().__init__(root, defaults)

    @staticmethod
    def _genkey(key):
        # הופך מפתחות לאותיות גדולות כדי למנוע תלות באותיות קטנות/גדולות. """
        return key.upper() if isinstance(key, str) else key

    @classmethod
    def _gendict(cls, data):
        # ממיר את כל מפתחות המילון לאותיות גדולות. """
        return {cls._genkey(k): v for k, v in data.items()}

    def __getitem__(self, key):
        return super().__getitem__(self._genkey(key))

    def __setitem__(self, key, value):
        super().__setitem__(self._genkey(key), value)

    def __delitem__(self, key):
        super().__delitem__(self._genkey(key))

    def get(self, key, default=None):
        return super().get(self._genkey(key), default)

    def pop(self, key, *args):
        return super().pop(self._genkey(key), *args)

    def update(self, *args, **kwargs):
        # מעדכן את התצורה תוך שמירה על מפתחות באותיות גדולות. """
        super().update(self._gendict(dict(*args, **kwargs)))


class Flask(flask.Flask):
    # הרחבה למחלקת Flask, כך שתשתמש במחלקת התצורה החדשה.
    config_class = Config
