import requests
import base64
import datetime
import time

def perform_login(email, password):
    url = "https://public-ubiservices.ubi.com/v2/profiles/sessions"
    headers = {
        "Ubi-Appid": "e3d5ea9e-50bd-43b7-88bf-39794f4e3d40",
        "Ubi-Requestedplatformtype": "uplay",
        "Ubi-Transactionid": "51ffc1a6-bfa8-42b6-8319-4bcc5f5616a1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    credentials = f"{email}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers["Authorization"] = f"Basic {encoded_credentials}"
    data = {"rememberMe": False}
    try:
        response = requests.post(url, headers=headers, json=data)
        log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_content_login = f"Login Request at {log_time}:\nURL: {url}\nHeaders: {headers}\nData: {data}\nResponse: {response.status_code}\nResponse content: {response.text}\n\n"
        with open("logs.txt", "a") as log_file:
            log_file.write(log_content_login)
        if response.status_code == 200:
            res = response.json()
            session_id = res['sessionId']
            ticket = res['ticket']
            user_id = res.get('profileId', 'Unknown')
            username = res.get('nameOnPlatform', 'Unknown')
            print("Username:", username)
            print("User-ID:", user_id)
            return session_id, ticket, user_id
        else:
            print("Login failed. Status code:", response.status_code)
            return None, None, None
    except Exception as e:
        print("an error occurred during login:", e)
        return None, None, None

def get_player_name(session_id, ticket, friend_id):
    url = f"https://public-ubiservices.ubi.com/v1/profiles/{friend_id}"
    headers = {
        "Ubi-Appid": "e3d5ea9e-50bd-43b7-88bf-39794f4e3d40",
        "Authorization": f"ubi_v1 t={ticket}",
        "Ubi-SessionId": session_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            player_data = response.json()
            player_name = player_data.get('nameOnPlatform', 'Unknown')
            return player_name
        else:
            return None
    except Exception as e:
        print("an error occurred while retrieving player name", e)
        return None

def get_friends_list(session_id, ticket, user_id):
    url = f"https://public-ubiservices.ubi.com/v3/profiles/{user_id}/friends?locale=en-us"
    headers = {
        "Ubi-Appid": "e3d5ea9e-50bd-43b7-88bf-39794f4e3d40",
        "Authorization": f"ubi_v1 t={ticket}",
        "Ubi-SessionId": session_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_content_friends = f"Friends Request at {log_time}:\nURL: {url}\nHeaders: {headers}\nResponse: {response.status_code}\nResponse content: {response.text}\n\n"
        with open("logs.txt", "a") as log_file:
            log_file.write(log_content_friends)
        if response.status_code == 200:
            friends_data = response.json()
            friend_ids = [friend['pid'] for friend in friends_data['friends']]
            log_content_friend_ids = f"Friend IDs: {', '.join(friend_ids)}\n\n"
            with open("logs.txt", "a") as log_file:
                log_file.write(log_content_friend_ids)
            return friend_ids
        else:
            return None
    except Exception as e:
        print("an error occurred while retrieving friends list", e)
        return None

def delete_friend(session_id, ticket, user_id, friend_id):
    url = f"https://public-ubiservices.ubi.com/v3/profiles/{user_id}/friends/{friend_id}"
    headers = {
        "Ubi-Appid": "e3d5ea9e-50bd-43b7-88bf-39794f4e3d40",
        "Authorization": f"ubi_v1 t={ticket}",
        "Ubi-SessionId": session_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            player_name = get_player_name(session_id, ticket, friend_id)
            print(f"Successfully removed friend {player_name}")
        else:
            print(f"Failed to remove {friend_id}. Status code:", response.status_code)
    except Exception as e:
        print(f"An error occurred while removing friend {friend_id}:", e)

def countdown(t, message):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(message, timeformat, end='\r')
        time.sleep(1)
        t -= 1

def main():
    email = input("Enter your email: ")
    password = input("Enter your password: ")
  
    session_id, ticket, user_id = perform_login(email, password)
    if session_id:
        friends_list = get_friends_list(session_id, ticket, user_id)
        if friends_list:
            total_friends = len(friends_list)
            print("Total Friends:", total_friends)
            for friend_id in friends_list:
                delete_friend(session_id, ticket, user_id, friend_id)
            print("Successfully removed all friends")
        else:
            print("failed to retrieve friends list")
    else:
        print("Login Failed")

if __name__ == "__main__":
    main()

countdown(15, "Closing in")
