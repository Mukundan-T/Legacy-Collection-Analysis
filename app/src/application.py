"""
The main logic for the program. Uses a text file of barcodes to convert to an Excel
file of information.

:authors: Mukundan Thanigaivelan, Mustarshid Choudhary
"""

from bookops_worldcat.authorize import WorldcatAccessToken
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from openpyxl import Workbook
from os import getenv

from worldcat_holdings import *
from alma_holdings import *
from process_values import *
from worksheet import *

def get_row(token: WorldcatAccessToken, oclc: str, bib_key: str) -> list:
    """
    Get the information for a new row to be added to the worksheet being created 
    with holdings information for the current OCLC number.

    :param token: a WorldCatAccessToken
    :param oclc: current OCLC number
    :param bib_key: Bibliographic key for Alma
    :return: a list that will be appended to the Excel worksheet
    """
    xml_str, data = get_record_and_holding_info(token, oclc)
    worldcat_details = get_all_worldcat_details(data, xml_str)

    params = {
        "other_system_id": f"(OCoLC){oclc}",
        "apikey": bib_key
    }
    mms_id = get_mms_id_with_oclc(params)
    new_params = {"apikey": getenv("BIB_KEY")}
    alma_details = get_info_from_mms_id(mms_id, new_params)

    ranges, scores = get_ranges_and_scores(worldcat_details, alma_details)
    combined_info = arrange_info(worldcat_details, alma_details, ranges, scores)

    return combined_info

def build_sheet(input_file: str) -> str:
    """
    Run the program for every barcode in the input file.

    :param input_file: a text file of barcodes
    :return: a string containing the path to the new Excel spreadsheet
    """
    credential_file = Path(__file__).resolve().parent.parent / ".env"
    token, bib_key = verify_token(credential_file)

    work_book = Workbook()
    work_sheet = initialize_sheet(work_book)
    oclcs = get_all_oclcs(input_file)

    rate_limit = 10
    with ThreadPoolExecutor(max_workers = rate_limit) as executor:
        futures = [executor.submit(get_row, token, oclc, bib_key) for oclc in oclcs]
        for future in futures:
            result = future.result()
            work_sheet.append(result)
    
    set_column_widths(work_sheet)
    save_path = select_result_location()
    return save_new_sheet(save_path, work_book)