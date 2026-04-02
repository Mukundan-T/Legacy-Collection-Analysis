"""
Define numerous functions to output numerical ranges and qualitative scores
for holdings information, both from Worldcat and Alma.

:author: Mukundan Thanigaivelan
"""

def process_date(year: int) -> tuple:
    """
    Given the year of a book, return the year range and the 
    qualitative score for this year.

    :param year: a year as an integer
    :return: a tuple with the range and score
    """
    ranges_and_scores = [
        (1700, '1000-1699', 4),
        (1800, '1700-1799', 4),
        (1820, '1800-1819', 3),
        (1850, '1820-1849', 2),
        (1900, '1850-1899', 1),
        (2000, '1900-1999', 1),
        (float('inf'), '2000-2040', 0)
    ]

    for threshold, range, score in ranges_and_scores:
        if year < threshold:
            return range, score

def process_holdings(holdings: int) -> tuple:
    """
    Given the number of holdings for a book, return the holdings range 
    and the qualitative score.

    :param holdings: number of holdings as an integer
    :return: a tuple with the range and score
    """
    ranges_and_scores = [
        (10, '01-09', 4),
        (20, '10-19', 3),
        (50, '20-49', 2),
        (100, '50-99', 1),
        (float('inf'), '100-3000', 0)
    ]

    for threshold, range, score in ranges_and_scores:
        if holdings < threshold:
            return range, score

def process_shared_print(shared_prints: int) -> tuple:
    """
    Given the number of shared prints for a book, return the shared prints range 
    and the qualitative score.

    :param shared_prints: number of shared prints as an integer
    :return: a tuple with the range and score
    """
    if shared_prints < 2:
        return '0-1', 4
    if shared_prints < 4:
        return '2-3', 2
    return '4-100', 0

def process_online_vers(online_versions: str) -> tuple:
    """
    Given the number of online versions for a book, return the online versions range 
    and the qualitative score.

    :param online_versions: number of online versions as an integer
    :return: a tuple with the range and score
    """
    if online_versions == "Info: Not found":
        return "No", 4
    return "Yes", 0

def process_alma_internal_note_east(note: str) -> tuple:
    """
    Given the Internal Note 2 value for a book, return the EAST/CNY information
    and the qualitative score.

    :param note: Internal Note 2 value as a string
    :return: a tuple with information and score
    """
    try:
        note = note.strip().lower()
    except:
        return "Unspecified", 2
    
    if note == "east retain":
        return "EAST", 4
    if note == "cny retain":
        return "Retain", 3
    if "east" not in note and "cny" not in note:
        return "Unspecified", 2
    if "cny unique item (withdraw candidate = false)" in note:
        return "WD-F", 1
    return "WD-T", 0

def process_alma_internal_note_loc(note: str) -> tuple:
    """
    Given the Internal Note 2 value for a book, return the local retention
    information and the qualitative score.

    :param note: Internal Note 2 value as a string
    :return: a tuple with information and score
    """
    try:
        note = note.strip().lower()
    except:
        return "No", 0
    
    return ("Yes", 4) if "local retention" in note else ("No", 0)