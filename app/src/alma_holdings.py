"""
Define methods to obtain information from the Alma API about holdings information and
OCLC numbers, given input barcodes.

:author: Mukundan Thanigaivelan
"""

from concurrent.futures import ThreadPoolExecutor
from xml.etree.cElementTree import fromstring
from dotenv import load_dotenv
from os import getenv
from requests import get
from pathlib import Path

BASE_URL = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
OCLC_URL = f"{BASE_URL}/items"
ALMA_URL = f"{BASE_URL}/bibs"

def get_oclc(params: dict) -> str:
    """
    Given URL params, query the Alma API and obtain information from which find and
    return the OCLC number.
    
    :param params: URL params with the Alma API key and barcode
    :return: the OCLC number corresponding to that barcode; "" otherwise
    """
    response = get(OCLC_URL, params=params, allow_redirects=True)
    
    root = fromstring(response.text)
    nums = root.findall(".//network_number")
    
    for num in nums:
        if "OCoLC" in num.text:
            return "".join(filter(str.isdigit, num.text))
    return ""

def get_all_oclcs(barcode_file: str) -> list:
    """
    Given a text file of barcodes, return a list of OCLC numbers that
    correspond to each barcode with parallel API requests to the Alma
    API.
    
    :param barcode_file: a text file of numerical barcodes
    :param oclc_num_file: a list of corresponding OCLC numbers
    """
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file)
    api_key = getenv("BIB_KEY")

    rate_limit = 10
    oclcs = []
    with (ThreadPoolExecutor(max_workers = rate_limit) as executor, 
          open(barcode_file, "r") as infile):
        futures = [
            executor.submit(
                get_oclc, 
                {"item_barcode": barcode.strip(), 
                 "apikey": api_key}
            ) 
            for barcode in infile]
        for future in futures:
            result = future.result()
            oclcs.append(result)

    return oclcs

def write_oclcs_to_txt(oclcs: list, outfile_path: str) -> None:
    """
    Given a list of OCLC numbers and an outfile path, write the OCLC numbers
    to the given text file.

    :param oclcs: a list of OCLC numbers
    :param outfile_path: a string path to text file
    """
    with open(outfile_path, "w") as outfile:
        for oclc in oclcs:
            outfile.write(f"{oclc}\n")

def get_mms_id_with_oclc(params: dict) -> str:
    """
    Given URL params with the OCLC number and API key, return the MMS ID
    for the holding.
    
    :param params: URL params to get the MMS ID with the OCLC number
    :return: the MMS ID if it exists; "" otherwise
    """
    response = get(ALMA_URL, params=params, allow_redirects=True)

    root = fromstring(response.text)
    mms_id = root.find(".//mms_id")

    if mms_id.text:
        return mms_id.text
    return ""

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
