
import json

import random

# Constants for file paths
PRODUCTS_FILE = "products.json"
SELLERS_FILE = "sellers.json"
BUYERS_FILE = "buyers.json"
SMS_FILE = "sms.json"

# User Management Class
class UserManagement:
    def __init__(self, user_file):
        self.user_file = user_file
        self.users = self.load_users()

    def load_users(self):
        try:
            with open(self.user_file, "r") as file:
                data = file.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except FileNotFoundError:
            return []

    def save_users(self, users):
        with open(self.user_file, "w") as file:
            json.dump(users, file, indent=4)

    def find_user(self, username):
        users = self.load_users()
        return next((user for user in users if user["username"] == username), None)

    def register_user(self, username, password):
        users = self.load_users()  # Load existing users
        if self.find_user(username):
            print("Username already exists. Please try a different one.")
            return False
        if not self.is_password_strong(password):
            print("Password is not strong. It should be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
            return False
        users.append({"username": username, "password": password})  # Add new user
        self.save_users(users)  # Save updated list
        self.users = users  # Update in-memory list
        print("Sign up successful!")
        return True
    
    def send_sms_code(self, username):
        user = self.find_user(username)
        if user:
            sms_manager = SMSManager(SMS_FILE)
            sms_code = sms_manager.generate_sms_code(username)
            user["sms_code"] = sms_code  # Add the SMS code to the user dictionary
            self.save_users(self.users)  # Save updated user data back to the file
            print(f"SMS code sent to {username}. Code: {sms_code}")
        else:
            print(f"User {username} not found.")

    def authenticate_user(self, username, password, sms_code=None):
        users = self.load_users()  # Load the latest user data
        user = next((u for u in users if u["username"] == username), None)
        if user:
            if user["password"] == password:
                if sms_code:  # Check SMS code only if provided
                    sms_manager = SMSManager(SMS_FILE)
                    if not sms_manager.verify_sms_code(username, sms_code):
                        print("Invalid SMS code.")
                        return False
                return True  # Authentication successful
            else:
                print("Invalid password.")
        else:
            print("User not found.")
        return False
    def is_password_strong(self, password):
        if len(password) < 8 or not any(char.isupper() for char in password) or \
            not any(char.islower() for char in password) or not any(char.isdigit() for char in password) or \
            not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
            return False
        return True

# Product Class
class Product:
    def __init__(self, name, price, stock, category="Uncategorized" , seller_id = None):
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.seller_id = seller_id

    def is_available(self):
        if self.stock == 0:
            return "this product is out of stock"
        return self.stock > 0

    def purchase(self, quantity=1):
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False

# Product Manager Class
class ProductManager:
    def __init__(self, file_path=PRODUCTS_FILE):
        self.file_path = file_path

    def load_products(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                products = []
                for category_data in data:
                    category_name = category_data["category"]
                    for item in category_data["products"]:
                        seller_id = item.get("seller_id", "unknown")  # Fallback to "unknown" if missing
                        product = Product(item["name"], item["price"], item["stock"], category=category_name)
                        product.seller_id = seller_id
                        products.append(product)
                return products
        except FileNotFoundError:
            return []

    def save_products(self, products):
        categories = {}
        for product in products:
            category = product.category if hasattr(product, "category") else "Uncategorized"
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "seller_id": product.seller_id  # Ensure this is included
            })

        data = [{"category": k, "products": v} for k, v in categories.items()]
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def add_product(self, name, price, stock, category="Uncategorized", seller_id=None):
        products = self.load_products()  # Load existing products
        new_product = Product(name, price, stock, category, seller_id=seller_id)  # Create a new Product object
        products.append(new_product)  # Add the new product
        self.save_products(products)  # Save updated products to file
# SMS Manager Class
class SMSManager:
    def __init__(self, sms_file):
        self.sms_file = sms_file

    def load_sms_data(self):
        try:
            with open(self.sms_file, "r") as file:
                data = file.read().strip()
                return json.loads(data) if data else {}
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(self.sms_file, "w") as file:
                json.dump({}, file)
            return {}

    def save_sms_data(self, sms_data):
        with open(self.sms_file, "w") as file:
            json.dump(sms_data, file, indent=4)

    def generate_sms_code(self, username):
        sms_data = self.load_sms_data()
        sms_code = str(random.randint(100000, 999999))
        sms_data[username] = sms_code
        self.save_sms_data(sms_data)
        # Removed print statement for displaying SMS code in terminal
        return sms_code

    def verify_sms_code(self, username, code):
        sms_data = self.load_sms_data()
        if sms_data.get(username) == code:
            del sms_data[username]  # Remove code after successful verification
            self.save_sms_data(sms_data)
            return True
        return False

