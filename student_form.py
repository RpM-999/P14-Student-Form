import streamlit as st
from PIL import Image
import datetime
import json

# --- Import our custom utilities ---
from connection_db import supabase
from utils.face_embedding import get_face_embedding
from utils.g_spread import connect_to_gsheet, write_to_sheet


try:
    sheet = connect_to_gsheet()
    if sheet is None:
        st.error("Registration database is offline. Please try again later.")
        st.stop()
except Exception as e:
    st.error(f"Error connecting to registration database: {e}")
    st.stop()

@st.cache_data(ttl=600) 
def get_department_list():
    
    try:
        response = supabase.table("department").select("dep_id, dep_name").order("dep_name").execute()
        
        return response.data
    
    except Exception as e:
        st.error(f"Could not fetch department list: {e}")
        return ["Error: Could not load departments"]

def show_registration_form():
    st.title("🎓 New Student Registration")
    st.write("Please fill in your details and provide three clear photos of your face.")

    DEPARTMENTS = get_department_list()
    current_year = datetime.datetime.now().year

    with st.form("student_registration_form"):
        st.subheader("Student Details")
        
        s_name = st.text_input("Full Name ",placeholder="Rupam Mondal")
        s_mail = st.text_input("Email " , placeholder="abc@gmail.com")
        s_phone = st.text_input("Phone Number",placeholder="1524632890")
        s_dob = st.date_input("Date of Birth")
        s_address = st.text_area("Address")

        col1, col2 = st.columns(2)
        
        with col1:
            selected_department = col1.selectbox(
                
                "Department", 
                options=DEPARTMENTS, 
                format_func=lambda dept: dept['dep_name']
            )
        
        
        
        s_admisionYear = col2.number_input("Admission Year (S_admisionYear)",
                                          current_year - 10, current_year, current_year)
    
        st.subheader("Live Face Photos")
        st.info("Provide 3 clear photos: Front, Left, and Right. (No hats or glasses)")
        
        col_img1, col_img2, col_img3 = st.columns(3)
        img_front = col_img1.camera_input("1. Front View", key="cam_front")
        img_left = col_img2.camera_input("2. Left View", key="cam_left")
        img_right = col_img3.camera_input("3. Right View", key="cam_right")

    submit_button = st.form_submit_button("Submit Registration")

    
    if submit_button:
        all_fields = [s_name, s_mail, s_phone, s_address, selected_department, s_admisionYear, s_dob]
        all_images = [img_front, img_left, img_right]

        if not all(all_fields):
            st.warning("Please fill in all student details.")
        elif not all(all_images):
            st.warning("Please take all 3 photos.")
        else:
            with st.spinner("Analyzing photos... Please wait."):
                all_embeddings = []
                for i, img_buffer in enumerate(all_images):
                    image = Image.open(img_buffer)
                    embedding, message = get_face_embedding(image)
                    
                    if embedding is None:
                        st.error(f"Error with Photo {i+1} ({message}).")
                        st.stop()
                    all_embeddings.append(embedding)

            with st.spinner("Saving registration..."):
                student_data = {
                    "S_name": s_name,
                    "S_mail": s_mail,
                    "S_phone": s_phone,
                    "S_Address": s_address,
                    "dep_id": selected_department['dep_id'],
                    "S_admisionYear": int(s_admisionYear),
                    "S_live_face_photos": all_embeddings,
                    "S_dob": s_dob 
                }
                
                success, message = write_to_sheet(sheet, student_data)
                
                if success:
                    st.success("✅ Registration Submitted! An admin will review your application.")
                    st.balloons()
                else:
                    st.error(f"Registration Failed: {message}")

# --- 5. Main "Router" Logic ---
try:
    # Check the flag in Supabase. Assumes table has only one row with id=1
    response = supabase.table("app_controls").select("is_registration_open").single().execute()
    is_open = response.data.get("is_registration_open", False)

    if is_open:
        show_registration_form()
    else:
        st.title("Registration Closed")
        st.info("The student registration form is not open at this time. Please check back later.")
except Exception as e:
    st.error(f"System error. Could not check registration status: {e}")