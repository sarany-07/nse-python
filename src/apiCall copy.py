
import requests

urllink = "https://www.nseindia.com/api/corporate-announcements?index=sme"

def callapi():

    headers = {
        "User-Agent": "PythonLearningApp/1.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    try:
        with requests.Session() as session:
            session.headers.update(headers)

            response = session.get(
                url=urllink,
                timeout=15
            )

            print("Status Code:", response.status_code)
            print("Content Type:", response.headers.get("Content-Type"))

            response.raise_for_status()

            data = response.json()
            print(data)

    except requests.exceptions.Timeout:
        print("Error: API request timed out")

    except requests.exceptions.HTTPError as error:
        print("HTTP Error:", error)
        print("Response:", response.text[:300])

    except requests.exceptions.RequestException as error:
        print("Request Error:", error)

    except ValueError:
        print("Error: Response is not valid JSON")

    finally:
        print("API request finished")

callapi()
