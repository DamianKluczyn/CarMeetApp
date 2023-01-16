import psycopg2
import bcrypt
import re
import os
from abc import ABC, abstractmethod

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


# Interface's
class User(ABC):
    @abstractmethod
    def get_state(self):
        pass

class State(ABC):
    @abstractmethod
    def change_state(self, login: str, db: Database_connection):
        pass

# Functional classes

# Check if user with this login already exists
class User_exist():
    def __init__(self, login: str, db: Database_connection) -> None:
        self._login = login
        self._db = db

    def check(self) -> bool:
        self._db.cur.execute('select count(*) from "Account" where login = %s;', (self._login,))
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
        self._db.cur.execute('select count(*) from "Account" where nick = %s;', (self._nick,))
        in_base = self._db.cur.fetchone()
        if (in_base[0] == 1):
            # nick exists
            return True
        # nick doesn't exist
        return False

# Check if password is strong (at least 8 letters, 1 capital, 1 number, 1 special char)
class Password_check():
    def check(self, password: str) -> bool:
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+!*()_\-=]{8,}', password):
            return True
        return False

# Hashes password using bcrypt algorithm
class Hash():
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
    def change_state(self, login: str, db: Database_connection) -> None:
        print("Changing to no meet state...")
        db.cur.execute(
            'UPDATE "Account" '
            'SET state = (%s) '
            'WHERE "Account".login = (%s)',
            (False, login))
        db.con.commit()


class No_meet_state(State):
    def change_state(self, login: str, db: Database_connection) -> None:
        print("Changing to meet state...")
        db.cur.execute(
            'UPDATE "Account" '
            'SET state = (%s) '
            'WHERE "Account".login = (%s)',
            (True, login))
        db.con.commit()


# Database user classes

# Login user from database
class Login(User):
    def __init__(self, login: str, password: str, db: Database_connection) -> None:
        self._login = login
        self._password = password
        self._db = db

    def get_login(self) -> str:
        return self._login

    def get_state(self) -> State:
        self._db.cur.execute('select state from "Account" where login = %s;', (self._login,))
        rows = self._db.cur.fetchone()
        if (rows[0] == False):
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
        self._login, self._password, self._nick, self._state = "", "", "", False
        self._db = db

    def register(self, login: str, password: str, nick: str) -> None:
        self._login = login
        self._password = password
        self._nick = nick
        self._db.cur.execute('insert into "Account" (login, password, nick, state) values (%s, %s, %s, %s);',
                            (self._login, self._password, self._nick, self._state))
        self._db.con.commit()

# Class represents logges user
class Logged_user(User):
    def __init__(self, login: str, state: State, db: Database_connection) -> None:
        self._login = login
        self._state = state
        self._db = db

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

    def change_state(self) -> None:
        if isinstance(self.get_state(), Meet_state):
            Meet_state().change_state(self._login, self._db)
        else:
            No_meet_state().change_state(self._login, self._db)

# Class represents car based
class Car():
    def __init__(self, db: Database_connection) -> None:
        self._db = db

    def add_car_to_user(self, brand: str, model: str, login: str) -> None:
        self._db.cur.execute(
            'UPDATE "Account" '
            'SET id_car = (Select id_car FROM "Car" WHERE brand = (%s) and model = (%s)) '
            'WHERE "Account".login = (%s)',
            (brand, model, login))
        self._db.con.commit()


    def add_car_to_db(self, brand: str, model: str) -> None:
        self._db.cur.execute('insert into Car (brand, model) values (%s, %s);',
                             (brand, model))
        self._db.con.commit()

    def change_car(self, brand: str, model: str, login: str) -> None:

        self._db.cur.execute(
            'UPDATE "Account" '
            'SET id_car = (Select id_car FROM "Car" WHERE brand = (%s) and model = (%s)) '
            'WHERE "Account".login = (%s)',
            (brand, model, login))
        self._db.con.commit()

