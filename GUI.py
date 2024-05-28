from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
import MediBring
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class DeliveryWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(DeliveryWindow, self).__init__()
        self.mycursor = MediBring.mydb.cursor()
        self.window = uic.loadUi("Deliveryman.ui")

        self.window.allButton.clicked.connect(self.all_Orders)

        self.window.show()

    def all_Orders(self):
        try:
            self.mycursor.execute("""
                SELECT Customers.First_Name, Customers.Last_Name, Customers.Address, Customers.Telephone_Number,
                    Medicines.Title, Carts.Quantity, Carts.Urgent
                FROM Customers
                JOIN Carts ON Customers.Customer_ID = Carts.Customer_ID
                JOIN Medicines ON Carts.Medicine_ID = Medicines.Medicine_ID
                ORDER BY Customers.Customer_ID;
            """)
            results = self.mycursor.fetchall()

            if not results:
                print("No data found.")
                self.window.table.setRowCount(0)
                return

            self.window.table.setRowCount(len(results))
            self.window.table.setColumnCount(7) 
            self.window.table.setHorizontalHeaderLabels(["Name", "Surname", "Address", "Telephone", "Medicine Title", "Quantity", "Urgency"])

            for row_num, result_data in enumerate(results):
                for col_num, row_data in enumerate(result_data):
                    item = QTableWidgetItem(str(row_data))
                    self.window.table.setItem(row_num, col_num, item)
        except Exception as e:
            print(f"An error occurred: {e}")
            self.window.table.setRowCount(0)


        


class SellerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(SellerWindow, self).__init__()
        self.mycursor = MediBring.mydb.cursor()
        self.window = uic.loadUi("Seller.ui")

        self.window.addButton.clicked.connect(self.add_medicine)
        self.window.deleteButton.clicked.connect(self.delete_from_Medicine)

        self.window.historyButton.clicked.connect(self.Medicine_refresh)
        self.window.deleteButton_2.clicked.connect(self.clear_Medicine)

        self.Medicine_refresh()
        self.window.show()

    def add_medicine(self):
        title = self.window.cartLineEdit.text()
        company = self.window.cartLineEdit_2.text()
        price = self.window.cartLineEdit_3.text()
        quantity = self.window.cartLineEdit_4.text()

        self.mycursor.execute("""
        SELECT Medicine_ID, Title, Quantity
        FROM Medicines
        WHERE Title = %s AND Company_ID = (
            SELECT Company_ID FROM Companies WHERE Name = %s
        );
        """, (title, company))
        result = self.mycursor.fetchone()

        if result is not None: 
            Medicine_id, Medicine_title, current_quantity = result

            self.mycursor.execute("""
                UPDATE Medicines
                SET Quantity = Quantity + %s
                WHERE Medicine_ID = %s;
            """, (quantity, Medicine_id))
            MediBring.mydb.commit()

            self.update_cart()

        else: 
            self.mycursor.execute("""
                SELECT Company_ID
                FROM Companies
                WHERE Name = %s;
            """, (company,))
            company_result = self.mycursor.fetchone()

            if company_result is not None:
                company_id = company_result[0]
            else:
                self.mycursor.execute("""
                    INSERT INTO Companies (Name)
                    VALUES (%s);
                """, (company,))
                MediBring.mydb.commit()

                self.mycursor.execute("""
                    SELECT Company_ID
                    FROM Companies
                    WHERE Name = %s;
                """, (company,))
                company_result = self.mycursor.fetchone()
                company_id = company_result[0]
        
            self.mycursor.execute("""
                INSERT INTO Medicines (Company_ID, Title, Price, Quantity)
                VALUES (%s, %s, %s, %s);
            """, (company_id, title, price, quantity))
            MediBring.mydb.commit()

            self.update_Medicine()

    def update_Medicine(self):
        self.window.cart.setRowCount(0)
        self.window.cart.setColumnCount(4)
        self.window.cart.setHorizontalHeaderLabels(["Title", "Company", "Price", "Quantity"])

        self.mycursor.execute("""
            SELECT Medicines.Title, Companies.Name, Medicines.Price, Medicines.Quantity
            FROM Medicines
            JOIN Companies ON Medicines.Company_ID = Companies.Company_ID;
        """)
        medicines = self.mycursor.fetchall()

        self.window.cart.setRowCount(len(medicines))
        for row_idx, (title, company, price, quantity) in enumerate(medicines):
            self.window.cart.setItem(row_idx, 0, QTableWidgetItem(title))
            self.window.cart.setItem(row_idx, 1, QTableWidgetItem(company))
            self.window.cart.setItem(row_idx, 2, QTableWidgetItem(str(price)))
            self.window.cart.setItem(row_idx, 3, QTableWidgetItem(str(quantity)))


        total_quantity = self.get_total_quantity()
        if hasattr(self.window, 'countLabel2'):
            self.window.countLabel2.setText(f"Count of Medicines: {total_quantity}")


    def delete_from_Medicine(self):
        current_row = self.window.cart.currentRow()
        title_item = self.window.cart.item(current_row, 0)

        if title_item is not None:
            title = title_item.text()

            self.mycursor.execute("""
                DELETE FROM Carts
                WHERE Medicine_ID IN (
                    SELECT Medicine_ID FROM Medicines
                    WHERE Title = %s
                )
            """, (title,))
            MediBring.mydb.commit()

            self.mycursor.execute("""
                DELETE FROM Medicines
                WHERE Title = %s
            """, (title,))
            MediBring.mydb.commit()

            self.window.cart.removeRow(current_row)

            self.Medicine_refresh()

            if hasattr(self.window, 'countLabel2'):
                self.get_total_quantity()



    def clear_Medicine(self):
        self.mycursor.execute("DELETE FROM Medicines")
        MediBring.mydb.commit()
        self.window.cart.setRowCount(0)
        self.window.countLabel2.setText(f"Count of Medicines: 0")

        
          
    def Medicine_refresh(self):
        self.mycursor.execute("""
            SELECT Medicines.Title, Companies.Name, Medicines.Price, Medicines.Quantity
            FROM Medicines
            JOIN Companies ON Medicines.Company_ID = Companies.Company_ID;
        """)
        all_medicines = self.mycursor.fetchall()

        total = 0.0
        count = 0

        self.window.cart.setRowCount(len(all_medicines))
        self.window.cart.setColumnCount(4)
        self.window.cart.setHorizontalHeaderLabels(["Title", "Company", "Price", "Quantity"])

        for row_num, (Medicine_title, Company_name, Medicine_price, quantity) in enumerate(all_medicines):
            item_title = QTableWidgetItem(str(Medicine_title))
            item_company = QTableWidgetItem(str(Company_name))
            item_price = QTableWidgetItem(str(Medicine_price))
            item_quantity = QTableWidgetItem(str(quantity))

            self.window.cart.setItem(row_num, 0, item_title)
            self.window.cart.setItem(row_num, 1, item_company)
            self.window.cart.setItem(row_num, 2, item_price)
            self.window.cart.setItem(row_num, 3, item_quantity)

            total += float(Medicine_price) * int(quantity)
            count += int(quantity)


        if hasattr(self.window, 'countLabel2'):
            self.window.countLabel2.setText(f"Total Items: {count}")

    def setup_ui(self):
        self.cart_refresh()

    def get_total_quantity(self):
        self.mycursor.execute("""
            SELECT SUM(Quantity) FROM Medicines;
        """)
        result = self.mycursor.fetchone()

        total_quantity = result[0] if result[0] is not None else 0
        return total_quantity    


class CustomerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(CustomerWindow, self).__init__()
        self.mycursor = MediBring.mydb.cursor()
        

        self.window = uic.loadUi("Customer.ui")

        self.window.searchButton.clicked.connect(self.search_Medicines)
        self.window.addButton.clicked.connect(self.add_cart)
        self.window.deleteButton.clicked.connect(self.delete_from_cart)
        self.window.allButton.clicked.connect(self.all_Medicines)
        self.window.historyButton.clicked.connect(self.cart_refresh)
        self.window.deleteButton_2.clicked.connect(self.clear_cart)
        self.window.addButton_2.clicked.connect(self.urgent_add)

        self.cart_refresh()

        self.window.show()
        
    total = 0.0
    count = 0

    def all_Medicines(self):
        self.mycursor.execute("""
            SELECT Medicines.Title, Companies.Name, Medicines.Price
            FROM Medicines
            JOIN Companies ON Medicines.Company_ID = Companies.Company_ID
        """)
        results = self.mycursor.fetchall()
        self.window.table.setRowCount(len(results))
        self.window.table.setColumnCount(len(results[0]))
        self.window.table.setHorizontalHeaderLabels(["Title", "Company", "Price"])
        for row_num, result_data in enumerate(results):
            for col_num, row_data in enumerate(result_data):
                item = QTableWidgetItem(str(row_data))
                self.window.table.setItem(row_num, col_num, item)

        self.agg_Cart()
        


    def search_Medicines(self):
        title = self.window.searchLineEdit.text()    
        self.mycursor.execute("""
            SELECT Medicines.Title, Companies.Name, Medicines.Price
            FROM Medicines
            JOIN Companies ON Medicines.Company_ID = Companies.Company_ID
            WHERE Medicines.Title = %s or Companies.Name = %s or Medicines.Price = %s
        """, (title, title, title))
        results = self.mycursor.fetchall()

        if len(results) == 0:
            results = "No Medicines found"
            self.window.table.setRowCount(1)
            self.window.table.setColumnCount(1)
            self.window.table.setHorizontalHeaderLabels(["Error"])
            item = QTableWidgetItem(str(results))
            self.window.table.setItem(0, 0, item)
            self.window.countLabel.setText(f"Count of Medicines: 0")   

        else:
            self.window.table.setRowCount(len(results))
            self.window.table.setColumnCount(len(results[0]))
            self.window.table.setHorizontalHeaderLabels(["Title", "Company", "Price"])
            for row_num, result_data in enumerate(results):
                for col_num, row_data in enumerate(result_data):
                    item = QTableWidgetItem(str(row_data))
                    self.window.table.setItem(row_num, col_num, item)

            self.mycursor.execute("""
                SELECT COUNT(*) FROM Medicines
                JOIN Companies ON Medicines.Company_ID = Companies.Company_ID
                WHERE Medicines.Title = %s or Companies.Name = %s  or Medicines.Price = %s
                """, (title, title, title))
            count = self.mycursor.fetchone()[0]
            self.window.countLabel.setText(f"Count of Medicines: {count}") 



    total = 0.0
    count = 0
    
    def add_cart(self):

        self.window.cart.setRowCount(self.window.cart.rowCount() + 1)
        self.window.cart.setColumnCount(3)
        self.window.cart.setHorizontalHeaderLabels(["Title", "Price", "Quantity"])

        self.cart_refresh()
        title = self.window.cartLineEdit.text()
        self.mycursor.execute("""
            SELECT Medicines.Medicine_ID, Medicines.Title, Medicines.Price
            FROM Medicines
            WHERE Medicines.Title = %s;    
        """, (title, ))
        result = self.mycursor.fetchone()
        self.mycursor.fetchall()

        if result is not None:
            Medicine_id, Medicine_title, Medicine_price = result
            self.mycursor.execute("""
            SELECT Carts.Medicine_ID
            FROM Carts
            WHERE Carts.Medicine_ID = %s;    
            """, (Medicine_id, ))
            result = self.mycursor.fetchone()

            if result is not None: #if the Medicine is already in the cart
                self.mycursor.execute(""" 
                    UPDATE Carts
                    SET Quantity = Quantity + 1
                    WHERE Medicine_ID IN (
                    SELECT Medicine_ID FROM Medicines
                    WHERE Medicines.Title = %s
                    );    
                """, (title, ))
                MediBring.mydb.commit()
                self.cart_refresh()

            else: #if the Medicine is not in the cart
                self.mycursor.execute("""
                    INSERT INTO Carts (Customer_ID, Medicine_ID, Price, Quantity, Shopping_Date, Urgent)
                    SELECT 1, Medicines.Medicine_ID, Medicines.Price, 1, CURRENT_DATE,0
                    FROM Medicines
                    WHERE Medicines.Title = %s;   
                """, (title, ))
                MediBring.mydb.commit()
                self.cart_refresh()

        else:
            self.window.cart.setRowCount(1)
            self.window.cart.setColumnCount(1)
            self.window.cart.setHorizontalHeaderLabels(["Error"])
            item = QTableWidgetItem("Medicine not found")
            self.window.cart.setItem(0, 0, item)
            self.window.countLabel2.setText(f"Count of Medicines: 0")

    def urgent_add(self):

        self.window.cart.setRowCount(self.window.cart.rowCount() + 1)
        self.window.cart.setColumnCount(3)
        self.window.cart.setHorizontalHeaderLabels(["Title", "Price", "Quantity"])

        self.cart_refresh()
        title = self.window.cartLineEdit.text()
        self.mycursor.execute("""
            SELECT Medicines.Medicine_ID, Medicines.Title, Medicines.Price
            FROM Medicines
            WHERE Medicines.Title = %s;    
        """, (title, ))
        result = self.mycursor.fetchone()
        self.mycursor.fetchall()

        if result is not None: 
            Medicine_id, Medicine_title, Medicine_price = result
            self.mycursor.execute("""
            SELECT Carts.Medicine_ID
            FROM Carts
            WHERE Carts.Medicine_ID = %s;    
            """, (Medicine_id, ))
            result = self.mycursor.fetchone()

            if result is not None: #if the Medicine is already in the cart
                self.mycursor.execute(""" 
                    UPDATE Carts
                    SET Quantity = Quantity + 1
                    WHERE Medicine_ID IN (
                    SELECT Medicine_ID FROM Medicines
                    WHERE Medicines.Title = %s
                    );    
                """, (title, ))
                MediBring.mydb.commit()
                self.cart_refresh()

            else: #if the Medicine is not in the cart
                self.mycursor.execute("""
                    INSERT INTO Carts (Customer_ID, Medicine_ID, Price, Quantity, Shopping_Date, Urgent)
                    SELECT 1, Medicines.Medicine_ID, Medicines.Price, 1, CURRENT_DATE,1
                    FROM Medicines
                    WHERE Medicines.Title = %s;   
                """, (title, ))
                MediBring.mydb.commit()
                self.cart_refresh()

        else:
            self.window.cart.setRowCount(1)
            self.window.cart.setColumnCount(1)
            self.window.cart.setHorizontalHeaderLabels(["Error"])
            item = QTableWidgetItem("Medicine not found")
            self.window.cart.setItem(0, 0, item)
            self.window.countLabel2.setText(f"Count of Medicines: 0")        
       

    def agg_Cart(self):
        self.mycursor.execute("SELECT COUNT(*) FROM Medicines")
        count = self.mycursor.fetchone()[0]
        self.window.countLabel.setText(f"Count of Medicines: {count}")

        self.mycursor.execute("SELECT COUNT(*) FROM Companies")
        Company_count = self.mycursor.fetchone()[0]
        self.window.authorLabel_2.setText(f"Company count: {Company_count: }")



    def refresh_agg_cart(self):
        self.mycursor.execute("SELECT AVG(Price) FROM Carts")
        avg_price_result = self.mycursor.fetchone()
        if avg_price_result[0] is not None:
            avg_price = avg_price_result[0]
            self.window.avgPriceLabel.setText(f"Average Price: {avg_price:.2f}")
        else:
            self.window.avgPriceLabel.setText(f"Average Price: 0")

        self.mycursor.execute("SELECT MIN(Price) FROM Carts")
        min_price_result = self.mycursor.fetchone()
        if min_price_result[0] is not None:
            min_price = min_price_result[0]
            self.window.minPriceLabel_2.setText(f"Min priced Medicine from cart: {min_price:.2f}")
        else:
            self.window.minPriceLabel_2.setText(f"Min priced Medicine from cart: 0")

        self.mycursor.execute("SELECT MAX(Price) FROM Carts")
        max_price_result = self.mycursor.fetchone()
        if max_price_result[0] is not None:
            max_price = max_price_result[0]
            self.window.maxPriceLabel_2.setText(f"Max priced Medicine from cart: {max_price:.2f}")
        else:
            self.window.maxPriceLabel_2.setText(f"Max priced Medicine from cart: 0")


    def refresh_total(self):
        self.window.totalBox.setText('Total: ' + str(self.total))

    def refresh_count(self):
        self.window.countLabel2.setText(f"Count of Medicines: {self.count}")


    def delete_from_cart(self):
        title_item = self.window.cart.item(self.window.cart.currentRow(), 0)
        quantity_item = self.window.cart.item(self.window.cart.currentRow(), 2)

        if title_item is not None and quantity_item is not None:
            title = title_item.text()
            quantity = int(quantity_item.text())

            deleted_Medicine_price_item = self.window.cart.item(self.window.cart.currentRow(), 1)
            deleted_Medicine_price = float(deleted_Medicine_price_item.text()) if deleted_Medicine_price_item is not None else 0.0

            self.mycursor.execute("""
                DELETE FROM Carts
                WHERE Medicine_ID IN (
                    SELECT Medicine_ID FROM Medicines
                    WHERE Title = %s
                )
            """, (title,))
            MediBring.mydb.commit()

            self.mycursor.execute("""
                SELECT COUNT(*) FROM Medicines
                WHERE Medicines.Title = %s
            """, (title,))
            
            count = self.mycursor.fetchone()[0]

            self.total -= deleted_Medicine_price * quantity
            self.refresh_total()

            self.count -= quantity

            if self.count == 0:
                self.window.countLabel2.setText(f"Count of Medicines: 0")
            else:
                self.refresh_count()
                
            self.refresh_agg_cart()         

            self.window.cart.removeRow(self.window.cart.currentRow())


    def clear_cart(self):
        self.mycursor.execute("DELETE FROM Carts")
        MediBring.mydb.commit()
        self.window.cart.setRowCount(0)
        self.window.countLabel2.setText(f"Count of Medicines: 0")
        self.refresh_agg_cart()
        self.window.totalBox.setText('Total: 0.0')

        
          
    def cart_refresh(self):
        self.mycursor.execute("""
            SELECT Medicines.Title, Medicines.Price, Carts.Quantity
            FROM Medicines 
            JOIN Carts ON Medicines.Medicine_ID = Carts.Medicine_ID  
        """)
        result = self.mycursor.fetchall()

        total = 0.0
        count = 0

        self.window.cart.setRowCount(len(result))
        self.window.cart.setColumnCount(3) 
        self.window.cart.setHorizontalHeaderLabels(["Title", "Price", "Quantity"])

        for row_num, (Medicine_title, Medicine_price, quantity) in enumerate(result):

            item_title = QTableWidgetItem(str(Medicine_title))
            item_price = QTableWidgetItem(str(Medicine_price))
            item_quantity = QTableWidgetItem(str(quantity))
            self.window.cart.setItem(row_num, 0, item_title)
            self.window.cart.setItem(row_num, 1, item_price)
            self.window.cart.setItem(row_num, 2, item_quantity)

            total += Medicine_price * quantity
            count += quantity
            

        self.total = total
        self.refresh_total()

        self.count = count
        self.refresh_count()

        self.refresh_agg_cart()
         
        


    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.mycursor = MediBring.mydb.cursor()

        self.window = uic.loadUi("Start.ui")
        self.window.sellerButton.clicked.connect(self.open_seller_window)
        self.window.deliveryButton.clicked.connect(self.open_delivery_window)
        self.window.customerButton.clicked.connect(self.open_customer_window)

        self.window.show()

    def open_seller_window(self):
        self.seller_window = SellerWindow()

    def open_delivery_window(self):
        self.delivery_window = DeliveryWindow()

    def open_customer_window(self):
        self.customer_window = CustomerWindow()           

    def show(self):
        self.window.show()

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()