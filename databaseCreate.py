import sqlite3

db_conn = sqlite3.connect('database.db')
db_cursor = db_conn.cursor()

''''def create_customer_table():
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Customer_First_Name TEXT NOT NULL,
            Customer_Last_Name TEXT NOT NULL,
            Customer_Email TEXT NOT NULL UNIQUE,
            Customer_Password TEXT NOT NULL
        )
    """)
'''

'''
def create_employee_table():
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            Employee_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Employee_First_Name TEXT NOT NULL,
            Employee_Last_Name TEXT NOT NULL,
            Employee_Email TEXT NOT NULL UNIQUE,
            Employee_Password TEXT NOT NULL
        )
    """)
'''

def create_bowling_reservation_table():
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS bowling_reservation (
            Bowling_Reservation_ID INTEGER PRIMARY KEY,
            Customer_ID INTEGER NOT NULL,
            --  Customer ID is Automatically Assigned
            Bowling_Reservation_Date TEXT NOT NULL,
            Bowling_Reservation_StartTime TEXT NOT NULL,
            Bowling_Reservation_EndTime TEXT NOT NULL,
            -- End Time is Automatically Assigned
            Bowling_Reservation_NumberofPeople INT NOT NULL,
            Bowling_Reservation_SpecialRequest TEXT,
            Lane_ID INTEGER NOT NULL, 
            --  Lane ID is Automatically Assigned
            FOREIGN KEY(Customer_ID) REFERENCES customer(Customer_ID)
        )
    """)

def create_restaurant_reservation_table():
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_reservation (
            Restaurant_Reservation_ID INTEGER PRIMARY KEY,
            Customer_ID INTEGER NOT NULL,
            -- Customer ID is Automatically Assigned
            Restaurant_Reservation_Date TEXT NOT NULL,
            Restaurant_Reservation_StartTime TEXT NOT NULL,
            Restaurant_Reservation_EndTime TEXT NOT NULL,
            -- End Time is Automatically Assigned
            Restaurant_Reservation_NumberofPeople INT NOT NULL,
            Restaurant_Reservation_SpecialRequest TEXT,
            Table_ID INTEGER NOT NULL,
            --  Table ID is Automatically Assigned
            FOREIGN KEY(Customer_ID) REFERENCES customer(Customer_ID)
        )
    """)

def create_accommodation_reservation_table():
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS accommodation_reservation (
            Accommodation_Reservation_ID INTEGER PRIMARY KEY,
            Customer_ID INTEGER NOT NULL,
            -- Customer ID is Automatically Assigned
            Accommodation_Reservation_Date TEXT NOT NULL,
            Accommodation_Reservation_StartTime TEXT NOT NULL,
            Accommodation_Reservation_EndTime TEXT NOT NULL, 
            -- End Time is Automatically Assigned
            Accommodation_Reservation_NumberofPeople INT NOT NULL,
            Accommodation_Reservation_Roomtype TEXT,
            Room_ID INTEGER NOT NULL,
            -- Room ID is Automatically Assigned
            FOREIGN KEY(Customer_ID) REFERENCES customer(Customer_ID)
        )
    """)

'''
def insert_sample_data():
    db_cursor.execute("""
        INSERT INTO customer (Customer_First_Name, Customer_Last_Name, Customer_Email, Customer_Password)
        VALUES ('Bob', 'Kelly', 'bob.kelly@mail.com', 'bobkelly')
    """)
    db_cursor.execute("""
        INSERT INTO customer (Customer_First_Name, Customer_Last_Name, Customer_Email, Customer_Password)
        VALUES ('Alice', 'Smith', 'alice.smith@mail.com', 'alicesmith')
    """)
    db_cursor.execute("""
        INSERT INTO customer (Customer_First_Name, Customer_Last_Name, Customer_Email, Customer_Password)
        VALUES ('John', 'Doe', 'john.doe@mail.com', 'johndoe')
    """)
'''

# Call the functions to create tables
##create_customer_table()
##create_employee_table()
create_bowling_reservation_table()
create_restaurant_reservation_table()
create_accommodation_reservation_table()
##insert_sample_data()

# Commit changes and close connection
db_conn.commit()
db_conn.close()
