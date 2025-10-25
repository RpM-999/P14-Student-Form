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
        return [] # Return empty list on error

def show_registration_form():
    st.title("🎓 New Student Registration")
    st.write("Please fill in your details and provide three clear photos of your face.")

    DEPARTMENTS = get_department_list()
    current_year = datetime.datetime.now().year
    
    max_dob = datetime.date(current_year - 15, 12, 31)
    min_dob = datetime.date(current_year - 100, 1, 1)
    default_dob = datetime.date(current_year - 20, 1, 1)

    with st.form("student_registration_form",clear_on_submit=True):
        st.subheader("Student Details")
        
        s_name = st.text_input("Full Name", placeholder="Rupam Mondal")
        s_mail = st.text_input("Email", placeholder="abc@gmail.com")
        s_phone = st.text_input("Phone Number", placeholder="1524632890")
        s_dob = st.date_input("Date of Birth",default_dob,min_value=min_dob,max_value=max_dob)
        s_address = st.text_area("Address")

        col1, col2 = st.columns(2)
        
        with col1:
            selected_department = st.selectbox(
                "Department", 
                options=DEPARTMENTS, 
                # Use .get() for safety in case dep_name is missing
                format_func=lambda dept: dept.get('dep_name', 'N/A')
            )
        
        with col2:
            s_admisionYear = st.number_input("Admission Year",
                                              current_year - 10, current_year, current_year)
            
        st.markdown("---")
    
        st.subheader("Live Face Photos")
        st.info("Provide 3 clear photos: Front, Left, and Right. (No hats or glasses)")
        
        capture_label = ""
        camera_key = ""
        
        if st.session_state.img_front_data is None:
            capture_label = "1. Capture Front View"
            camera_key = "cam_front_seq"
        elif st.session_state.img_left_data is None:
            capture_label = "2. Capture Left View"
            camera_key = "cam_left_seq"
        elif st.session_state.img_right_data is None:
            capture_label = "3. Capture Right View"
            camera_key = "cam_right_seq"
        else:
            st.success("All 3 photos captured!")
            capture_label = None
            
        img_buffer = None
        if capture_label:
            img_buffer = st.camera_input(capture_label, key=camera_key)
        
        
        st.write("Captured Photos:")
        prev_col1, prev_col2, prev_col3 = st.columns(3)
        with prev_col1:
            if st.session_state.img_front_data:
                st.image(st.session_state.img_front_data, caption="Front View", width=150)
            else:
                st.caption("Front View (Pending)")
        with prev_col2:
            if st.session_state.img_left_data:
                st.image(st.session_state.img_left_data, caption="Left View", width=150)
            else:
                st.caption("Left View (Pending)")
        with prev_col3:
            if st.session_state.img_right_data:
                st.image(st.session_state.img_right_data, caption="Right View", width=150)
            else:
                st.caption("Right View (Pending)")
                
        st.markdown("---")
        submit_button = st.form_submit_button("Submit Registration")
        
    if img_buffer is not None:
        if camera_key == "cam_front_seq" and st.session_state.img_front_data is None:
            st.session_state.img_front_data = img_buffer
            st.rerun() # Rerun immediately to update previews and show next camera prompt
        elif camera_key == "cam_left_seq" and st.session_state.img_left_data is None:
            st.session_state.img_left_data = img_buffer
            st.rerun()
        elif camera_key == "cam_right_seq" and st.session_state.img_right_data is None:
            st.session_state.img_right_data = img_buffer
            st.rerun()

    
    if submit_button:
        
        img_front = st.session_state.img_front_data
        img_left = st.session_state.img_left_data
        img_right = st.session_state.img_right_data
        all_images = [img_front, img_left, img_right]
        
        
        all_text_fields = [s_name, s_mail, s_phone, s_address, selected_department, s_admisionYear, s_dob]
        

        if not all(all_text_fields):
            st.warning("Please fill in all student details.")
        elif not all(all_images):
            st.warning("Please take all 3 photos.")
        else:
            with st.spinner("Analyzing photos... Please wait."):
                all_embeddings = []
                image_buffers = [img_front, img_left, img_right]
                
                for i, img_buffer in enumerate(image_buffers):
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
                    "S_dob": str(s_dob)  # <-- IMPORTANT: Convert date to string
                }
                
                success, message = write_to_sheet(sheet, student_data)
                
                if success:
                    st.success("✅ Registration Submitted! An admin will review your application.")
                    st.balloons()
                    st.session_state.img_front_data = None
                    st.session_state.img_left_data = None
                    st.session_state.img_right_data = None
                else:
                    st.error(f"Registration Failed: {message}")

# --- 5. Main "Router" Logic ---
try:
    # --- THIS IS THE FIXED CODE BLOCK ---
    # Fetch the list of results (even though there's only one)
    response = supabase.table("app_controls").select("is_registration_open").execute()
    
    # Check if data was returned and get the value from the first dictionary
    if response.data:
        is_open = response.data[0].get("is_registration_open", False)
    else:
        is_open = False # Default to closed if no data is found
    # ------------------------------------

    if is_open:
        show_registration_form()
    else:
        st.title("Registration Closed")
        st.info("The student registration form is not open at this time. Please check back later.")
except Exception as e:
    st.error(f"System error. Could not check registration status: {e}")