class Meet():
    def __init__(self, user: Logged_user, db: Database_connection) -> None:
        self._db = db
        self._user = user

    def meet_count(self, city: str) -> None:
        self._db.cur.execute(
            'select L.name, count(A.id_account) '
            'from "Location" L '
            'left JOIN "Account" A on L.id_location = A.id_location '
            'where L.city = (%s) group by L.name;', (city,))
        in_base = self._db.cur.fetchall()
        for row in in_base:
            print(row[0],"- ", row[1])

    def meet_user(self, city: str, name: str) -> None:
        self._db.cur.execute(
            'UPDATE "Account" '
            'SET id_location = (select id_location from "Location" where city = (%s) and name = (%s))'
            'WHERE "Account".login = (%s)',
            (city, name, self._user.get_login()))
        self._db.con.commit()


# Proxy - check the input and call class with
class Proxy():
    def __init__(self, db: Database_connection) -> None:
        self._db = db
    def login_proxy(self) -> Logged_user:
        while(True):
            login = str(input("Login: "))
            password = str(input("Password: "))
            if(User_exist(login, self._db).check()):
                if(Login(login, password, self._db).sign()):
                    print("Login successfull!")
                    Clear_terminal()
                    return Logged_user(login, Login(login, password, self._db).get_state(), self._db)
                else:
                    print("Wrong password!")
            else:
                print("User does not exists!")

    def register_proxy(self) -> None:
        while(True):
            login = str(input("Login: "))
            password = str(input("Password: "))
            nick = str(input("Nick: "))
            if(not User_exist(login, self._db).check()):
                if(not Nick_exist(nick, self._db).check()):
                    if(Password_check().check(password)):
                        password = Hash(password).get_hashed_password()
                        Register(self._db).register(login, password, nick)
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
            Car(self._db).add_car_to_user(brand, model, user.get_login())
            print("Car added/changed successfully!")
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
            Car(self._db).add_car_to_db(brand, model)
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
            Car(self._db).change_car(brand, model, user.get_login())
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
        if(Password_check().check(password)):
            password = Hash(password).get_hashed_password()
            user.change_password(password)
            print("Password changed successfully!")
        else:
            print("Password too weak!")


    def change_nick_proxy(self, user: Logged_user) -> None:
        nick = str(input("New nick: "))
        if(not Nick_exist(nick, self._db).check()):
            user.change_nick(nick)
            print("Nick changed successfully!")
            return
        print("User with that nick already exists!")
        return

    def add_location_proxy(self) -> None:
        city = str(input("City: "))
        name = str(input("Location name: "))
        self._db.cur.execute('select count(*) from "Location" where city = %s and name = %s;', (city, name))
        in_base = self._db.cur.fetchone()
        if (in_base[0] != 0):
            self._db.cur.execute('insert into Location (city, name) values (%s, %s);',
                                 (city, name))
            self._db.con.commit()
            print("Location added successfully!")
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        print("Location already in database!")
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    def meet(self, user: Logged_user) -> None:
        self._db.cur.execute('select city, count(*) from "Location" group by city;')
        in_base = self._db.cur.fetchall()
        print("Available cities: ")
        cities = list()
        for row in in_base:
            cities.append(row[0])
            print(row[0], end=', ')
        city = str(input("\nInsert city: "))
        if city in cities:
            Meet(user, self._db).meet_count(city)
            self._db.cur.execute('select name from "Location" where city = (%s);', (city,))
            in_base = self._db.cur.fetchall()
            names = []
            for row in in_base:
                names.append(row[0])
            names = list(dict.fromkeys(names))
            name = str(input("\nInsert your location:"))
            if name in names:
                Meet(user, self._db).meet_user(city, name)
            else:
                print("Wrong location!")
        else:
            print("Wrong city!")

