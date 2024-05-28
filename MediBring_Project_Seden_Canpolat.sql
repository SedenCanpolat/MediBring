CREATE DATABASE MediBring_Project_Seden_Canpolat;
USE MediBring_Project_Seden_Canpolat;

CREATE TABLE Customers (
  Customer_ID int NOT NULL AUTO_INCREMENT,
  First_Name varchar(50),
  Last_Name varchar(50),
  Email varchar(50),
  Address varchar(70),
  Telephone_Number varchar(10),
  PRIMARY KEY (Customer_ID)
);

CREATE TABLE Companies (
  Company_ID int NOT NULL AUTO_INCREMENT,
  Address varchar(70),
  Name varchar(50),
  Telephone_Number varchar(10),
  PRIMARY KEY (Company_ID)
);


CREATE TABLE Medicines (
  Medicine_ID int NOT NULL AUTO_INCREMENT,
  Company_ID int,
  Title varchar(50),
  Price int,
  PRIMARY KEY (Medicine_ID),
  FOREIGN KEY (Company_ID) REFERENCES Companies (Company_ID)
);

CREATE TABLE Carts (
  Cart_ID int NOT NULL AUTO_INCREMENT,
  Customer_ID int,
  Medicine_ID int,
  Price int,
  Quantity int,
  Shopping_Date varchar(10),
  Urgent int,
  PRIMARY KEY (Cart_ID)
);

DROP TABLE Customers;
DROP TABLE Medicines;
DROP TABLE Companies;
DROP TABLE Carts;

INSERT INTO Customers (First_Name, Last_Name, Email, Address, Telephone_Number) VALUES ("Elsa", "Snow", "elsasnowemail", "Finland", "5364562141");
INSERT INTO Customers (First_Name, Last_Name, Email, Address, Telephone_Number) VALUES ("Elmas", "Snow", "elmassnowemail", "Finland", "5364564558");
INSERT INTO Customers (First_Name, Last_Name, Email, Address, Telephone_Number) VALUES ("Adrea", "Sun", "adreasunemail", "Sweden", "5556898437");


INSERT INTO Companies (Address, Name, Telephone_Number) VALUES ("Istanbul", "Vem", "2183648123");
INSERT INTO Medicines (Company_ID, Title, Price) VALUES ("1", "Hyonat", "50");

INSERT INTO Companies (Address, Name, Telephone_Number) VALUES ("Istanbul", "Abdiibrahim", "2180547125");
INSERT INTO Medicines (Company_ID, Title, Price) VALUES ("2", "Fucidin", "60");

INSERT INTO Companies (Address, Name, Telephone_Number) VALUES ("Almanya", "Merck", "2183645648");
INSERT INTO Medicines (Company_ID, Title, Price) VALUES ("3", "İliadin", "30");

INSERT INTO Companies (Address, Name, Telephone_Number) VALUES ("İstanbul", "Bayer", "2198364599");
INSERT INTO Medicines (Company_ID, Title, Price) VALUES ("4", "Rennie", "40");

INSERT INTO Medicines (Company_ID, Title, Price) VALUES ("4", "Coraspirin", "20");


select * from Companies;
select * from Medicines;
 
select * from Customers;
select * from Carts; #empty from the beginning please add it from the project 
