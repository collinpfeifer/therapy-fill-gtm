from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import re
from ollama import chat
from pydantic import BaseModel
from bin import load_proxies, load_user_agents
import random

uas = load_user_agents()
ps = load_proxies()

class FunFact(BaseModel):
    fun_fact: str
    name: str
    email: str

class FunFactList(BaseModel):
    fun_facts: list[FunFact]

def scrape_email_from_website(start_url: str, time_limit=600):
    ua = random.choice(uas)
    #proxy = random.choice(ps)

    # Selenium options
    options = Options()
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
    driver = uc.Chrome(headless=True, use_subprocess=False, options=options)
    driver.set_page_load_timeout(30)

    # Initialize sets and queue
    # Put links that are not good to scrape
    visited_links = {"https://thriveworks.com/", "https://lifestance.com/", "https://growtherapy.com/"}
    queue = [start_url]
    emails = set()
    start_time = time.time()

    # Start scraping
    while queue and time_limit > 0:
        url = queue.pop(0)  # Get the next URL to process
        if url in visited_links:
            continue  # Skip if already visited
        visited_links.add(url)  # Mark as visited
        try:
            if time.time() - start_time > time_limit:
                print(f"Timed out after {time_limit} seconds. Returning emails scraped so far.")
                return emails
            driver.get(url)
            WebDriverWait(driver, 60).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "loading-spinner"))  # Intermediary element
                )
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Get the page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Extract emails
            email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
            emails.update(set(re.findall(email_pattern, soup.get_text())))

            # response = chat(
            #     messages=[
            #     {
            #       'role': 'user',
            #       'content': f'In the following HTML page could you generate one fun fact for each person/email address in this list EMAISL: {emails}, based on the persons description within this html page? If there is no description of any emails or people, return nothing HTML:{html}',
            #     }
            #   ],
            #   model='mistral',
            #   format=FunFactList.model_json_schema())

            # fun_facts = FunFactList.model_validate_json(response.message.content)
            # print(fun_facts)

            # Extract links and add new ones to the queue
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)  # Resolve relative URLs
                parsed_url = urlparse(full_url)
                if href.startswith('mailto:'):
                    # Extract email address (remove 'mailto:' and query parameters if present)
                    email = href.split(':')[1].split('?')[0]
                    emails.add(email)
                # Only add links that belong to the same domain and are not visited
                if parsed_url.netloc == urlparse(start_url).netloc and full_url not in visited_links:
                    queue.append(full_url)

            br_fixation_elements = soup.find_all('br-fixation')
            for element in br_fixation_elements:
                print(element.get_text())
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    driver.quit()
    return emails

if __name__ == "__main__":
    # Example usage
    start_url = 'https://www.thecarecollectiveindy.com/'
    #start_url = 'https://out.psychologytoday.com/us/profile/1237051/website-redirect'
    #start_url = "https://thriveworks.com/therapist/in/miosha-mya-williams"
    #start_url = "https://bot.sannysoft.com/"
    emails = scrape_email_from_website(start_url)
    print(emails)
