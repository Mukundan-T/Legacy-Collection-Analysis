"""
Define a set of functions to query the Worldcat API and parse its output 
to extract meaningful information.

:authors: Mustarshid Choudhary, Mukundan Thanigaivelan
"""

from bookops_worldcat.authorize import WorldcatAccessToken
from bookops_worldcat.metadata_api import MetadataSession
import xml.etree.cElementTree as ET
from dotenv import load_dotenv
from os import getenv

def verify_token(filepath: str) -> tuple:
    """
    Given a .env file with the valid API credentials, create and return a
    WorldcatAccessToken and the Alma API key.

    :return: a WorldcatAccessToken and the Alma API key
    """
    load_dotenv(filepath)

    token = WorldcatAccessToken(
        key = getenv("API_KEY"),
        secret = getenv("API_SECRET"),
        scopes = getenv("API_SCOPES")
    )

    return token, getenv('BIB_KEY')

def get_all_worldcat_details(data: dict, xml_str: str) -> list:
    """
    Find and return all of the details pertaining to the given OCLC number.

    :param data: a dictionary containing all information
    :param xml_str: a string containing the XML data
    :return: a list containing all of the details pertaining to the OCLC 
    number in the order that they appear in the Excel sheet
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
        subfields = publisher_new.findall("marc:subfield[@code='b']", ns)
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

def get_record_and_holding_info(token: WorldcatAccessToken, oclc_num: str) -> tuple:
    """
    Given the token and an oclc_num, use the WorldCatMetadataAPI to get the records
    and the holdings information for the OCLC number and return them.

    :param token: a WorldCatAccessToken
    :param oclc_num: the current OCLC number in the given input file
    :return: a tuple of a string with XML content and data as a dictionary
    """
    with MetadataSession(authorization = token) as session:
        result = session.bib_get(oclc_num)
        response = session.summary_holdings_get(oclc_num)
    
    xml_str = result.text
    data = response.json()

    return xml_str, data