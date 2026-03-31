import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json



# <--------------------- Make sure this is your exact sheet name ----------------------------------->



SHEET_NAME = "STUDENT DETAILS"                      

@st.cache_resource(ttl=60)

def connect_to_gsheet():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def write_to_sheet(sheet, data_row: dict):
    try:
        headers = sheet.row_values(1)
        
        if "S_live_face_photos" in data_row:
            data_row["S_live_face_photos"] = json.dumps(data_row["S_live_face_photos"])
        if "STUDENT_PHOTO_EMBEDDING" in data_row:
            data_row["STUDENT_PHOTO_EMBEDDING"] = json.dumps(data_row["STUDENT_PHOTO_EMBEDDING"])
        
        # Convert date to string
        if "S_dob" in data_row:
            data_row["S_dob"] = str(data_row["S_dob"])
        if "STUDENT_DOB" in data_row:
            data_row["STUDENT_DOB"] = str(data_row["STUDENT_DOB"])

        ordered_data = [data_row.get(h, "") for h in headers]
        sheet.append_row(ordered_data)
        
        return True, "✅ Data saved to sheet successfully."
    except Exception as e:
        return False, f"⚠️ Error writing to sheet: {e}"