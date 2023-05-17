import requests


def get_address(latitude, longitude):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": f"{latitude},{longitude}",
        "key": '5e7a317742a4495bb60728a01c809e5d'
    }

    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code == 200 and data.get("status", {}).get("code") == 200:
        results = data["results"]
        print(results)
        if results:
            address = results[0]["formatted"]
            return address
    return None