class View:
    def __init__(self, db: Database_connection):
        self._db = db

    def view_cars(self) -> None:
        self._db.cur.execute('select * from "Car";')
        in_base = self._db.cur.fetchall()
        for row in in_base:
            print("Brand: ", row[1], ", Model: ", row[2])
        Clear_terminal()

    def view_locations(self) -> None:
        self._db.cur.execute('select * from "Location";')
        in_base = self._db.cur.fetchall()
        for row in in_base:
            print("City: ", row[1], ", Name: ", row[2])
        Clear_terminal()

class Login_menu:
    def __init__(self, db: Database_connection) -> None:
        self.choice = ""
        self._db = db

    def start(self) -> None:
        print("LOGIN MENU")
        while True:
            self.choice = int(input("""
            Choose an option:
            1. Login
            2. Register
            0. Exit
            """))
            if self.choice == 1:
                user = Proxy(self._db).login_proxy()
                if isinstance(user.get_state(), Meet_state):
                    Meet_menu(user, self._db).start()
                    break
                else:
                    No_meet_menu(user, self._db).start()
                    break
            elif self.choice == 2:
                Proxy(self._db).register_proxy()
            elif self.choice == 0:
                print("Exiting program...")
                Clear_terminal()
                break


class User_settings:
    def __init__(self, user: Logged_user, db: Database_connection) -> None:
        self._user = user
        self._db = db
        self.choice = ""

    def start(self) -> None:
        print("Logged user menu")
        while True:
            self.choice = int(input("""
            Choose an option:
            1. Add/change your car
            2. Change password
            3. Change nick
            4. Add car to database
            5. Add locations to database
            0. Back
            """))
            if self.choice == 1:
                Proxy(self._db).add_car_to_user_proxy(self._user)
            elif self.choice == 2:
                Proxy(self._db).change_password_proxy(self._user)
            elif self.choice == 3:
                Proxy(self._db).change_nick_proxy(self._user)
            elif self.choice == 4:
                Proxy(self._db).add_car_to_db_proxy()
            elif self.choice == 5:
                Proxy(self._db).add_location_proxy()
            elif self.choice == 0:
                print("Going back...")
                Clear_terminal()
                break
            else:
                print("Wrong option!")

class Meet_menu:
    def __init__(self, user: Logged_user, db: Database_connection) -> None:
        self._db = db
        self._user = user
    def start(self):
        print("Meet Menu")
        while True:
            self.choice = int(input("""
                    Choose an option:
                    1. Meet
                    2. View locations
                    3. View cars
                    4. Settings
                    5. Change state
                    0. Exit
                    """))
            if self.choice == 1:
                Proxy(self._db).meet(self._user)
            elif self.choice == 2:
                View(self._db).view_locations()
            elif self.choice == 3:
                View(self._db).view_cars()
            elif self.choice == 4:
                User_settings(self._user, self._db).start()
            elif self.choice == 5:
                self._user.change_state()
                No_meet_menu(self._user, self._db).start()
                break
            elif self.choice == 0:
                print("Exiting program...")
                Clear_terminal()
                break

class No_meet_menu():
    def __init__(self, user: Logged_user, db: Database_connection) -> None:
        self._db = db
        self._user = user

    def start(self):
        print("No Meet Menu")
        while True:
            self.choice = int(input("""
                    Choose an option:
                    1. Change state
                    2. View locations
                    3. View cars
                    4. Settings
                    0. Exit
                    """))
            if self.choice == 1:
                self._user.change_state()
                Meet_menu(self._user, self._db).start()
                break
            elif self.choice == 2:
                View(self._db).view_locations()
            elif self.choice == 3:
                View(self._db).view_cars()
            elif self.choice == 4:
                User_settings(self._user, self._db).start()
            elif self.choice == 0:
                print("Exiting program...")
                Clear_terminal()
                break


def main():
    db = Database_connection()
    Login_menu(db).start()

if __name__ == "__main__":
    main()