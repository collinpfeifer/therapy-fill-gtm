from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import random
import time
from bin import load_proxies, load_user_agents

# Function to set up Selenium with a proxy
def create_driver_with_proxy(proxy, user_agent):
    options = webdriver.ChromeOptions()
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--headless")  # Optional: headless mode for background execution
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)

# Function to scrape with retries
def scrape_with_proxies(url):
    proxies = load_proxies()
    user_agents = load_user_agents()
    for proxy in proxies:
        try:
            print(f"Trying proxy: {proxy}")
            user_agent = random.choice(user_agents)
            driver = create_driver_with_proxy(proxy, user_agent)
            driver.get(url)

            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Extract the page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Example: Extract the title of the page
            title = soup.title.string if soup.title else "No title found"
            print(f"Page title: {title}")

            driver.quit()
            return html  # Return the HTML content if successful

        except WebDriverException as e:
            print(f"Proxy failed: {proxy} - Error: {e}")
            driver.quit()
            continue  # Try the next proxy

    print("No working proxies found!")
    return None

# Example usage
# proxies = load_proxies()
# user_agents = load_user_agents()
# url = "https://www.example.com"

# html_content = scrape_with_proxies(url, proxies, user_agents)

# if html_content:
#     print("Scraping successful!")
# else:
#     print("Failed to scrape with all proxies.")
