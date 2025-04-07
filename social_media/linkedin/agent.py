from browser_use import Agent
import asyncio
from controller import controller
from browser import browser
from llm import llm
from configuration import configuration

auth, config = configuration()

task = f"""
# LinkedIn Professional Networking Task

## SETUP
1. Login: Sign in to LinkedIn with {auth["linkedin"]["email"]} and {auth["linkedin"]["password"]}
2. Target companies: Visit each company in {config["cmh_list"]} one by one

## FOR EACH COMPANY: EXACT SEQUENCE
1. Go to company page
2. Click "People" tab
3. SET current_position = top of page
4. WHILE not at end of page:
   a. Identify visible profiles (around 5-7)
   b. FOR EACH visible profile:
      i. READ position title carefully
      ii. IF position contains ANY of these terms:
         - "Clinical Director"
         - "Program Manager" + "outpatient"
         - "Operations Director" + "outpatient"
         - "Executive Director" + "outpatient"
         - "Manager" + "adult services"
         - "Director" + "adult services"
      iii. AND does NOT contain ANY of these terms:
         - "substance use"
         - "children"
         - "youth"
         - "family"
         - "therapist"
         - "clinician"
      iv. THEN:
         - RIGHT-CLICK profile and select "Open in new tab"
         - SWITCH to new tab
         - CLICK "Connect" (or click "More" then "Connect")
         - When prompted, click "Connect" WITHOUT adding a note
         - RECORD their: Name, Position, Company, Profile URL
         - CLOSE tab
         - RETURN to people list tab
   c. SCROLL down slightly to see new profiles
   d. REMEMBER last name viewed in case page resets
   e. IF page resets to top:
      i. Scroll down to find last name viewed
      ii. Continue from there

## RECORD-KEEPING
- After each successful connection, immediately write:
  Name:
  Position:
  Company:
  Profile URL:

## ERROR HANDLING
- IF LinkedIn shows connection limit message: STOP and tell me
- IF unsure about a position: SKIP that profile
- IF can't find "Connect" button: TRY finding "More" button first

## EXTREMELY IMPORTANT
- Process EVERY profile on the page before moving to next company
- Do NOT give up after checking just a few profiles
- Follow these steps EXACTLY in order with no deviation
- Do NOT improvise or change the process
"""
# Create agent with the model


async def main():
    try:
        async with await browser.new_context() as context:
            # context.on("page", lambda page: inject_script(page))
            agent = Agent(
                task=task,
                llm=llm,
                # use_vision=True,
                # planner_llm=planner_llm,
                # use_vision_for_planner=False,
                # planner_interval=4,
                controller=controller,
                browser=browser,
                browser_context=context,
            )
            result = await agent.run()
            print(result)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if browser:
            await browser.close()
        # if session:
        #     client.sessions.release(session.id)


async def inject_script(page):
    """Inject JavaScript if the page starts with LinkedIn"""
    if page.url.startswith("https://www.linkedin.com"):
        await page.evaluate(
            """
            console.log("Injected JavaScript into LinkedIn!");
            document.body.style.backgroundColor = 'red';  // Example modification
        """
        )


if __name__ == "__main__":
    asyncio.run(main())
