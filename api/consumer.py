import requests

response = requests.get("http://localhost:5000/api/v1/users/")

users = response.json()
print(users)