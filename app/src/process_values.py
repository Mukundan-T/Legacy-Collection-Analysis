"""
Define functions to obtain the ranges and scores for the Worldcat and Alma holdings
information, and arrange them properly.

:author: Mukundan Thanigaivelan
"""

from analytics import *

def get_ranges_and_scores(worldcat_values: list, alma_values: list) -> tuple:
    """
    Using the given Worldcat and Alma information, obtain the ranges
    and scores for the correct fields and return them in 2 lists.

    :param worldcat_values: a list of Worldcat information
    :param alma_values: a list of Alma information
    :return: a tuple of 2 lists
    """
    date1 = int(worldcat_values[3])
    holdings = int(worldcat_values[5])
    shared_print = int(worldcat_values[6])
    online_vers = worldcat_values[7]
    internal_note2 = alma_values[7]

    date1_range, date1_score = process_date(date1)
    holdings_range, holdings_score = process_holdings(holdings)
    shared_print_range, shared_print_score = process_shared_print(shared_print)
    online_vers_range, online_vers_score = process_online_vers(online_vers)
    internal_note2_east_range, internal_note2_east_score = process_alma_internal_note_east(internal_note2)
    internal_note2_loc_range, internal_note2_loc_score = process_alma_internal_note_loc(internal_note2)

    ranges = [date1_range, holdings_range, shared_print_range, 
              online_vers_range, internal_note2_east_range, 
              internal_note2_loc_range]
    
    scores = [date1_score, holdings_score, shared_print_score, 
              online_vers_score, internal_note2_east_score, 
              internal_note2_loc_score]
    
    return ranges, scores

def arrange_info(worldcat_info: list, alma_info: list, ranges: list, scores: list) -> list:
    """
    Given the Worldcat and Alma information in addition to the ranges and scores
    that are relevant, rearrange the information and return a list of all the
    information (this will be one row in the spreadsheet).
    
    :param worldcat_info: A list of field values obtained from WorldCat
    :param alma_info: A list of field values obtained from Alma
    :param ranges: a list of ranges
    :param scores: a list of scores
    :return: a list that rearranges all this information correctly
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

    [date1_range, holdings_range, shared_print_range, 
     online_vers_range, internal_note2_east_range, 
     internal_note2_loc_range] = ranges

    [date1_score, holdings_score, shared_print_score, 
     online_vers_score, internal_note2_east_score, 
     internal_note2_loc_score] = scores

    sum_of_scores = sum(scores)

    return [perm_call_num, item_element_desc, title_details, title, edition_details, 
            publisher_details, publisher, date_one_details, date_two_details, 
            publication_date, publication_place, holdings, sharedprints, 
            online_version_details, internal_note1, internal_note2, record_source_details, 
            material_type, wc_oclc_number, al_oclc_num, mms_id, holdings_id, item_id, 
            barcode, location, sum_of_scores, date1_score, holdings_score, shared_print_score, 
            online_vers_score, internal_note2_east_score, internal_note2_loc_score, 
            date1_range, holdings_range, shared_print_range, online_vers_range, 
            internal_note2_east_range, internal_note2_loc_range]