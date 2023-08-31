import base64
import getpass

def generate_token(email, password):
    token = 'basic ' + base64.b64encode((email + ":" + password).encode("utf-8")).decode("utf-8")
    return token

def save_token_to_file(token):
    with open("token.txt", "w") as file:
        file.write(token)

def main():
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")

    token = generate_token(email, password)
    save_token_to_file(token)
    print("Generated Token saved to token.txt")

if __name__ == "__main__":
    main()
