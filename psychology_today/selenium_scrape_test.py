import json
import os
from time import sleep
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bin import load_user_agents
# from pprint import pprint as pp

DATA_DIR = "psychology_today/therapist_data_test/"


def process_browser_logs_for_network_events(logs):
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.response" in log["method"]
            or "Network.request" in log["method"]
            or "Network.webSocket" in log["method"]
        ):
            yield log


def main():
    # load the user agents, in random order
    uas = load_user_agents()
    # ps = load_proxies()

    # Set up Chrome options and capabilities
    ua = random.choice(uas)
    # proxy = random.choice(ps)

    # Selenium options
    options = Options()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_argument(f'--user-agent={ua}')
    # Uncomment below to use proxy
    # options.add_argument(f'--proxy-server={proxy}')
    # options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--start-maximized')
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-web-security')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-webrtc")
    options.add_argument("--disable-webgl")
    options.add_argument("--use-gl=swiftshader")
    options.accept_insecure_certs = True
    # options.add_experimental_option("prefs", {
    #     "profile.default_content_settings.popups": 0,
    #     "protocol_handler.excluded_schemes.mailto": True,
    # })
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)

    # Start browser
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)
    driver = uc.Chrome(headless=True, use_subprocess=False,
                       options=options, version=131)
    start_zip_code = str(
        int(input("What zipcode would you like to start in?: ")))
    for result in [{"zip_code": 46001}, {"zip_code": 46011}]:
        zipcode = result["zip_code"]
        if zipcode != start_zip_code and os.path.isfile(f"psychology_today/therapist_data/therapists_{zipcode}.json"):
            print(f"Already explored {zipcode}")
            continue
        # Open the target URL
        driver.get(f"https://www.psychologytoday.com/us/therapists/{zipcode}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Retrieve and process network logs
        therapist_uuids = []
        while True:
            try:
                logs = driver.get_log("performance")
                events = process_browser_logs_for_network_events(logs)
                for event in events:
                    request = event['params'].get('request', {})
                    if request.get("method") == "POST" and request.get("url") == "https://www.psychologytoday.com/api/metrics/profile" and request.get("hasPostData"):
                        request_data = json.loads(request.get("postData"))
                        if request_data.get("metric_name") == "Impression":
                            therapist_uuids.extend(
                                request_data.get("entity_uuids"))
                sleep(random.uniform(3, 4))
                next_button = driver.find_element(
                    By.XPATH, '//a[contains(@class, "page-btn") and @title="Next - Therapists listings"]')
                # Scroll to the element
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", next_button)
                # Use JavaScript to click the button
                driver.execute_script("arguments[0].click();", next_button)
                sleep(random.uniform(3, 4))
            except Exception as e:
                print(f"Error retrieving or processing logs: {e}")
                break

        print(len(therapist_uuids))
        # Quit the WebDriver
        # Get existing data from the JSON file
        # No this needs to grab all data, it will repeat across zipcodes
        data = []
        seen_uuids_ids = set()  # Set to track unique UUID

        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(DATA_DIR, filename), "r") as file:
                    print(file)
                    try:
                        data = json.load(file)
                        if isinstance(data, list):  # Check if the JSON is an array
                            for therapist in data:
                                therapist_uuid = therapist.get("uuid")

                                if therapist_uuid in seen_uuids_ids:
                                    continue  # Skip duplicate entry
                                else:
                                    seen_uuids_ids.add(therapist_uuid)
                                    data.append(therapist)
                        else:
                            print(f"Skipping non-array JSON file: {filename}")
                    except json.JSONDecodeError:
                        print(f"Skipping invalid JSON file: {filename}")

        current_uuids = [entry["uuid"] for entry in data]
        print(current_uuids)
        therapist_uuids = [
            uuid for uuid in therapist_uuids if uuid not in current_uuids]
        print(therapist_uuids)


if __name__ == "__main__":
    main()
