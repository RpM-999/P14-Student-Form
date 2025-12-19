Student Registration Form (Streamlit + Supabase + Google Sheets)
================================================================

[![license: MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10-blue.svg)](requirements.txt)
[![streamlit](https://img.shields.io/badge/Streamlit-Enabled-orange.svg)](https://streamlit.io)

🧭 Overview
-----------
- Streamlit app for collecting new student registrations with three live camera photos (front, left, right) and generating face embeddings for identity verification.
- Supabase supplies dynamic data (department list, registration toggle) and persists session state for the client connection.
- Google Sheets stores submitted student records, including serialized facial embeddings for downstream matching.

✨ Key Features
--------------
- Guided student form with validation for required fields, bounded DOB, and admission year range.
- Live camera capture for three angles and on-device face embedding via `facenet-pytorch` (InceptionResnetV1 + MTCNN).
- Dynamic departments pulled from Supabase; registration availability controlled via `app_controls.is_registration_open`.
- Writes ordered student rows to the `STUDENT-DETAILS` sheet with embeddings JSON-encoded.

📁 Project Structure
-------------------
- App UI & flow: [student_form.py](student_form.py)
- Supabase client bootstrap: [connection_db.py](connection_db.py)
- Face detection & embeddings: [utils/face_embedding.py](utils/face_embedding.py)
- Google Sheets integration: [utils/g_spread.py](utils/g_spread.py)
- Python deps: [requirements.txt](requirements.txt)
- Additional notes (empty by default): [DOCUMENTATION.md](DOCUMENTATION.md)

🗺️ Visual map (feel free to replace with an image):

```
P14-Student-Form
├─ student_form.py          # Streamlit app UI and flow
├─ connection_db.py         # Supabase bootstrap
├─ utils/
│  ├─ face_embedding.py     # Face detection + embeddings
│  └─ g_spread.py           # Google Sheets helper
├─ requirements.txt         # Python dependencies
└─ DOCUMENTATION.md         # Extra notes (optional)
```

🧰 Prerequisites
---------------
- Python 3.10+ recommended.
- A Supabase project with REST enabled.
- A Google Cloud service account with Sheets and Drive API access.
- (Optional) GPU-accelerated PyTorch for faster face embedding; CPU works but is slower.

⚙️ Setup
--------
1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2) Configure Streamlit secrets

Create `.streamlit/secrets.toml` with your keys:

```toml
[supabase]
url = "https://YOUR-PROJECT.supabase.co"
anon_key = "SUPABASE_ANON_KEY"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@your-project-id.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40your-project-id.iam.gserviceaccount.com"
```

3) Prepare Google Sheet

- Create a sheet named `STUDENT-DETAILS` and share it with the service account email.
- Set the header row (row 1) to at least: `S_name`, `S_mail`, `S_phone`, `S_Address`, `dep_id`, `S_admisionYear`, `S_live_face_photos`, `S_dob`.

4) Configure Supabase tables

- `department` table: `dep_id` (int, PK), `dep_name` (text). Populate rows for the select box.
- `app_controls` table: `is_registration_open` (bool). Set `true` to allow the form, `false` to show “Registration Closed”.

▶️ Run the App
--------------

```bash
streamlit run student_form.py
```

📝 Usage
-------
- Open the served URL; fill student details, choose department, and set admission year.
- Capture three clear photos (front/left/right); embeddings compute automatically before submission.
- On success the app shows a green check and triggers balloons; failures surface inline error messages.

🖼️ Screenshots
--------------
- Form preview (replace with your capture):

	![Student registration form](docs/form-ui.png)

- Google Sheet record view (replace with your capture):

	![Student record in sheet](docs/sheet-record.png)

Store screenshots under `docs/` and update the image paths if you choose a different location.

🔄 Workflow
----------
- Data entry ➜ Photo capture (front/left/right) ➜ Face embeddings ➜ Validation ➜ Save to Sheets
- You can embed a visual pipeline here (replace with your own image):

	![Project workflow](docs/workflow.png)

🛟 Operational Notes
-------------------
- Face capture requires camera permissions in the browser; ensure lighting and an unobstructed face.
- If you see “Registration database offline,” confirm Sheets access and secrets configuration.
- If embeddings fail with “No face detected,” retake photos with a centered, well-lit face.
- All secrets must be supplied through `.streamlit/secrets.toml`; avoid hard-coding keys.

🔗 Live Demo
-----------
- (Optional) Publish your Streamlit app and link it here: https://share.streamlit.io/your-app

📜 License
---------
- Provide your license terms here (e.g., MIT, Apache-2.0).

👩‍💻 Developed By
-----------------
- Rupam Mondal
- Email: mailto:your-email@example.com
- LinkedIn: https://www.linkedin.com/in/your-handle
