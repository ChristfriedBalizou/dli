from db import Database
from models import DBsession, User

import os

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR_PATH, "jeamsql.ini")

class Auth(object):


    def __init__(self):

        self.session = {}
        self.database = Database(section="PPR-DECALOG",
                                 config_path=CONFIG_PATH)


    def is_connected(self, username):

        if username in self.session:
            return True
        return False


    def lookup_in_db(self, username):

        obj = (self.database
                   .select("select * from SYN_USER WHERE WSLOGIN='%s'" % username))

        if len(obj) == 0 :
            return None

        user = obj[0]

        return User(username=user.WSLOGIN,
                    first_name=user.NOM,
                    last_name=user.PRENOM,
                    email=user.EMAIL)


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
            sess.add(user)

        if user.password_hash is None:
            user.has_password(password)
            sess.commit()

        if user.verify_password(password) is True:
            self.session[username] = user
            return True, user

        return False, None
