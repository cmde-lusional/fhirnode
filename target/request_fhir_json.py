import requests

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

if __name__ == "__main__":
    url = "http://localhost:5000/protocol"
    data = fetch_data(url)
    if data:
        print(data)