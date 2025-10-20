import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

# --- Google Sheet Configuration ---
# IMPORTANT: Change this to the exact name of your Google Sheet
SHEET_NAME = "STUDENT-DETAILS"


@st.cache_resource(ttl=60)
def connect_to_gsheet():
    """
    Connects to the Google Sheet using credentials from st.secrets
    and returns the worksheet object.
    Caches the connection for 60 seconds.
    """
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Open the Google Sheet by its name and get the first tab
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def write_to_sheet(sheet, data_row: dict):
    """
    Appends a new row to the Google Sheet.
    'data_row' is a dictionary. The function will match dictionary keys
    to the header names in row 1 of the sheet.
    """
    try:
        # Get headers from the sheet (Row 1)
        headers = sheet.row_values(1)
        
        # --- Critical Step ---
        # Convert the face embedding (a list) into a JSON string
        # so it can be stored in a single cell.
        if "S_live_face_photos" in data_row:
            data_row["S_live_face_photos"] = json.dumps(data_row["S_live_face_photos"])
        
        # Create an ordered list of values based on the header order
        # Use .get(h, "") to avoid errors if a key is missing
        ordered_data = [data_row.get(h, "") for h in headers]
        
        # Append the new row to the sheet
        sheet.append_row(ordered_data)
        
        return True, "✅ Data saved to sheet successfully."
    except Exception as e:
        return False, f"⚠️ Error writing to sheet: {e}"

def read_from_sheet(sheet):
    """
    Reads all data from the sheet (except the header row)
    and returns it as a list of dictionaries.
    """
    try:
        # get_all_records() automatically uses row 1 as keys
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"⚠️ Error reading from sheet: {e}")
        return []

def clear_sheet(sheet):
    """
    Clears all data from the sheet *except* the header row (Row 1).
    """
    try:
        row_count = sheet.row_count
        if row_count > 1:
            # Delete all rows from 2 to the end
            sheet.delete_rows(2, row_count)
        return True
    except Exception as e:
        st.error(f"⚠️ Error clearing sheet: {e}")
        return False