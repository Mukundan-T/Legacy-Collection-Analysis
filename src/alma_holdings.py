"""
Define methods to obtain information from the Alma API about holdings information, MMS
IDs, and OCLC numbers, given input identifiers.

:author: Mukundan Thanigaivelan
"""

from xml.etree.cElementTree import fromstring
from os import getenv
from requests import get

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
        bibs = item.get("bib")
        if not bibs or not isinstance(bibs, list):
            raise ValueError(f"No bibliographic record found for OCLC {oclc}")

        mms_id = bibs[0].get("mms_id")
    else:
        bib_data = item.get("bib_data")
        if not isinstance(bib_data, dict):
            raise ValueError("Response does not contain bib_data")

        mms_id = bib_data.get("mms_id")

    if mms_id is None or not str(mms_id).strip():
        identifier = barcode or pid or oclc
        raise ValueError(
            f"No MMS ID returned for identifier {identifier}"
        )

    return str(mms_id)

def get_oclc(mms_id: str):
    """
    Given an MMS ID, get the OCLC number and return it as a string.

    :param mms_id: The MMS ID of the holding as a string
    :return: OCLC number as a string
    """
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

    network_numbers = bib.get("network_number")

    if not network_numbers:
        raise ValueError(
            f"No network numbers found for MMS ID {mms_id}"
        )

    oclc = next(
        (
            number.removeprefix("(OCoLC)")
            for number in network_numbers
            if isinstance(number, str)
            and number.startswith("(OCoLC)")
            and number.removeprefix("(OCoLC)").strip()
        ),
        None
    )

    if oclc is None:
        raise ValueError(
            f"No OCLC number found for MMS ID {mms_id}"
        )

    return oclc

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
