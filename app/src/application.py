"""
The main logic for the program. Uses a text file of identifiers to convert to an Excel
file of information.

:authors: Mukundan Thanigaivelan, Mustarshid Choudhary
"""

from bookops_worldcat.authorize import WorldcatAccessToken
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from openpyxl import Workbook

from worldcat_holdings import *
from alma_holdings import *
from process_values import *
from worksheet import *

def get_row(
    token: WorldcatAccessToken, 
    bib_key: str,
    identifier: str,
    id_type: str
) -> list:
    """
    Get the information for a new row to be added to the worksheet being created 
    with holdings information for the current item ID.

    :param token: a WorldCatAccessToken
    :param bib_key: bibliographic key for Alma
    :param identifier: either a barcode, OCLC #, or Item PID
    :param id_type: string specifying which type of ID this is
    :return: a list that will be appended to the Excel worksheet
    """
    # Get MMS id and OCLC
    if id_type == "Barcode":
        mms_id = get_mms_id(barcode = identifier)
        oclc = get_oclc(mms_id)
    elif id_type == "Item PID":
        mms_id = get_mms_id(pid = identifier)
        oclc = get_oclc(mms_id)
    elif id_type == "OCLC Number":
        oclc = identifier
        mms_id = get_mms_id(oclc = oclc)

    # Get Worldcat data with OCLC number
    xml_str, data = get_record_and_holding_info(token, oclc)
    worldcat_details = get_all_worldcat_details(data, xml_str)

    # Get Alma data with MMS ID
    alma_details = get_info_from_mms_id(mms_id, {"apikey": bib_key})

    # Get ranges/scores with fetched data
    ranges, scores = get_ranges_and_scores(worldcat_details, alma_details)
    combined_info = arrange_info(worldcat_details, alma_details, ranges, scores)

    # Return a formatted row
    return combined_info

def build_sheet(input_file: str, file_type: str) -> str:
    """
    Run the program for every ID in the input file.

    :param input_file: a text file of either barcodes, PIDs, or OCLC #s
    :param file_type: a string specifying which type of IDs file has
    :return: a string containing the path to the new Excel spreadsheet
    """
    credential_file = Path(__file__).resolve().parent.parent / ".env"
    token, bib_key = verify_token(credential_file)

    work_book = Workbook()
    work_sheet = initialize_sheet(work_book)

    with open(input_file, 'r', encoding='utf-8') as file:
        ids = [line.rstrip('\n') for line in file]

    rate_limit = 10
    with ThreadPoolExecutor(max_workers = rate_limit) as executor:
        futures = [
            executor.submit(get_row, token, bib_key, identifier, file_type) 
            for identifier in ids
        ]
        for future in futures:
            result = future.result()
            work_sheet.append(result)
    
    set_column_widths(work_sheet)
    save_path = select_result_location()
    return save_new_sheet(save_path, work_book)
