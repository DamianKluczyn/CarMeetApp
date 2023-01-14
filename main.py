import psycopg2
import bcrypt
import re
import os
from abc import ABC, abstractmethod
from typing import Dict



# Interface's
class User(ABC):
    @abstractmethod
    def get_state(self):
        pass

class State(ABC):
    @abstractmethod
    def change_state(self):
        pass

# Database Connection

class Database_connection:
    def __init__(self):
        self.con = psycopg2.connect(
            database='car_meet',
            user='postgres',
            password='admin'
        )
        self.cur = self.con.cursor()


# Functional classes

# Check if user with this login already exists
class User_exist(Database_connection):
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

# Check if user with this nick already exists
class Nick_exist(Database_connection):
    def __init__(self, nick):
        super().__init__()
        self._nick = nick

    def check(self) -> bool:
        self.cur.execute('select count(*) from "Account" where nick = %s;', (self.nick,))
        in_base = self.cur.fetchone()
        if (in_base[0] == 1):
            # nick exists
            return True
        # nick doesn't exist
        return False

# Check if password is strong (at least 8 letters, 1 capital, 1 number, 1 special char)
class Password_check():
    def check(self, password):
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            return True
        return False

# Hashes password using bcrypt algorithm
class Hash:
    def __init__(self, password) -> None:
        self._password = password.encode('utf-8')
        self._salt = bcrypt.gensalt()
        self._hashed_password = bcrypt.hashpw(self._password, self._salt).decode('utf-8')

    def get_hashed_password(self) -> str:
        return self._hashed_password


# States (Meet - wants to meet, No_meet - closed for meetings/offline
class Meet_state(State):
    def change_state(self):
        pass

class No_meet_state(State):
    def change_state(self):
        pass

# Login user from database
class Login(Database_connection):
    def __init__(self) -> None:
        self._login = ""
        self._password = ""
        super().__init__()

    def getLogin(self) -> str:
        return self._login

    def sign(self) -> bool:
        self.cur.execute('select password from "Account" where login = %s;', (self._login,))
        rows = self.cur.fetchone()
        if (bcrypt.checkpw(self._password.encode('utf-8'), rows[0].encode('utf-8')) == True):
            # login successfully
            return True
        # login failed
        return False


# Register user in database
class Register(Database_connection):
    def __init__(self) -> None:
        self._login, self._password, self._nick, self._state = "", "", "", No_meet_state
        #TODO zmiana parametrow
        super().__init__()

    def register(self, login, password, nick) -> None:
        self._login = login
        self._password = password
        self._nick = nick
        self.cur.execute('insert into "Account" (login, password, nick, state) values (%s, %s, %s, "no_meet_state");',
                            (self._login, self._passw.get_hashed_password(), self._fname, self._lname))
        self.con.commit()


class Logged_user(User):
    def __init__(self, login, state: State):
        self._login = login
        self._state = state

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
        while(True):
            login = str(input("Login: "))
            password = str(input("Password: "))
            nick = str(input("Nick: "))
            if(not User_exist(login).check()):
                if(not Nick_exist(nick).check()):
                    if(Password_check.check(password)):
                        password = Hash(password).get_hashed_password()
                        Register.register(login, password, nick)
                        print("Registered successfully!")
                        break;
                    else:
                        print("Register failed!\nPassword too weak! - use at least 8 letters, 1 capital, 1 number, 1 special char.")
                else:
                    print("Register failed!\nNick already exists!")
            else:
                print("Register failed!\n User with this login already exists")
            input("Press Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')


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

class Login_menu:
    pass

class Logged_menu:
    pass