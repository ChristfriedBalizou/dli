from db import Database
from model.models import DBsession, User

import os
import json

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR_PATH, "jeamsql.ini")

'''
https://stackoverflow.com/a/7346105
'''
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)



@Singleton
class Auth(object):
    '''
    Authentication manager
    '''

    def __init__(self):

        self.session = {}
        self.database = Database(section="PPR-DECALOG",
                                 config_path=CONFIG_PATH)


    def is_connected(self, username):

        if username in self.session:
            return True
        return False


    def lookup_in_db(self, username):

        # prevent sql injection
        username = username.replace("'", "")

        json_str = (self.database
                   .select("select * from SYN_USER WHERE WSLOGIN='%s'" % username,
                           fmt="json"))

        obj = json.loads(json_str)

        if len(obj) == 0 :
            return None

        #take last in the list
        user = obj.pop()

        return User(username=user.get("WSLOGIN"),
                    first_name=user.get("NOM"),
                    last_name=user.get("PRENOM"),
                    email=user.get("EMAIL"))


    def logout(self, username):

        if self.is_connected(username):
            del self.session[username]


    def check_authentication(self, username, password):

        if self.is_connected(username):
            return True, self.session.get(username)

        sess = DBsession()

        user = (sess.query(User)
                    .filter_by(username=username)
                    .first())

        if user is None:
            user = self.lookup_in_db(username)

            if user is None:
                return False, None

            sess.add(user)

        if user.password_hash is None:
            user.has_password(password)
            sess.commit()

        if user.verify_password(password) is True:
            self.session[username] = user
            return True, user

        return False, None
