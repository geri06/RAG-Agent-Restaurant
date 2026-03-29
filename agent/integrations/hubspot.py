"""
Integration Stubs — agent/integrations/hubspot.py

STATUS: STUB
  This file exists as a placeholder for the real HubSpot integration.
  Currently it just prints what it would do instead of calling the API.

TO MAKE IT REAL:
  1. Get a HubSpot API key from your sandbox
  2. pip install hubspot-api-client
  3. Replace the print() below with the actual API call
"""


async def create_hubspot_note(
    contact_email: str,
    restaurant_name: str,
    email_draft: str,
) -> str:
    """
    STUB: Creates a note on a HubSpot contact record.

    In production this would:
    1. Look up the contact by email via the HubSpot Contacts API
    2. Create a note associating the email draft with that contact
    3. Return the note URL

    Parameters
    ----------
    contact_email : str
    restaurant_name : str
    email_draft : str

    Returns
    -------
    str
        The URL of the created note (stub returns a fake URL).
    """
    print("\n🗂️  [HubSpot STUB] Would create contact note for:")
    print(f"   Email: {contact_email}")
    print(f"   Restaurant: {restaurant_name}")
    print(f"   Draft length: {len(email_draft)} chars")
    return "https://app.hubspot.com/contacts/stub/note/999"
