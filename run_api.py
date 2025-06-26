import requests

def get_cost(product_name="חפש לי שלט לפלייסטישן 5"):
    url = "https://telegram-bot-1-q869.onrender.com/get-cost"
    params = {"product_name": product_name}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        data = response.json()
        print("Response from API:")
        print(data)
    except requests.RequestException as e:
        print(f"Error while requesting API: {e}")


if __name__ == "__main__":
    get_cost()
