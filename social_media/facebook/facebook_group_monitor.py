import time
import json
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FacebookPostMonitor:
    def __init__(self, email, password, keywords, headless=False):
        """Initialize the Facebook post monitor with your credentials and keywords."""
        self.email = email
        self.password = password
        self.keywords = keywords

        # Set up the browser options
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-notifications')
        options.add_argument('--lang=en')
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

        # Initialize the browser
        self.driver = uc.Chrome(
            headless=False, use_subprocess=False, options=options)
        self.wait = WebDriverWait(self.driver, 10)

        # Results storage
        self.relevant_posts = []

    def login(self):
        """Log in to Facebook."""
        try:
            self.driver.get("https://www.facebook.com")

            # Accept cookies if prompted
            try:
                cookie_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]")))
                cookie_button.click()
                time.sleep(1)
            except:
                pass  # No cookie prompt

            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(self.email)

            # Enter password
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()

            # Wait for login to complete
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@aria-label='Create' or @aria-label='Your profile']")))

            print("Login successful")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def scan_group_for_relevant_posts(self, group_url, group_name, max_posts=300, scroll_times=50):
        """Scan a Facebook group for posts containing relevant keywords."""
        try:
            print(f"\nScanning group: {group_name} ({group_url})")
            self.driver.get(group_url)
            time.sleep(5)  # Allow page to load

            # Scroll down to load more posts
            for i in range(scroll_times):
                print(f"Scrolling to load more posts ({i+1}/{scroll_times})")
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Find all posts
            print("Finding posts...")
            posts = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'userContentWrapper') or contains(@class, 'feed_story_') or contains(@class, 'x1yztbdb')]")

            print(f"Found {len(posts)} posts, scanning for keywords...")
            group_relevant_posts = []

            for post in posts[:max_posts]:
                try:
                    # Get post text
                    post_text = post.text.lower()

                    # Check if post contains relevant keywords
                    matched_keywords = []
                    for keyword in self.keywords:
                        if keyword.lower() in post_text:
                            matched_keywords.append(keyword)

                    # If post contains any relevant keywords, add it to the list
                    if matched_keywords:
                        # Try to get post link
                        try:
                            timestamp = post.find_element(
                                By.XPATH, ".//a[contains(@class, 'timestamp') or contains(@href, '/permalink/')]")
                            post_link = timestamp.get_attribute("href")
                        except:
                            post_link = "Link not found"

                        # Try to get author name
                        try:
                            author = post.find_element(
                                By.XPATH, ".//a[contains(@class, 'profileLink') or contains(@data-hovercard, 'user')]")
                            author_name = author.text
                            author_link = author.get_attribute("href")
                        except:
                            author_name = "Unknown"
                            author_link = ""

                        # Add post to relevant posts list
                        relevant_post = {
                            "group_name": group_name,
                            "group_url": group_url,
                            # Truncate long posts
                            "post_text": post_text,
                            "post_link": post_link,
                            "author_name": author_name,
                            "author_link": author_link,
                            "matched_keywords": matched_keywords,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                        group_relevant_posts.append(relevant_post)
                        print(
                            f"✅ Found relevant post with keywords: {', '.join(matched_keywords)}")
                except Exception as e:
                    print(f"Error processing post: {e}")
                    continue

            print(
                f"Found {len(group_relevant_posts)} relevant posts in this group")
            return group_relevant_posts

        except Exception as e:
            print(f"Error scanning group: {e}")
            return []

    def scan_multiple_groups(self, groups_config, max_posts_per_group=30):
        """Scan multiple Facebook groups for relevant posts."""
        all_relevant_posts = []

        if not self.login():
            print("Failed to log in to Facebook. Exiting.")
            return all_relevant_posts

        for group_name, group_url in groups_config.items():
            group_posts = self.scan_group_for_relevant_posts(
                group_url, group_name, max_posts=max_posts_per_group)
            all_relevant_posts.extend(group_posts)
            time.sleep(3)  # Pause between groups

        self.relevant_posts = all_relevant_posts
        return all_relevant_posts

    def save_relevant_posts_json(self, filename="relevant_posts.json"):
        """Save the relevant posts to a JSON file."""
        if self.relevant_posts:
            # Convert datetime objects to strings for JSON serialization
            serializable_posts = []
            for post in self.relevant_posts:
                serializable_post = dict(post)
                serializable_posts.append(serializable_post)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_posts, f, indent=4, ensure_ascii=False)

            print(
                f"\n✅ Saved {len(self.relevant_posts)} relevant posts to {filename}")
            return True
        else:
            print("\n❌ No relevant posts found to save.")
            return False

    def quit(self):
        """Close the browser."""
        self.driver.quit()


def load_groups_config(filename="target_groups.json"):
    """Load groups configuration from JSON file or create a default one."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create a default config if file doesn't exist
        default_config = {
            "Therapist Network": "https://www.facebook.com/groups/therapistnetworking",
            "Private Practice Community": "https://www.facebook.com/groups/privatepracticecommunity"
        }

        with open(filename, 'w') as f:
            json.dump(default_config, f, indent=4)

        print(
            f"Created default groups config in {filename}. Please edit it with your target groups.")
        return default_config


# Example usage
if __name__ == "__main__":
    # Facebook credentials
    fb_email = ""
    fb_password = ""

    # Keywords to search for
    keywords = [
        "cancellations",
        "income",
        "revenue",
        "no-show",
        "no",
        "anyone",
        "know",
        "show",
        "cancelled",
        "cancel",
        "finance",
        "frustrated",
        "frustration",
        "frustrations",
        "frustrating",
        "tool",
        "tools",
        "exist"
    ]

    # Load groups from config file
    groups = load_groups_config()

    print("🔍 Facebook Post Monitor Starting")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Groups to scan: {len(groups)}")

    # Create and run the monitor
    monitor = FacebookPostMonitor(
        fb_email, fb_password, keywords, headless=False)

    try:
        # Scan all groups
        relevant_posts = monitor.scan_multiple_groups(
            groups, max_posts_per_group=300)

        # Save results to JSON
        monitor.save_relevant_posts_json("relevant_posts.json")

        print("\n📊 Summary:")
        print(f"- Total relevant posts found: {len(relevant_posts)}")
        print(f"- Groups scanned: {len(groups)}")

        if len(relevant_posts) > 0:
            print("\n🔔 Next Steps:")
            print("- Review the relevant_posts.json file")
            print("- Visit the relevant posts on Facebook to engage manually")
    finally:
        # Always quit the browser
        monitor.quit()
