import psycopg2
import bcrypt
from abc import ABC, abstractmethod

class Database_connection:
    def __init__(self):
        self.con = psycopg2.connect(
            database='car_meet',
            user='postgres',
            password='290e47'
        )
        self.cur = self.con.cursor()

class User_exist:
    def __init__(self, login):
        super().__init__()
        self._login = login

    def check(self) -> bool:
        self.cur.execute('select count(*) from "Account" where login = %s;', (self.login,))
        in_base = self.cur.fetchone()
        if (in_base[0] == 1):
            return False
        return True

class Login:
    def __init__(self):
        self._login = input("\nLogin: ").lower()
        self._passw = input("Password: ")
        # TODO przejscie przez proxy
        self._exist = False
        super().__init__()

    def getLogin(self) -> str:
        return self._login

    def sign(self) -> bool:
        self._exist = User_exist(self._login)
        if (not self._exist.check()):
            self.cur.execute('select password from "Account" where login = %s;', (self._login,))
            rows = self.cur.fetchone()
            if (bcrypt.checkpw(self._passw.encode('utf-8'), rows[0].encode('utf-8')) == True):
                return True
        return False

class Register:
    def __init__(self):
        self._login, self._passw, self._fname, self._lname, self._exist = " ", " ", " ", " ", " "
        #TODO zmiana parametrow
        super().__init__()

    def register(self) -> bool:
        self._login = input("\nLogin: ").lower()
        self._passw = input("Password: ")
        self._fname = input("First name: ").lower().capitalize()
        self._lname = input("Last name: ").lower().capitalize()
        self._exist = User_exist(self._login)
        #TODO przejscie przez proxy
        if (self._exist.check()):
            self._passw = hash(self._passw)
            self.cur.execute('insert into "Account" (login, password, fname, lname) values (%s, %s, %s, %s);',
                             (self._login, self._passw.get_hashed_password(), self._fname, self._lname))
            self.con.commit()
            print("\nUser registered succesfully!\n")
            return True
        print("\nRegistration failed!\n")
        return False

class Hash:
    def __init__(self, password):
        self._password = password.encode('utf-8')
        self._salt = bcrypt.gensalt()
        self._hashed_password = bcrypt.hashpw(self._password, self._salt).decode('utf-8')

    def get_hashed_password(self) -> str:
        return self._hashed_password

class Logged_user:
    def __init__(self, login):
        self._login = login

    def get_login(self) -> str:
        return self._login

class Car:
    def __init__(self, login):
        self._login = login
        self._brand = ""
        self._type = ""
        self._modded = False
        #TODO przejscie przez flyweight

    def add_car(self) -> bool:
        pass

    def change_car(self) -> bool:
        pass

class Proxy:
    pass

class IFlyweight(ABC):
    pass

class Flyweight(IFlyweight):
    pass

class Flyweight_factory:
    pass

class Meet_state:
    pass

class No_meet_state:
    pass

class Login_menu:
    pass

class Logged_menu:
    pass