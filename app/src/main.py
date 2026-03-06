from alma_holdings import get_oclcs, get_info_from_mms_id, get_mms_id_with_oclc
from bookops_worldcat.authorize import WorldcatAccessToken
from bookops_worldcat.metadata_api import MetadataSession
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from tkinter import Tk, filedialog
from os import getenv, startfile
from pathlib import Path
import xml.etree.cElementTree as ET
import openpyxl as op

def verify_token(filepath):
    """
    Given a .env file with the valid API credentials, create and return a
    WorldcatAccessToken.

    :return: a WorldcatAccessToken
    """
    load_dotenv(filepath)

    token = WorldcatAccessToken(
        key = getenv("API_KEY"),
        secret = getenv("API_SECRET"),
        scopes = getenv("API_SCOPES")
    )

    print(token)
    print("Is expired: " + str(token.is_expired()))

    return token, getenv('BIB_KEY')

def initialize_sheet(work_book):
    """
    Add the headings to each column in the new excel sheet.

    :param work_book: the workbook excel
    :return: a new work sheet with column headings
    """
    work_sheet = work_book.active
    work_sheet.title = "Book Records"

    work_sheet.append(["[Alma] Call Number", "[Alma] Description",
                       "[OCLC] Title", "[Alma] Title", "[OCLC] Edition",
                       "[OCLC] Publisher", "[Alma] Publisher", 
                       "[OCLC] Date 1", "[OCLC] Date 2", 
                       "[Alma] Publication Date", "[Alma] Publication Place",
                       "[OCLC] Holdings", "[OCLC] Shared Prints", 
                       "[OCLC] Online Versions", "[Alma] Internal Note 1",
                       "[Alma] Internal Note 2", "[OCLC] Record Source",
                       "[Alma] Material Type", "[OCLC] OCLC Number", 
                       "[Alma] OCLC Number", "[Alma] MMS ID", 
                       "[Alma] Holdings ID", "[Alma] Item ID", 
                       "[Alma] Barcode", "[Alma] Location"])

    return work_sheet

def get_all_worldcat_details(data, xml_str):
    """
    Find and return all of the details pertaining to the given OCLC number.

    :param data: a dictionary containing all information
    :param xml_str: a string containing the XML data
    :return: a list containing all of the details pertaining to the OCLC 
    number in the order that they appear in the excel sheet
    """
    # Holdings extraction
    holdings = data['totalHoldingCount']
    sharedprints = data['totalSharedPrintCount']

    root = ET.fromstring(xml_str)
    ns = {'marc': 'http://www.loc.gov/MARC21/slim'}

    # OCLC number extraction
    oclc = root.find("marc:controlfield[@tag='001']", ns)

    oclc_number = oclc.text if oclc is not None else "Not found"
    oclc_number = '#' + oclc_number[3:]

    # online_versions extration
    online_versions = root.find("marc:datafield[@tag='776']", ns)

    if online_versions is not None:
        subfields = online_versions.findall("marc:subfield[@code='w']", ns)
        online_version_details = " ".join(sub.text for sub in subfields if sub.text)
    else:
        online_version_details = "Info: Not found"

    # Title extration
    title = root.find("marc:datafield[@tag='245']", ns)

    if title is not None:
        subfields = title.findall("marc:subfield",ns)
        title_details = " ".join(sub.text for sub in subfields if sub.text)
    else:
        title_details = "No title found"

    # Edition extraction
    edition = root.find("marc:datafield[@tag='250']",ns)

    if edition is not None:
        subfields = edition.findall("marc:subfield", ns)
        edition_details = " ".join(sub.text for sub in subfields if sub.text)
    else:
        edition_details = "-"

    # Publisher extraction only subfield b
    publisher_old = root.find("marc:datafield[@tag='260']", ns)
    publisher_new = root.find("marc:datafield[@tag='264']", ns)

    if publisher_old is not None and publisher_new is None:
        subfields = publisher_old.findall("marc:subfield[@code='b']", ns)
        publisher_details = " ".join(sub.text for sub in subfields if sub.text)

    elif publisher_old is None and publisher_new is not None:
        subfields = publisher_new.findall("marc:subfield[@code='b']", ns)  # FIXED: same as above
        publisher_details = " ".join(sub.text for sub in subfields if sub.text)

    else:
        publisher_details = "-"

    # Date extraction
    date_one = root.find("marc:controlfield[@tag='008']", ns)

    date_details = date_one.text if date_one is not None else "Not found"
    date_one_details = date_details[7:11]
    date_two_details = date_details[11:15]

    # Record source extraction
    record_source = root.find("marc:datafield[@tag='040']", ns)

    if record_source is not None:
        subfield = record_source.findall("marc:subfield[@code='a']",ns)
        record_source_details = " ".join(sub.text for sub in subfield if sub.text)
    else:
        record_source_details = "Not Found"

    return [title_details, edition_details, publisher_details, 
            date_one_details, date_two_details, holdings, 
            sharedprints, online_version_details, 
            record_source_details, oclc_number]

