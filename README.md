# 🎓 P14 Student Registration Form

A modern, intelligent student registration system built with Streamlit that captures student information along with facial recognition data for enhanced security and identification.

## 📋 Overview

This application provides a web-based interface for new student registration with integrated facial recognition technology. It captures student details, department information, and uses advanced AI to create face embeddings for future identification purposes.

## ✨ Features

- **📝 Comprehensive Student Form**: Capture all essential student information including name, email, phone, date of birth, and address
- **🏫 Department Integration**: Dynamic department selection integrated with Supabase database
- **📸 Live Face Capture**: Real-time face photo capture (Front, Left, and Right views) using device camera
- **🤖 AI-Powered Face Recognition**: Utilizes FaceNet (InceptionResnetV1) with MTCNN for face detection and embedding generation
- **☁️ Cloud Storage**: Automatic data storage in Google Sheets for easy access and management
- **🔐 Registration Control**: Admin-controlled registration open/close functionality via Supabase
- **✅ Input Validation**: Comprehensive validation for all form fields and image captures
- **🎨 User-Friendly UI**: Clean, intuitive interface built with Streamlit

## 🛠️ Tech Stack

- **Frontend Framework**: [Streamlit](https://streamlit.io/) - Fast web app development
- **Face Detection**: [MTCNN](https://github.com/timesler/facenet-pytorch) - Multi-task Cascaded Convolutional Networks
- **Face Recognition**: [FaceNet (InceptionResnetV1)](https://github.com/timesler/facenet-pytorch) - Deep learning face recognition
- **Deep Learning**: [PyTorch](https://pytorch.org/) - Neural network framework
- **Database**: [Supabase](https://supabase.com/) - Department data and app controls
- **Data Storage**: [Google Sheets](https://www.google.com/sheets/about/) - Student registration data
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/) - Image manipulation
- **Authentication**: [Google OAuth2](https://developers.google.com/identity/protocols/oauth2) - Service account authentication

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Active internet connection for cloud services

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/RpM-999/P14-Student-Form.git
   cd P14-Student-Form
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### 1. Supabase Setup

Create a `.streamlit/secrets.toml` file in the project root with your Supabase credentials:

```toml
[supabase]
url = "your-supabase-project-url"
anon_key = "your-supabase-anon-key"
```

**Required Supabase Tables:**
- `department` - Columns: `dep_id`, `dep_name`
- `app_controls` - Columns: `is_registration_open` (boolean)

### 2. Google Sheets Setup

Add Google Service Account credentials to `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "your-private-key"
client_email = "your-service-account-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

**Google Sheets Setup:**
1. Create a Google Sheet named `STUDENT-DETAILS`
2. Share it with your service account email
3. Add headers in the first row: `S_name`, `S_mail`, `S_phone`, `S_Address`, `dep_id`, `S_admisionYear`, `S_live_face_photos`, `S_dob`

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run student_form.py
   ```

2. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`
   - The application will automatically open if available

3. **Register a new student**
   - Fill in all student details
   - Select the department from the dropdown
   - Capture three clear face photos (Front, Left, Right views)
   - Ensure good lighting and no obstructions (glasses, hats)
   - Submit the form

4. **Admin Controls**
   - Use Supabase `app_controls` table to enable/disable registration
   - Set `is_registration_open` to `true` to allow registrations

## 📁 Project Structure

```
P14-Student-Form/
│
├── student_form.py           # Main application file with UI and logic
├── connection_db.py          # Supabase database connection
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── DOCUMENTATION.md          # Additional documentation
├── .gitignore               # Git ignore rules
│
└── utils/
    ├── face_embedding.py    # Face detection and embedding generation
    └── g_spread.py          # Google Sheets integration
```

## 📚 Dependencies

- **streamlit** - Web application framework
- **supabase** - Database client for Supabase
- **gspread** - Google Sheets API wrapper
- **google-auth** - Google authentication library
- **facenet-pytorch** - Pre-trained FaceNet models
- **torch** - PyTorch deep learning framework
- **torchvision** - PyTorch vision utilities
- **Pillow** - Image processing library
- **numpy** - Numerical computing library

## 🔧 Key Components

### Face Recognition Pipeline

1. **Face Detection (MTCNN)**: Detects and aligns faces in captured images
2. **Face Embedding (FaceNet)**: Generates 512-dimensional embeddings
3. **Storage**: Embeddings stored as JSON in Google Sheets

### Data Flow

```
User Input → Form Validation → Face Capture → Face Detection → 
Embedding Generation → Data Storage (Google Sheets) → Success/Error Feedback
```

## 🔐 Security Notes

- All secrets should be stored in `.streamlit/secrets.toml` (never commit this file)
- Service account credentials are used for Google Sheets access
- Face embeddings are one-way transformations (cannot reconstruct original images)
- Registration can be controlled remotely via Supabase

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is part of the P14 Face Recognition System.

## 👤 Author

**RpM-999**

## 🐛 Known Issues

- Camera access requires HTTPS in production environments
- First model load may take time (models are cached afterward)

## 📞 Support

For issues or questions, please contact your respective HOD or create an issue in the repository.

---

**Note**: Ensure all dependencies are properly installed and configured before running the application.
