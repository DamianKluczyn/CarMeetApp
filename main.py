import psycopg2
import bcrypt
import re
import os
from abc import ABC, abstractmethod

# Interface's
class User(ABC):
    @abstractmethod
    def get_state(self):
        pass

class State(ABC):
    @abstractmethod
    def change_state(self):
        pass


# Database Connection - singleton

class Database_connection:
    __instance = None

    @staticmethod
    def get_connection():
        if Database_connection.__instance == None:
            Database_connection()
        return Database_connection.__instance

    def __init__(self) -> None:
        if Database_connection.__instance != None:
            raise Exception("Singleton cannot be instantiated more than once!")
        else:
            self.con = psycopg2.connect(
                database='car_meet',
                user='postgres',
                password='admin'
            )
            self.cur = self.con.cursor()


# Functional classes

# Check if user with this login already exists
class User_exist():
    def __init__(self, login: str, db: Database_connection) -> None:
        self._login = login
        self._db = db

    def check(self) -> bool:
        self._db.cur.execute('select count(*) from "Account" where login = %s;', (self.login,))
        in_base = self._db.cur.fetchone()
        if (in_base[0] == 1):
            # user exists
            return True
        # user doesn't exist
        return False

# Check if user with this nick already exists
class Nick_exist():
    def __init__(self, nick: str, db: Database_connection) -> None:
        self._nick = nick
        self._db = db

    def check(self) -> bool:
        self._db.cur.execute('select count(*) from "Account" where nick = %s;', (self.nick,))
        in_base = self._db.cur.fetchone()
        if (in_base[0] == 1):
            # nick exists
            return True
        # nick doesn't exist
        return False

# Check if password is strong (at least 8 letters, 1 capital, 1 number, 1 special char)
class Password_check():
    def check(self, password: str) -> bool:
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            return True
        return False

# Hashes password using bcrypt algorithm
class Hash:
    def __init__(self, password: str) -> None:
        self._password = password.encode('utf-8')
        self._salt = bcrypt.gensalt()
        self._hashed_password = bcrypt.hashpw(self._password, self._salt).decode('utf-8')

    def get_hashed_password(self) -> str:
        return self._hashed_password

def Clear_terminal() -> None:
    input("\nPress Enter to continue...")
    os.system('cls' if os.name == 'nt' else 'clear')


# States (Meet - wants to meet, No_meet - closed for meetings/offline
class Meet_state(State):
    def change_state(self):
        pass

class No_meet_state(State):
    def change_state(self):
        pass


# Database user classes

# Login user from database
class Login(User):
    def __init__(self, login: str, password: str, db: Database_connection) -> None:
        self._login = login
        self._password = password
        self._db = db

    def get_login(self) -> str:
        return self._login

    def get_state(self, state: str) -> State:
        self._db.cur.execute('select state from "Account" where login = %s;', (self._login,))
        rows = self._db.cur.fetchone()
        if (rows[0] == "no_meet_state"):
            return No_meet_state()
        return Meet_state()

    def sign(self) -> bool:
        self._db.cur.execute('select password from "Account" where login = %s;', (self._login,))
        rows = self._db.cur.fetchone()
        if (bcrypt.checkpw(self._password.encode('utf-8'), rows[0].encode('utf-8')) == True):
            # login successfully
            return True
        # login failed
        return False

# Register user in database
class Register():
    def __init__(self, db: Database_connection) -> None:
        self._login, self._password, self._nick, self._state = "", "", "", "no_meet_state"
        self._db = db

    def register(self, login: str, password: str, nick: str) -> None:
        self._login = login
        self._password = password
        self._nick = nick
        self._db.cur.execute('insert into Account (login, password, nick, state) values (%s, %s, %s, %s);',
                            (self._login, self._passw.get_hashed_password(), self._fname, self._lname))
        self._db.con.commit()

# Class represents logges user
class Logged_user(User):
    def __init__(self, login: str, state: State) -> None:
        self._login = login
        self._state = state

    def get_login(self) -> str:
        return self._login

    def get_state(self) -> State:
        return self._state

    def change_password(self, password: str) -> None:
        self._db.cur.execute(
            'UPDATE "Account" '
            'SET password = (%s) '
            'WHERE "Account".login = (%s)',
            (password, self._login))
        self._db.con.commit()
        return

    def change_nick(self, nick: str) -> None:
        self._db.cur.execute(
            'UPDATE "Account" '
            'SET nick = (%s) '
            'WHERE "Account".login = (%s)',
            (nick, self._login))
        self._db.con.commit()
        return


