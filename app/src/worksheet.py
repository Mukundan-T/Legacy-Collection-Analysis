"""
Define methods to style, format, and save the Excel workbook created as the result
of running this program.

:authors: Mukundan Thanigaivelan, Mustarshid Choudhary
"""

from openpyxl.worksheet.worksheet import Worksheet
from openpyxl import Workbook
from tkinter import Tk, filedialog
from os import startfile

def initialize_sheet(work_book: Workbook) -> Worksheet:
    """
    Add the headings to each column in the new Excel sheet.

    :param work_book: the workbook Excel
    :return: a new work sheet with column headings
    """
    work_sheet = work_book.active
    work_sheet.title = "Book Records"

    work_sheet.append(["[Alma] Call Number", "[Alma] Description", "[OCLC] Title", "[Alma] Title", 
                       "[OCLC] Edition", "[OCLC] Publisher", "[Alma] Publisher", "[OCLC] Date 1", 
                       "[OCLC] Date 2", "[Alma] Publication Date", "[Alma] Publication Place",
                       "[OCLC] Holdings", "[OCLC] Shared Prints", "[OCLC] Online Versions", 
                       "[Alma] Internal Note 1", "[Alma] Internal Note 2", "[OCLC] Record Source",
                       "[Alma] Material Type", "[OCLC] OCLC Number", "[Alma] OCLC Number", 
                       "[Alma] MMS ID", "[Alma] Holdings ID", "[Alma] Item ID", "[Alma] Barcode", 
                       "[Alma] Location", "Summed Score", "[OCLC] Date 1 Date Score", 
                       "[OCLC] Holdings Holding Score", "[OCLC] Shared Print Shared Score", 
                       "[OCLC] Online Versions Online Score", "[Alma] Internal Note 2 EAST Score",
                       "[Alma] Internal Note 2 Local Score",  "[OCLC] Date 1 Date Range", 
                       "[OCLC] Holdings Holding Range", "[OCLC] Shared Print Shared Range", 
                       "[OCLC] Online Versions Online Range", "[Alma] Internal Note 2 EAST/CNY", 
                       "[Alma] Internal Note 2 Local"])

    return work_sheet

def set_column_widths(work_sheet: Worksheet) -> None:
    """
    Set the width for each column in the Excel spreadsheet.

    :param work_sheet: the Excel spreadsheet
    """
    column_widths = {
        'A': 22, 'B': 50, 'C': 75, 'D': 75, 'E': 20, 'F': 30,
        'G': 30, 'H': 15, 'I': 15, 'J': 25, 'K': 25, 'L': 15,
        'M': 20, 'N': 25, 'O': 30, 'P': 30, 'Q': 20, 'R': 20,
        'S': 20, 'T': 20, 'U': 20, 'V': 20, 'W': 20, 'X': 20,
        'Y': 20, 'Z': 14, 'AA': 22, 'AB': 28, 'AC': 28, 'AD': 32, 
        'AE': 32, 'AF': 32, 'AG': 28, 'AH': 28, 'AI': 32, 
        'AJ': 32, 'AK': 32, 'AL': 28
    }

    for column, width in column_widths.items():
        work_sheet.column_dimensions[column].width = width

def select_result_location() -> str:
    """
    Return the path to the new Excel file (where it should be saved).

    :return: a string containing the path to the new Excel file
    """
    root = Tk()
    root.withdraw()

    save_path = filedialog.asksaveasfilename(
        defaultextension = ".xlsx",
        filetypes = [("Excel files", "*.xlsx")],
        title = "Save Excel File As..."
    )

    return save_path

def save_new_sheet(path: str, work_book: Workbook):
    """
    Save the new Excel spreadsheet to the indicated directory. If the 
    save was canceled, return None.

    :param path: the path to the directory
    :param work_book: the workbook Excel
    :return: the path to the Excel spreadsheet, None if the save 
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