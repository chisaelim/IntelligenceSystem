import requests

# 1. The server answers, but with an error status: this is NOT an exception
response = requests.get("https://jsonplaceholder.typicode.com/todos/999999", timeout=10)
print("missing item:", response.status_code, "ok =", response.ok)

# 2. We cannot reach any server at all: this IS an exception.
#    Nothing listens on port 9 of your own computer, so the connection is refused at once.
try:
    requests.get("http://127.0.0.1:9/", timeout=5)
except requests.RequestException as error:
    print("no connection:", type(error).__name__)
