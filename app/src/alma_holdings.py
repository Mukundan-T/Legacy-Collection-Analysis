from concurrent.futures import ThreadPoolExecutor
from xml.etree.cElementTree import fromstring
from requests import get
from dotenv import load_dotenv
from os import getenv
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

def get_oclcs(barcode_file):
    """
    Given a text file of barcodes, return a text file of OCLC numbers that
    correspond to each barcode.
    
    :param barcode_file: A text file of numerical barcodes
    :param oclc_num_file: A text file of corresponding OCLC numbers
    """
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file)

    rate_limit = 10
    futures = []
    with ThreadPoolExecutor(max_workers = rate_limit) as executor, open(barcode_file, "r") as infile:
        for barcode in infile:
            futures.append(executor.submit(get_oclc, {
                                           "item_barcode": barcode.strip(), 
                                           "apikey": getenv("BIB_KEY")
                                           }))

    oclcs = []
    for future in futures:
        if future.result():
            oclcs.append(future.result())

    return oclcs

def get_oclcs_to_file(barcode_file: str, oclc_num_file: str) -> None:
    """
    Given a text file of barcodes, return a text file of OCLC numbers that
    correspond to each barcode.
    
    :param barcode_file: A text file of numerical barcodes
    :param oclc_num_file: A text file of corresponding OCLC numbers
    """
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file)

    rate_limit = 10
    futures = []
    with ThreadPoolExecutor(max_workers = rate_limit) as executor, open(barcode_file, "r") as infile:
        for barcode in infile:
            futures.append(executor.submit(get_oclc, {
                                           "item_barcode": barcode.strip(), 
                                           "apikey": getenv("BIB_KEY")
                                           }))

    oclcs = []
    for future in futures:
        if future.result():
            oclcs.append(future.result())

    return oclcs

    # with open(oclc_num_file, "w") as outfile:
    #     for future in futures:
    #         if future.result():
    #             outfile.write(f"{future.result()}\n")

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

def main():
    # Obtain an OCLC Number with a barcode
    get_oclcs_to_file("tests/barcodes.txt", "tests/oclc.txt")

    # Load .env with API keys
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file)

    # Obtain an MMS ID using the OCLC number
    oclc = 19590300
    params = {
        "other_system_id": f"(OCoLC){oclc}",
        "apikey": getenv("BIB_KEY")
    }
    mms_id = get_mms_id_with_oclc(params)

    # Obtain all holdings information using the MMS ID
    new_params = {"apikey": getenv("BIB_KEY")}
    print(get_info_from_mms_id(mms_id, new_params))

if __name__ == "__main__":
    main()