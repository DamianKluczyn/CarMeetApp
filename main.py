import psycopg2
import bcrypt
from abc import ABC, abstractmethod
from typing import Dict

class User(ABC):
    @abstractmethod
    def get_state(self):
        pass

class Database_connection:
    def __init__(self):
        self.con = psycopg2.connect(
            database='car_meet',
            user='postgres',
            password='admin'
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
            # user exists
            return True
        # user doesn't exist
        return False

class Login(Database_connection):
    def __init__(self):
        self._login = ""
        self._passw = ""
        super().__init__()

    def getLogin(self) -> str:
        return self._login

    def sign(self) -> bool:
        self.cur.execute('select password from "Account" where login = %s;', (self._login,))
        rows = self.cur.fetchone()
        if (bcrypt.checkpw(self._passw.encode('utf-8'), rows[0].encode('utf-8')) == True):
            # login successfully
            return True
        # login failed
        return False

class Register:
    def __init__(self):
        self._login, self._password, self._nick, self._state = "", "", "", No_meet_state
        #TODO zmiana parametrow
        super().__init__()

    def register(self, login, password, nick) -> bool:
        self._login = login
        self._password = password
        self._nick = nick
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

class Logged_user(User):
    def __init__(self, login):
        self._login = login

    def get_login(self) -> str:
        return self._login

    def get_state(self):
        pass

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

class IFlyweight(ABC):
    @abstractmethod
    def getState(self, unique_state) -> str:
        pass

class Flyweight(IFlyweight):
    def __init__(self, shared_state: str) -> None:
        self._shared_state = shared_state
        print("Flyweight innit")

    def getState(self, unique_state) -> str:
        return f"Shared state: {self._shared_state}, Unique state: {unique_state}"

class Flyweight_factory:
    _flyweights: Dict[str, Flyweight] = {}

    def __init__(self, initial_flyweights: Dict) -> None:
        for state in initial_flyweights:
            self._flyweights[self.getKey(state)] = Flyweight(state)

    def getKey(self, state: Dict) -> str:
        return "_".join(sorted(state))

    def getFlyweight(self, shared_state: Dict) -> Flyweight:
        key = self.getKey(shared_state)
        if not self._flyweights.get(key):
            print("Creating new flyweight")
            self._flyweights[key] = Flyweight(key)
        else:
            print("Using existing flyweight")

        return self._flyweights[key]

class Proxy(User):
    def __init__(self) -> None:
        pass
    def login_proxy(self):
        pass
    def register_proxy(self):
        pass
    def add_car_proxy(self):
        # TODO flyweight
        pass
    def change_car_proxy(self):
        # TODO flyweight
        pass
    def change_password_proxy(self):
        pass
    def change_nick_proxy(self):
        pass
    def add_location_proxy(self):
        # TODO flyweight
        pass
    def get_state(self):
        pass
    '''
    def addSubject(self, factory: Flyweight_factory) -> None:
        print("Proxy add subject")
        flyweight = factory.getFlyweight([self._first_name])
        flyweight.getState([self._last_name, self._latitude, self._longitude])
        #self._real_subject = RealSubject(flyweight, self._last_name, self._latitude, self._longitude)
    
    def getState(self) -> str:
        return self._real_subject.getState()
    '''

class State(ABC):
    @abstractmethod
    def change_state(self):
        pass

class Meet_state(State):
    def change_state(self):
        pass

class No_meet_state(State):
    def change_state(self):
        pass

class Login_menu:
    pass

class Logged_menu:
    pass