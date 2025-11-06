import streamlit as st
from PIL import Image
import datetime
import json
from connection_db import supabase
from utils.face_embedding import get_face_embedding 
from utils.g_spread import connect_to_gsheet, write_to_sheet 



# ----------------------------------- (Connect to sheet - no change) ----------------------------------------



try:
    sheet = connect_to_gsheet()
    if sheet is None: st.error("Registration database offline."); st.stop()
except Exception as e: st.error(f"Error connecting to registration database: {e}"); st.stop()

@st.cache_data(ttl=600)
def get_department_list():
    try:
        response = supabase.table("department").select("dep_id, dep_name").order("dep_name").execute()
        return response.data
    except Exception as e: st.error(f"Could not fetch department list: {e}"); return []





# ---------------------------------------- STUDENT FORM -------------------------------------------------------





def show_registration_form():
    st.title("🎓 New Student Registration")
    st.write("Please fill in your details and provide three clear photos of your face.")

    DEPARTMENTS = get_department_list()
    current_year = datetime.datetime.now().year
    
    
    

    # ------------------------- Use st.form for everything --------------------------------------------
    
    
    
    with st.form("student_registration_form", clear_on_submit=True):
        st.subheader("Student Details")
        s_name = st.text_input("Full Name", placeholder="Rupam Mondal")
        s_mail = st.text_input("Email", placeholder="abc@gmail.com")
        s_phone = st.text_input("Phone Number", placeholder="1524632890")
        max_dob = datetime.date(current_year - 15, 12, 31)
        min_dob = datetime.date(current_year - 100, 1, 1)
        default_dob = datetime.date(current_year - 20, 1, 1)
        s_dob = st.date_input("Date of Birth", value=default_dob, min_value=min_dob, max_value=max_dob)
        s_address = st.text_area("Address")
        col1, col2 = st.columns(2)
        with col1:
            selected_department = st.selectbox(
                "Department", options=DEPARTMENTS,
                format_func=lambda dept: dept.get('dep_name', 'N/A')
            )
        with col2:
            s_admisionYear = st.number_input("Admission Year", current_year - 10, current_year, current_year)
        st.markdown("---")



        # ------------------------------------- CAPTURE PHOTO ------------------------------------------------
        
        
        
        st.subheader("Live Face Photos")
        st.info("Provide 3 clear photos: Front, Left, and Right. (No hats or glasses) .")

        img_front = st.camera_input("1. Capture Front View", key="cam_front")
        img_left = st.camera_input("2. Capture Left View", key="cam_left")
        img_right = st.camera_input("3. Capture Right View", key="cam_right")
        

        st.markdown("---")
        submitted = st.form_submit_button("Submit Registration")

        if submitted:

            all_text_fields_values = [s_name, s_mail, s_phone, s_address, selected_department, s_admisionYear, s_dob]
            all_images = [img_front, img_left, img_right]

            
            if any(val is None or (isinstance(val, str) and not val.strip()) for val in all_text_fields_values):
                 st.warning("Please fill in all student details.")
                 
            
            elif not all(all_images):
                 st.warning("Please capture all 3 photos (Front, Left, Right).")
            else:
               
                with st.spinner("Analyzing photos..."):
                    all_embeddings = []
                    image_buffers = [img_front, img_left, img_right]
                    for i, current_img_buffer in enumerate(image_buffers):
                         image = Image.open(current_img_buffer)
                         embedding, message = get_face_embedding(image)
                         if embedding is None:
                             st.error(f"Error processing Photo {i+1}: {message}.")
                             
                             st.experimental_rerun() 
                             return 
                         all_embeddings.append(embedding)

                with st.spinner("Saving registration..."):
                    student_data = {
                        "S_name": s_name, "S_mail": s_mail, "S_phone": s_phone, "S_Address": s_address,
                        "dep_id": selected_department['dep_id'], "S_admisionYear": int(s_admisionYear),
                        "S_live_face_photos": all_embeddings, "S_dob": str(s_dob)
                    }
                    success, message = write_to_sheet(sheet, student_data)
                    if success:
                        st.success("✅ Registration Submitted!")
                        st.balloons()
                        
                    else:
                        st.error(f"Registration Failed: {message}")
                        

# --------------------------------------- (Main Router Logic) -------------------------------------



try:
    response = supabase.table("app_controls").select("is_registration_open").execute()
    if response.data: is_open = response.data[0].get("is_registration_open", False)
    else: is_open = False
    if is_open: show_registration_form()
    else: st.title("Registration Closed"), st.info("The registration form is not closed.")
except Exception as e: 
    st.info("concact with your respective HOD")