# Cart Class
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity=1):
        if product.purchase(quantity):
            self.items.append((product, quantity))
            print(f"Added {quantity} x {product.name} to cart.")
        else:
            print(f"Sorry, {product.name} is out of stock.")

    def view_cart(self):
        if not self.items:
            print("Your cart is empty.")
            return
        total = 0
        print("Your Cart:")
        for product, quantity in self.items:
            subtotal = product.price * quantity
            total += subtotal
            print(f"{product.name} - ${product.price} x {quantity} = ${subtotal}")
        print(f"Total: ${total:.2f}")

    def checkout(self, product_manager):
        if not self.items:
            print("Your cart is empty. Add items before checkout.")
            return

        total = 0
        for product, quantity in self.items:
            total += product.price * quantity

        print(f"Total amount: ${total:.2f}")
        confirm = input("Do you want to confirm the purchase? (yes/no): ").strip().lower()
        if confirm == "yes":
            print("Processing your purchase...")

            # Load all products
            all_products = product_manager.load_products()

            # Update stock for purchased items
            for product, quantity in self.items:
                for p in all_products:
                    if p.name == product.name and p.category == product.category:  # Match product by name and category
                        p.stock -= quantity  # Reduce stock
                        break

            # Save updated products to file
            product_manager.save_products(all_products)

            print("Purchase confirmed. Thank you for shopping!")
            self.items = []  # Clear the cart
        else:
            print("Purchase cancelled.")

# Seller Interface
def seller_interface(product_manager, seller_id):
    while True:
        question = """
        Welcome to seller interface
        1. Add product
        2. View/Edit products
        3. Logout
        Select an option: """

        choice = input(question).strip()
        if choice == "1":
            name = input("Enter product name: ").strip()
            price = float(input("Enter product price: "))
            stock = int(input("Enter product stock: "))
            category = input("Enter product category (or leave blank for Uncategorized): ").strip()
            if category == "":
                category = "Uncategorized"
            product_manager.add_product(name , price , stock , category , seller_id)
            print("Product added successfully!")

        elif choice == "2":
            print("Loading products from JSON...")
            products = product_manager.load_products()
            seller_products = [product for product in products if product.seller_id == seller_id]

            if seller_products:
                print("Your Products:")
                for idx, product in enumerate(seller_products, start=1):
                    print(f"{idx}. {product.name} - ${product.price} (Stock: {product.stock})")
                    print(f"Category: {product.category}")
                    print("----------------------------------")

                product_choice = input("Select a product to edit (or type 'back' to return): ").strip()
                if product_choice.lower() == "back":
                    continue # Exit the Edit menu
                

                if product_choice.isdigit() and 1 <= int(product_choice) <= len(seller_products):
                    selected_product = seller_products[int(product_choice) - 1]
                    print(f"Editing product: {selected_product.name}")

                    new_name = input("Enter new product name (or leave blank to keep unchanged): ").strip()
                    new_price = input("Enter new product price (or leave blank to keep unchanged): ").strip()
                    new_stock = input("Enter new product stock (or leave blank to keep unchanged): ").strip()
                    new_category = input("Enter new product category (or leave blank to keep unchanged): ").strip()

                    if new_name:
                        selected_product.name = new_name
                    if new_price:
                        selected_product.price = float(new_price)
                    if new_stock:
                        selected_product.stock = int(new_stock)
                    if new_category:
                        selected_product.category = new_category

                    product_manager.save_products(products)
                    print("Product updated successfully!")
            else:
                print("No products found.")

        elif choice == "3":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

# Buyer Interface
def buyer_interface(product_manager):
    cart = Cart()
    while True:
        question = """
        Welcome to buyer interface
        1. Browse Products by Category
        2. View Cart
        3. Checkout
        4. Logout
        select an option: """
        
        choice = input(question).strip()
        
        if choice == "1":
            # Load products and group by category
            products = product_manager.load_products()
            if not products:
                print("No products available.")
            else:
                # Extract categories dynamically
                categories = {}
                for product in products:
                    category = getattr(product, "category", "Uncategorized")
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(product)

                # Display categories
                print("Available Categories:")
                for idx, category in enumerate(categories.keys(), start=1):
                    print(f"{idx}. {category}")

                category_choice = input("Select a category (or type 'back' to return): ").strip()
                if category_choice.isdigit() and 1 <= int(category_choice) <= len(categories):
                    selected_category = list(categories.keys())[int(category_choice) - 1]
                    print(f"Products in {selected_category}:")
                    category_products = categories[selected_category]

                    for idx, product in enumerate(category_products, start=1):
                        print(f"{idx}. {product.name} - ${product.price} (Stock: {product.stock})")

                    product_choice = input("Select a product to add to cart (or type 'back' to return): ").strip()
                    if product_choice.isdigit() and 1 <= int(product_choice) <= len(category_products):
                        selected_product = category_products[int(product_choice) - 1]
                        quantity = int(input(f"How many {selected_product.name}s would you like to add? "))
                        cart.add_item(selected_product, quantity)
        elif choice == "2":
            cart.view_cart()
        elif choice == "3":
            cart.checkout(product_manager)
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select a valid option.")
            
            

