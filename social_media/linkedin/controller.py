import json
from pathlib import Path
from browser_use import Controller, ActionResult
from pydantic import BaseModel, Field

# Initialize the controller
controller = Controller()


class Contact(BaseModel):
    name: str = Field(..., description="The full name of the contact")
    position: str = Field(..., description="The job position or title of the contact")
    company: str = Field(..., description="The company or organization name")
    profile_link: str = Field(..., description="URL to the contact's profile")


@controller.action("Ask user for information")
def ask_human(question: str) -> ActionResult:
    answer = input(f"\n{question}\nInput: ")
    return ActionResult(extracted_content=answer)


@controller.action("Write to JSON file")
def write_json(name: str, position: str, company: str, profile_link: str):
    contact = Contact(
        name=name, position=position, company=company, profile_link=profile_link
    )
    """
    Append a single Contact object to a JSON file.
    If the file doesn't exist, it creates a new file.
    If the file exists, it reads the current contacts, appends the new one, and writes back.

    Args:
        contact: Single Contact object to append
        file_path: Path to the JSON file
    """
    file_path = Path("contacts.json")
    contacts = []

    # Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing file if it exists
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                contacts = json.load(f)

            # Validate it's a list
            if not isinstance(contacts, list):
                print(
                    f"Warning: Existing file {file_path} does not contain a JSON array. Creating new file."
                )
                contacts = []
        except json.JSONDecodeError:
            print(
                f"Warning: Existing file {file_path} is not valid JSON. Creating new file."
            )
            contacts = []

    # Append the new contact
    contacts.append(contact.model_dump())

    # Write back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"Successfully appended contact '{contact.name}' to {file_path}")


@controller.action("Read JSON file")
def read_json():
    file_path = Path("contacts.json")
    # Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # Read existing file if it exists
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
