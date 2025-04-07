import json
import os
from time import sleep
import random
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from pprint import pprint as pp
from scrape_website import scrape_email_from_website
from bin import load_user_agents, load_proxies
import zipcodes

DATA_DIR = "psychology_today/therapist_data/"


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
    for result in zipcodes.filter_by(state="IN"):
        zipcode = result["zip_code"]
        city = result["city"]
        state = result["state"]
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
        therapist_uuids = [
            uuid for uuid in therapist_uuids if uuid not in current_uuids]

        for count, therapist_uuid in enumerate(therapist_uuids, start=1):
            psychology_today_api = f"https://www.psychologytoday.com/directory-listing/listing/profile/{therapist_uuid}?lang=en"
            # rand_proxy = random.choice(proxies)
            ua = random.choice(uas)
            # print(f"Random Proxy: {rand_proxy}")
            print(f"Random User-Agent: {ua}")
            # proxy = {
            #     "http": rand_proxy,
            #     # "https": rand_proxy
            # }
            headers = {
                "User-Agent": ua,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://www.google.com",
                "DNT": "1",  # Do Not Track
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "no-cache",
            }
            print(f"Pulling Therapist UUID JSON: {therapist_uuid}")
            sleep(random.uniform(5, 10))
            res = requests.get(psychology_today_api,
                               # proxies=proxy,
                               headers=headers).json()
            sleep(random.uniform(4, 6))
            # id, name, credentials, address, uuid, personal_website/out.pscyh link, education, phone_number, emails, profile_link, session_fees
            # Setting up keys and data ato pull what is necessary into a database
            primary_location = res.get("primaryLocation", {})
            address_keys = ["addressLine1", "addressLine2",
                            "cityName", "regionName", "postalCode", "countryCode"]
            education = res.get("education", {})
            education_keys = ["institution", "diplomaDegree"]
            listing_name = res.get("listingName")
            # Grab the out link based on a previous pattern
            out_link = f"https://out.psychologytoday.com/us/profile/{res.get('id')}/website-redirect" if res.get(
                "hasWebsite") else None
            url = None
            if out_link != None:
                grab_redirect = requests.get(
                    out_link, headers=headers, allow_redirects=False)
                if grab_redirect.ok:
                    url = grab_redirect.headers["location"]

            # Should be able to grab the URL from the redirect request
            emails = []
            if url != None:
                print("Scraping personal website for emails:")
                try:
                    emails = scrape_email_from_website(url)
                    print(f"Found emails!: {emails}")
                    print(f"URL: {url}")
                except Exception as e:
                    print(f'Error {e}')
            else:
                print("No personal websites/email :(")

            print(f"Adding Therapist {count}, ID: {res.get('id')}!")

            record = {
                "id": res.get("id"),
                "uuid": res.get("uuid"),
                "name": res.get("contactName"),
                "address": " ".join([str(primary_location.get(key)) for key in address_keys]),
                "phone_number": res.get("formattedPhoneNumber"),
                "credentials": " ".join([cred.get("label") if cred.get("type") == "academic" else "" for cred in res.get("suffixes")]),
                "education": " ".join([str(education.get(key)) for key in education_keys]) if education != None else None,
                "session_fees": str(res.get("fees", {}).get("individual_session_cost")) if res.get("fees") != None else None,
                "profile_link": f"https://www.psychologytoday.com/us/therapists/{listing_name.lower().replace(' ', '-')}-{city.lower()}-{state.lower()}/{res.get('id')}",
                "personal_website": url,
                "emails": list(emails)
            }

            cur_data = []
            with open(f"psychology_today/therapist_data/therapists_{zipcode}.json", "r", encoding="utf-8") as file:
                cur_data = json.load(file)
            if not any(entry for entry in data if entry.get("id") == record["id"] and entry.get("uuid") == record["uuid"]):
                data.append(record)
                cur_data.append(record)
            with open(f"psychology_today/therapist_data/therapists_{zipcode}.json", "w", encoding="utf-8") as file:
                print("Writing to file!")
                json.dump(cur_data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