def set_column_widths(work_sheet):
    """
    Set the width for each column in the excel spreadsheet.

    :param work_sheet: the excel spreadsheet
    """
    column_widths = {
        'A': 20, 'B': 50, 'C': 75, 'D': 75, 'E': 20, 'F': 30,
        'G': 30, 'H': 15, 'I': 15, 'J': 25, 'K': 25, 'L': 15,
        'M': 20, 'N': 25, 'O': 30, 'P': 30, 'Q': 20, 'R': 20,
        'S': 20, 'T': 20, 'U': 20, 'V': 20, 'W': 20, 'X': 20,
        'Y': 20
    }

    for column, width in column_widths.items():
        work_sheet.column_dimensions[column].width = width

def select_result_location():
    """
    Return the path to the new Excel file (where it should be saved).

    :return: a string containing the path to the new excel file
    """
    root = Tk()
    root.withdraw()

    save_path = filedialog.asksaveasfilename(
        defaultextension = ".xlsx",
        filetypes = [("Excel files", "*.xlsx")],
        title = "Save Excel File As..."
    )

    return save_path

def save_new_sheet(path, work_book):
    """
    Save the new excel spreadsheet to the indicated directory. If the 
    save was canceled, return None.

    :param path: the path to the directory
    :param work_book: the workbook excel
    :return: the path to the excel spreadsheet, None if the save 
    was canceled
    """
    if path:
        work_book.save(path)
        print(f"Excel file saved to: {path}")
        startfile(path)
        return path
    else:
        print("Save canceled.")
        return None

def get_record_and_holding_info(token, oclc_num):
    """
    Given the token and an oclc_num, use the WorldcatMetadataAPI to get the records
    and the holdings information for the OCLC number, and return them.

    :param token: a WorldCatAccessToken
    :param oclc_num: the current OCLC number in the given input file
    :return: a tuple of two Response objects, the first being the result and 
    the second being the response
    """
    with MetadataSession(authorization = token) as session:
        result = session.bib_get(oclc_num)
        response = session.summary_holdings_get(oclc_num)
    
    xml_str = result.text
    data = response.json()

    return xml_str, data

def arrange_info(worldcat_info, alma_info):
    """
    Docstring for arrange_info
    
    :param worldcat_info: A list of field values obtained from WorldCat
    :param alma_info: A list of field values obtained from Alma
    """
    [title_details, edition_details, publisher_details, 
     date_one_details, date_two_details, holdings, 
     sharedprints, online_version_details, 
     record_source_details, wc_oclc_number
     ] = worldcat_info
    
    [title, perm_call_num, item_element_desc, publisher, 
     publication_date, publication_place, internal_note1, 
     internal_note2, material_type, al_oclc_num, mms_id, 
     holdings_id, item_id, barcode, location] = alma_info
    
    return [perm_call_num, item_element_desc, title_details, 
            title, edition_details, publisher_details, publisher,
            date_one_details, date_two_details, publication_date,
            publication_place, holdings, sharedprints, 
            online_version_details, internal_note1, internal_note2,
            record_source_details, material_type, wc_oclc_number, 
            al_oclc_num, mms_id, holdings_id, item_id, barcode, 
            location]

def add_row(token, oclc, bib_key, ws):
    """
    Add a new row to the worksheet being created with holdings information for
    the current OCLC number.

    :param token: a WorldCatAccessToken
    :param oclc: current OCLC number
    :param bib_key: Bibliographic key for Alma
    :param ws: worksheet being created
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

    ws.append(arrange_info(worldcat_details, alma_details))

def run_program(input_file):
    """
    Run the script for every OCLC number in the input text file.

    :param input_file: a text file of OCLC numbers
    :return: a string containing the path to the new excel spreadsheet
    """
    credential_file = Path(__file__).resolve().parent.parent / ".env"
    token, bib_key = verify_token(credential_file)

    work_book = op.Workbook()
    work_sheet = initialize_sheet(work_book)
    oclcs = get_oclcs(input_file)

    rate_limit = 10
    with ThreadPoolExecutor(max_workers = rate_limit) as executor:
        for oclc in oclcs:
            executor.submit(add_row, token, oclc, bib_key, work_sheet)
    
    set_column_widths(work_sheet)
    save_path = select_result_location()
    return save_new_sheet(save_path, work_book)