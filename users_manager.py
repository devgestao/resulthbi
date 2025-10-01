import json
from pathlib import Path
from companies_manager import get_company_by_cnpj

def load_users():
    with open('users.json', 'r') as file:
        return json.load(file)['users']

def save_users(users_data):
    with open('users.json', 'w') as file:
        json.dump({'users': users_data}, file, indent=4)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            # Get companies data for user's CNPJs
            user_companies = []
            for cnpj in user['empresas_vinculos']:
                company = get_company_by_cnpj(cnpj)
                if company:
                    user_companies.append(company)
            return {
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin'],
                'empresas': user_companies
            }
    return None

def add_user(user_data):
    users = load_users()
    users.append(user_data)
    save_users(users)

def update_user(username, user_data):
    users = load_users()
    for i, user in enumerate(users):
        if user['username'] == username:
            users[i] = user_data
            break
    save_users(users)

def delete_user(username):
    users = load_users()
    users = [u for u in users if u['username'] != username]
    save_users(users)
