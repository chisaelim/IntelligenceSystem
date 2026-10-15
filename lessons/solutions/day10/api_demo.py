import requests

url = "https://jsonplaceholder.typicode.com/todos/1"
response = requests.get(url, timeout=10)  # always give a timeout

print("status code:", response.status_code)
print("ok:", response.ok)
print("content type:", response.headers["Content-Type"])

data = response.json()  # JSON text -> Python dictionary
print("title:", data["title"])
print("completed:", data["completed"])
