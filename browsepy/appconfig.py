import flask

class Config(flask.Config):
    """
    Custom configuration class for Flask that treats keys in a case-insensitive manner.
    
    All keys are automatically converted to uppercase, allowing access regardless of original casing.
    """

    def __init__(self, root, defaults=None):
        # Initialize with defaults converted to uppercase keys
        defaults = self.gendict(defaults) if defaults else {}
        super().__init__(root, defaults)

    @staticmethod
    def genkey(key):
        """
        Converts a key to uppercase if it's a string.

        :param key: The key to convert.
        :type key: str
        :return: Uppercase version of the key.
        :rtype: str
        """
        return key.upper() if isinstance(key, str) else key

    @classmethod
    def gendict(cls, data):
        """
        Converts all keys in a dictionary to uppercase.

        :param data: Dictionary to convert.
        :type data: dict
        :return: New dictionary with uppercase keys.
        :rtype: dict
        """
        return {cls.genkey(k): v for k, v in data.items()}

    def __getitem__(self, key):
        # Get item with case-insensitive key
        return super().__getitem__(self.genkey(key))

    def __setitem__(self, key, value):
        # Set item with case-insensitive key
        super().__setitem__(self.genkey(key), value)

    def __delitem__(self, key):
        # Delete item with case-insensitive key
        super().__delitem__(self.genkey(key))

    def get(self, key, default=None):
        # Get value for key with fallback if not found
        return super().get(self.genkey(key), default)

    def pop(self, key, *args):
        # Remove and return item for case-insensitive key
        return super().pop(self.genkey(key), *args)

    def update(self, *args, **kwargs):
        """
        Update the configuration with new values, treating all keys as case-insensitive.
        """
        super().update(self.gendict(dict(*args, **kwargs)))


class Flask(flask.Flask):
    """
    Custom Flask class that uses the case-insensitive Config class.
    """
    config_class = Config
