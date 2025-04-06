
from functions import seller_interface, buyer_interface, UserManagement, ProductManager, SMSManager


# Constants for file paths

PRODUCTS_FILE = "products.json"
SELLERS_FILE = "sellers.json"
BUYERS_FILE = "buyers.json"
SMS_FILE = "sms.json"

# Main Execution
if __name__ == "__main__":
    product_manager = ProductManager(PRODUCTS_FILE)
    seller_users = UserManagement(SELLERS_FILE)
    buyer_users = UserManagement(BUYERS_FILE)
    sms = SMSManager(SMS_FILE)

    question = """
    Welcome to the Online Store!
    1. Login as Seller
    2. Login as Buyer
    3. Sign Up (Seller)
    4. Sign Up (Buyer)
    5. Exit
    
    select option:  """
    
    
    

    while True:
        choice = input(question).strip()
        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            if username.strip() and password.strip():
                if seller_users.authenticate_user(username, password):
                    seller_users.send_sms_code(username)
                    sms = input("please enter your sms code: ")
                if seller_users.authenticate_user(username, password, sms):
                    seller_interface(product_manager, username)
                else:
                    print("Authentication failed. Please try again.")
            else:
                print("Username or password is incorrect please try again")
        elif choice == "2":
            username = input("Username: ")
            password = input("Password: ")
            if username.strip() and password.strip() :
                if buyer_users.authenticate_user(username, password):
                    buyer_users.send_sms_code(username)  # Send SMS code
                    sms = input("Please enter your SMS code: ").strip() 
                if buyer_users.authenticate_user(username, password, sms):  # Authenticate with SMS
                    buyer_interface(product_manager)
                else:
                    print("Authentication failed. Please try again.")
        elif choice == "3":
            username = input("New Username: ")
            password = input("New Password: ")
            seller_users.register_user(username, password)
        elif choice == "4":
            username = input("New Username: ")
            password = input("New Password: ")
            buyer_users.register_user(username, password)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select a valid option.")