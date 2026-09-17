"""
Define methods to obtain information from the Alma API about holdings information, MMS
IDs, and OCLC numbers, given input identifiers.

:author: Mukundan Thanigaivelan
"""

from xml.etree.cElementTree import fromstring
from dotenv import load_dotenv
from os import getenv
from requests import get
from pathlib import Path

BASE_URL = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
OCLC_URL = f"{BASE_URL}/items"
ALMA_URL = f"{BASE_URL}/bibs"

def get_mms_id(
    barcode: str = None, 
    pid: str = None,
    oclc: str = None
) -> str:
    """
    Using the given barcode, Item PID, or OCLC #, get the item's MMS ID and
    return it.

    :param barcode: a given barcode string
    :param pid: a given Item PID or None
    :param oclc: a given OCLC # or None
    :return: a string with MMS ID
    """
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file)
    api_key = getenv("BIB_KEY")

    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json",
    }

    if barcode:
        response = get(
            OCLC_URL, 
            params = {
                "item_barcode": barcode,
            }, 
            headers = headers, 
            allow_redirects = True
        )
    elif pid:
        response = get(
            f"{ALMA_URL}/0/holdings/0/items/{pid}", 
            headers = headers
        )
    elif oclc:
        response = get(
            ALMA_URL,
            params = {
                "other_system_id": f"(OCoLC){oclc}"
            },
            headers = headers
        )
    else:
        raise ValueError("Either barcode, Item PID, or OCLC # must be provided.")

    response.raise_for_status()
    item = response.json()

    if oclc:
        return item["bib"][0]["mms_id"]

    return item["bib_data"]["mms_id"]

def get_oclc(mms_id: str):
    """
    Given an MMS ID, get the OCLC number and return it as a string.

    :param mms_id: The MMS ID of the holding as a string
    :return: OCLC number as a string
    """
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file)
    api_key = getenv("BIB_KEY")

    response = get(
        f"{ALMA_URL}/{mms_id}",
        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json",
        }
    )

    response.raise_for_status()
    bib = response.json()

    if not bib["network_number"]:
        return ""
    
    return next(
        (number.removeprefix("(OCoLC)") 
            for number in bib["network_number"] 
            if number.startswith("(OCoLC)")
        ),
        None
    )

def get_info_from_mms_id(mms_id: str, params: dict) -> str:
    """
    Given a holding's MMS ID and the API key, return a printable string with desired
    information about the holding including but not limited to title, publisher, date
    of publication, etc.
    
    :param mms_id: The MMS ID of the holding
    :param params: URL params with API key
    :return: a formatted string with desired holdings information
    """
    url = f"{ALMA_URL}/{mms_id}/holdings/ALL/items"

    response = get(url, params=params)
    root = fromstring(response.text)
    
    # Field names as they appear in XML response
    field_signifiers = [".//title", ".//permanent_call_number", ".//description", 
                        ".//publisher_const", ".//date_of_publication", 
                        ".//place_of_publication", ".//internal_note_1", 
                        ".//internal_note_2", ".//physical_material_type", 
                        ".//network_number", ".//mms_id", ".//holding_id", ".//pid", 
                        ".//barcode", ".//location"]
    
    info = []
    for field in field_signifiers:
        value = root.find(field)
        if value is not None:
            value = ("".join(filter(str.isdigit, value.text)) 
                            if field == ".//network_number" 
                            else value.text)
            info.append(value)
        else:
            info.append("None")

    return info