class Car:
    def __init__(self, db: Database_connection) -> None:
        self._db = db

    def add_car_to_user(self, brand, model, login) -> None:
        self._db.cur.execute(
            'UPDATE "Account" '
            'SET id_car = (Select id_car FROM "Car" WHERE brand = (%s) and model = (%s)) '
            'WHERE "Account".login = (%s)',
            (brand, model, login))
        self._db.con.commit()

    def add_car_to_db(self, brand, model) -> None:
        self._db.cur.execute('insert into Car (brand, model) values (%s, %s);',
                             (brand, model))
        self._db.con.commit()

    def change_car(self, brand, model, login) -> None:
        self._db.cur.execute(
            'UPDATE "Account" '
            'SET id_car = (Select id_car FROM "Car" WHERE brand = (%s) and model = (%s)) '
            'WHERE "Account".login = (%s)',
            (brand, model, login))
        self._db.con.commit()

# Proxy - check the input and call class with
class Proxy():
    def __init__(self, db: Database_connection) -> None:
        self._db = db
    def login_proxy(self) -> Logged_user:
        while(True):
            login = str(input("Login: "))
            password = str(input("Password: "))
            if(User_exist(login).check()):
                if(Login(login, password).sign()):
                    print("Login successfull!")
                    Clear_terminal()
                    return Logged_user(login, Login(login, password).get_state())
                else:
                    print("Wrong password!")
            else:
                print("User does not exists!")


    def register_proxy(self) -> None:
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
                        Clear_terminal()
                        return
                    else:
                        print("Register failed!\nPassword too weak! - use at least 8 letters, 1 capital, 1 number, 1 special char.")
                else:
                    print("Register failed!\nNick already exists!")
            else:
                print("Register failed!\n User with this login already exists")
            Clear_terminal()
            return

    def add_car_to_user_proxy(self, user: Logged_user) -> None:
        brand = str(input("Brand: "))
        model = str(input("Model: "))
        self._db.cur.execute('select count(*) from "Car" where brand = %s and model = %s;', (brand, model))
        in_base = self._db.cur.fetchone()
        if (in_base[0] == 1):
            Car.add_car_to_user(brand, model, user.get_login())
            print("Car added successfully!")
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        print("Car isn't in database, add it before allocating!")
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    def add_car_to_db_proxy(self) -> None:
        brand = str(input("Brand: "))
        model = str(input("Model: "))
        self._db.cur.execute('select count(*) from "Car" where brand = %s and model = %s;', (brand, model))
        in_base = self._db.cur.fetchone()
        if (in_base[0] != 0):
            Car.add_car_to_db(brand, model)
            print("Car added successfully!")
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        print("Car already in database!")
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    def change_car_proxy(self, user: Logged_user) -> None:
        brand = str(input("Brand: "))
        model = str(input("Model: "))
        self._db.cur.execute('select count(*) from "Car" where brand = %s and model = %s;', (brand, model))
        in_base = self._db.cur.fetchone()
        if (in_base[0] == 1):
            Car.change_car(brand, model, user.get_login())
            print("Car added successfully!")
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        print("Car isn't in database, add it before allocating!")
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    def change_password_proxy(self, user: Logged_user) -> None:
        password = str(input("New Password: "))
        if (Password_check.check(password)):
            password = Hash(password).get_hashed_password()
            user.change_password(password)

    def change_nick_proxy(self, user: Logged_user) -> None:
        nick = str(input("New Password: "))
        if (not Nick_exist(nick, self._db)):
            user.change_nick(nick)
            print("Nick changed successfully!")
            return
        print("User with that nick already exists!")
        return

    def add_location_proxy(self) -> None:
        pass


class View:
    def __init__(self, db):
        self._db = db

    def view_cars(self) -> None:
        pass

    def view_locations(self) -> None:
        pass

class Login_menu:
    pass

class User_settings:
    pass

class Meet_menu:
    pass

class No_meet_menu:
    pass

def main():
    db = Database_connection()

if __name__ == "__main__":
    main()