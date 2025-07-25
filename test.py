import requests

# POST test
response = requests.post("http://localhost:8000/reviews", 
                        json={"text": "Я люблю этот товар"})
print(response.json())

# GET test  
response = requests.get("http://localhost:8000/reviews?sentiment=positive")
print(response.json())