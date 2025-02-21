import mysql.connector
from tabulate import tabulate
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="Sanket8787", 
            database="inventory_management"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"OOPS! Something went wrong! {err}")
        return None
def register_user():
    print("--- Register User---")
    username = input("Enter Username: ").strip()
    password = input("Enter Password: ").strip()
    role = input("Enter Role (admin/staff): ").strip().lower()

    # Validate inputs
    if not username or not password or role not in ['admin', 'staff']:
        print("Invalid input. Please enter valid username, password, and role (admin/staff).")
        return

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query_check = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query_check, (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                print("Username already exists. Please choose a different username.")
                return

            query_insert = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (username, password, role))
            connection.commit()
            print("-----------------------------------------------------")
            print(f" '{username}' registered successfully as {role}.")
            print("-----------------------------------------------------")
    except Exception as e:
        print(f"An error occurred: {e}")
def login():
    print("--- Login Page ---")
    username = input("Enter Username: ").strip()
    password = input("Enter Password: ").strip()
    role = input("Enter Role (admin/staff): ").strip()

    if not username or not password or not role:
        print("All fields are required!")
        return None

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
            cursor.execute(query, (username, password, role))
            user = cursor.fetchone()

            if user:
                print("-----------------------------------------------------")
                print(f"Login Successful! Welcome, {user['username']} ({user['role']}).")
                print("-----------------------------------------------------")
                return user
            else:
                print("Invalid credentials. Please try again.")
                return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
# Product add karnyache function 
def insert_product():
    print("=== Add Product ===")
    product_name = input("Enter Product Name: ").strip()
    quantity = int(input("Enter Quantity: "))
    price = float(input("Enter Price: "))
    low_stock_alert = int(input("Set a Limit for Low Stock Alert "))

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO products (product_name, quantity, price, low_stock_alert) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (product_name, quantity, price, low_stock_alert)) 
            connection.commit()
            print("Product added successfully!")
    except Exception as e:
        print(f"Error! Insert Product again: {e}")
        
def update_product():
    print("--- Update Product ---")
    product_id = int(input("Enter Product ID to Update: "))
    new_quantity = int(input("Enter New Quantity: "))
    new_price = float(input("Enter New Price: "))

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "UPDATE products SET quantity = %s, price = %s WHERE product_id = %s"
            cursor.execute(query, (new_quantity, new_price, product_id))
            connection.commit()
            if cursor.rowcount > 0:
                print("Product updated successfully!")
            else:
                print("No product found with the given ID.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
#delet product
def delete_product():
    print("--- Delete Product ---")
    product_id = int(input("Enter Product ID to Delete: "))

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "DELETE FROM products WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            connection.commit()
            if cursor.rowcount > 0:
                print("Product deleted successfully!")
            else:
                print("No product found with the given ID.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
#search the product
def search_product():
    print("--- Search Product ---")
    keyword = input("Enter Product Name or ID to Search: ").strip()

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM products WHERE product_name LIKE %s OR product_id = %s"
            cursor.execute(query, (f"%{keyword}%", keyword))
            products = cursor.fetchall()

            if products:
                print(tabulate(products, headers="keys", tablefmt="grid"))
            else:
                print("No products found matching the criteria.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
#seals ch record
def record_sale():
    print("--- Record Sale ---")
    product_id = int(input("Enter Product ID: "))
    quantity_sold = int(input("Enter Quantity Sold: "))

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            # Check if enough stock is available
            cursor.execute("SELECT quantity, price FROM products WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()

            if result:
                current_quantity, price = result
                if current_quantity >= quantity_sold:
                    total_amount = quantity_sold * price
                    cursor.execute("INSERT INTO transactions (product_id, transaction_type, quantity, amount) VALUES (%s, %s, %s, %s)",
                                   (product_id, 'sale', quantity_sold, total_amount))
                    cursor.execute("UPDATE products SET quantity = quantity - %s WHERE product_id = %s",
                                   (quantity_sold, product_id))
                    connection.commit()
                    print(f"Sale recorded successfully! Total Amount: {total_amount}")
                else:
                    print("Not enough stock available.")
            else:
                print("No product found with the given ID.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
#seals ch report
def generate_sales_report():
    print("--- Generate Sales Report ---")
    report_type = input("Enter Report Type (daily/weekly/monthly): ").strip()

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)

            if report_type == "daily":
                query = "SELECT * FROM transactions WHERE transaction_type = 'sale' AND DATE(transaction_date) = CURDATE()"
            elif report_type == "weekly":
                query = "SELECT * FROM transactions WHERE transaction_type = 'sale' AND YEARWEEK(transaction_date) = YEARWEEK(CURDATE())"
            elif report_type == "monthly":
                query = "SELECT * FROM transactions WHERE transaction_type = 'sale' AND MONTH(transaction_date) = MONTH(CURDATE())"
            else:
                print("Invalid report type.")
                return

            cursor.execute(query)
            sales = cursor.fetchall()

            if sales:
                print(tabulate(sales, headers="keys", tablefmt="grid"))
            else:
                print("No sales data found for the selected period.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
#main and brain of the code
def main():
    while True:
        print("\n--- Inventory Management System ---")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            user = login()
            if user:
                while True:
                    print(f"\n=== Welcome, {user['username']} ({user['role']}) ===")
                    if user['role'] == 'admin':
                        # Admin Menu
                        print("1. Add Product")
                        print("2. Update Product")
                        print("3. Delete Product")
                        print("4. Search Product")
                        print("5. Record Sale")
                        print("6. Generate Sales Report")
                        print("7. Register New User")
                        print("8. Logout")
                    elif user['role'] == 'staff':
                        # Staff Menu
                        print("1. Add Product")
                        print("2. Update Product")
                        print("3. Delete Product")
                        print("4. Search Product")
                        print("5. Record Sale")
                        print("6. Logout")

                    sub_choice = input("Enter your choice: ").strip()

                    if user['role'] == 'admin':
                        if sub_choice == "1":
                            insert_product()
                        elif sub_choice == "2":
                            update_product()
                        elif sub_choice == "3":
                            delete_product()
                        elif sub_choice == "4":
                            search_product()
                        elif sub_choice == "5":
                            record_sale()
                        elif sub_choice == "6":
                            generate_sales_report()
                        elif sub_choice == "7":
                            register_user()
                        elif sub_choice == "8":
                            print("Logging out...")
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    elif user['role'] == 'staff':
                        if sub_choice == "1":
                            insert_product()
                        elif sub_choice == "2":
                            update_product()
                        elif sub_choice == "3":
                            delete_product()
                        elif sub_choice == "4":
                            search_product()
                        elif sub_choice == "5":
                            record_sale()
                        elif sub_choice == "6":
                            print("Logging out...")
                            break
                        else:
                            print("Invalid choice. Please try again.")

        elif choice == "2":
            register_user()
        elif choice == "3":
            print("Exiting the system...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()