from browser_use import Browser, BrowserConfig

# from steel import Steel
# from configuration import configuration

# auth, _ = configuration()

# client = Steel(base_url="http://0.0.0.0:3000", steel_api_key="testkey")
# client = Steel(steel_api_key=auth["steel"]["api_key"])

# Create a new browser session with custom options
# session = client.sessions.create(
#     # api_timeout=1800000,  # 30 minutes
#     # block_ads=True,
# )


# # Initialize the browser
browser = Browser(
    config=BrowserConfig(
        # Specify the path to your Chrome executable
        chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS path
        # disable_security=True,
        # cdp_url="ws://0.0.0.0:3000/",
        # cdp_url=f"wss://connect.steel.dev?apiKey={auth["steel"]["api_key"]}&sessionId={session.id}",
    )
)

# browser_context = BrowserContext(browser=browser)
# browser_context.add_init_script(
#     """
# if (window.location.href.startsWith('https://www.linkedin.com')) {
#     // Your LinkedIn-specific JavaScript here
#     console.log('This is a LinkedIn page');
#     // Add your custom JavaScript code here
# }
# """
# )
