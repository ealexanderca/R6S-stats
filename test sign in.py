import requests
import getpass
import json

UBI_APP_ID = "39baebad-39e5-4552-8c25-2c9b919064e2"  # R6 Siege App ID
SPACE_ID = "fcf5c91c-5f93-4884-959f-7c3d18a562d6"     # Uplay space ID
LOGIN_URL = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
TWOFA_URL = "https://public-ubiservices.ubi.com/v3/profiles/sessions/two-factor"

def login(email, password):
    headers = {
        "Content-Type": "application/json",
        "Ubi-AppId": UBI_APP_ID,
    }

    payload = {
        "rememberMe": True,
        "spaceId": SPACE_ID,
        "email": email,
        "password": password
    }

    response = requests.post("https://connect.ubisoft.com/login?appId=685a3038-2b04-47ee-9c5a-6403381a46aa&genomeId=f9224c7b-01b4-4a68-ad4f-98ede78ef225&lang=en-CA&nextUrl=https:%2F%2Fconnect.ubisoft.com%2Flogged-in.html%3FappId%3D685a3038-2b04-47ee-9c5a-6403381a46aa%26lang%3Den-CA%26genomeId%3Df9224c7b-01b4-4a68-ad4f-98ede78ef225", headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


def complete_2fa(twofa_ticket, code):
    headers = {
        "Content-Type": "application/json",
        "Ubi-AppId": UBI_APP_ID,
    }

    payload = {
        "ticket": twofa_ticket,
        "code": code
    }

    response = requests.post(TWOFA_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


def main():
    print("🔐 Ubisoft Login")
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    try:
        result = login(email, password)

        if "twoFactorAuthenticationTicket" in result:
            print("\n📲 2FA Required.")
            code = input("Enter your 2FA code: ")
            result = complete_2fa(result["twoFactorAuthenticationTicket"], code)

        ticket = result.get("ticket")
        user_id = result.get("userId")
        session_id = result.get("sessionId")

        print("\n✅ Login successful!")
        print(f"User ID: {user_id}")
        print(f"Ticket: {ticket}")
        print(f"Session ID: {session_id}")

        # You can now use these headers to make further requests
        auth_headers = {
            "Ubi-AppId": UBI_APP_ID,
            "Authorization": f"Ubi_v1 t={ticket}"
        }

        # Example use: print(auth_headers) or fetch profile/stats

    except requests.HTTPError as e:
        print("❌ Login failed:", e)
        if e.response is not None:
            print("Response:", e.response.text)

if __name__ == "__main__":
    main()