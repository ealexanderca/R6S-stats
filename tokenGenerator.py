import base64
import getpass
from web_utils import *

def token_encode(email, password):
    token = 'basic ' + base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")
    return token

def save_token_to_file(token):
    file = open(filePath()+"token.txt", "w") 
    file.write(token)

def main():
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")
    token = token_encode(email, password)
    save_token_to_file(token)
    print("Generated Token saved to token.txt")

if __name__ == "__main__":
    main()
