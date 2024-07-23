class User:
    def __init__(self, user_name, password, user_dni="", user_email=""):
        self._user_dni = user_dni
        self._user_name = user_name
        self._user_email = user_email
        self._password = password
