

# This file is only used to create the database tables and add some records for testing


import sqlite3

conn = sqlite3.connect("main.db")

curs = conn.cursor()

# Tables

# User table
curs.execute(
    """
    create table if not exists User (
    userID integer not null unique,
    firstname text not null,
    surname text not null,
    email text not null,
    phoneNumber text not null,
    addressLine text not null,
    townCity text not null,
    county text not null,
    postcode text not null,
    type text not null,
    password text,
    PRIMARY KEY("userID" AUTOINCREMENT)
    )
    """)

# Product table
curs.execute(
    """
    create table if not exists Product (
    productID integer not null unique,
    name text not null,
    company text not null,
    price real not null,
    desc text not null,
    type text not null,
    photoURL text,
    PRIMARY KEY("productID" AUTOINCREMENT)
    )
    """)

# Appliance table
curs.execute(
    """
    create table if not exists Appliance (
    applianceID integer not null unique,
    name text not null,
    avgWatts real not null,
    avgTime real not null,
    PRIMARY KEY("applianceID" AUTOINCREMENT)
    )
    """)

# Payment table
curs.execute(
    """
    create table if not exists Payment (
    paymentID integer not null unique,
    userID integer not null,
    nameOnCard text not null,
    number text not null,
    securityCode text not null,
    expiryDate text not null,
    PRIMARY KEY("paymentID" AUTOINCREMENT)
    FOREIGN KEY("userID") REFERENCES User ("userID")
    )
    """)

# Consultation table
curs.execute(
    """
    create table if not exists Consultation (
    consultID integer not null unique,
    userID integer not null,
    productID text not null,
    date text not null,
    time text not null,
    status text not null,
    PRIMARY KEY("consultID" AUTOINCREMENT),
    FOREIGN KEY("userID") REFERENCES User ("userID"),
    FOREIGN KEY("productID") REFERENCES Product ("productID")
    )
    """)

# Installation table
curs.execute(
    """
    create table if not exists Installation (
    installID integer not null unique,
    userID integer not null,
    productID text not null,
    paymentID text not null,
    date text not null,
    time text not null,
    status text not null,
    PRIMARY KEY("installID" AUTOINCREMENT),
    FOREIGN KEY("userID") REFERENCES User ("userID"),
    FOREIGN KEY("productID") REFERENCES Product ("productID"),
    FOREIGN KEY("paymentID") REFERENCES Payment ("paymentID")
    )
    """)

# ApplianceEnergyUsage table
curs.execute(
    """
    create table if not exists ApplianceEnergyUsage (
    usageID integer not null unique,
    userID integer not null,
    date text not null,
    appliance text not null,
    usage real not null,
    PRIMARY KEY("usageID" AUTOINCREMENT),
    FOREIGN KEY("userID") REFERENCES User ("userID")
    )
    """)


# Adding records

# adding user accounts
useracc = (
    ['John', 'Smith', 'john@smith.com', '07895631546', '12 Pleasant Drive', 'Manchester', 'Greater Manchester', 'M12 3DF'],
    ['Sarah', 'Olsen', 'saraholsen@gmail.com', '07382323458', '65 Park Road', 'Oldham', 'Greater Manchester', 'BL4 7RL']
    )

#curs.executemany("insert into User values (null,?,?,?,?,?,?,?,?,null)", useracc)   


# adding products

product = (
    ['Solar Panel 1', 'company 1', 1000.00, 'This is a description', 'Solarpanel'],
    ['Solar Panel 2', 'company 2', 1100.00, 'This is a description', 'Solarpanel'],
    ['Solar Panel 3', 'company 3', 1299.00, 'This is a description', 'Solarpanel'],
    ['EV charger 1', 'company 1', 99.99, 'This is a description', 'EVcharger'],
    ['EV charger 2', 'company 2', 149.99, 'This is a description', 'EVcharger'],
    ['EV charger 3', 'company 3', 89.99, 'This is a description', 'EVcharger'],
    ['Home EMS 1', 'company 1', 299.99, 'This is a description', 'HEMS'],
    ['Home EMS 2', 'company 2', 399.99, 'This is a description', 'HEMS'],
    ['Home EMS 3', 'company 3', 219.99, 'This is a description', 'HEMS']
)

#curs.executemany("insert into Product values (null,?,?,?,?,?,null)", product)

# adding test account
acc = ['Test', 'Account', 'test1@test.com', '07382323458', '65 Park Road', 'Oldham', 'Greater Manchester', 'BL4 7RL']


conn.commit()
