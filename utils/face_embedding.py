import streamlit as st
import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN

# --- Model Configuration ---

# Set up the device (use GPU if available, otherwise CPU)
# Using GPU (cuda) on Streamlit Cloud requires a paid plan, 
# but this code works fine on CPU (it'll just be a bit slower).
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


@st.cache_resource
def load_models():
    """
    Loads and caches the MTCNN and InceptionResnetV1 models.
    This function runs only once and stores the models in Streamlit's cache.
    """
    # MTCNN is for detecting and cropping faces
    mtcnn = MTCNN(
        image_size=160, 
        margin=0, 
        min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], # Default thresholds for face detection
        factor=0.709, 
        prewhiten=True,
        device=device
    )
    
    # InceptionResnetV1 is for generating the face embeddings
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    
    return mtcnn, resnet

# --- Load Models on App Start ---
# This line calls the cached function and makes the models globally available
# in this script.
mtcnn, resnet = load_models()


# --- Main Embedding Function ---

def get_face_embedding(image: Image):
    """
    Takes a PIL Image, detects the face, and returns the embedding.

    Args:
        image (PIL.Image): The image file captured from st.camera_input.

    Returns:
        A tuple:
        - (list, "Success message") if a face is found and embedding is created.
        - (None, "Error message") if no face is detected or an error occurs.
    """
    
    # Convert image to RGB format (st.camera_input gives RGBA)
    image_rgb = image.convert('RGB')
    
    # --- 1. Detect Face ---
    # mtcnn() returns a cropped and pre-whitened image tensor of the face.
    # If no face is detected, it returns None.
    face_tensor = mtcnn(image_rgb, save_path=None)
    
    if face_tensor is None:
        return None, "❌ No face detected. Please ensure your face is clear and try again."

    # --- 2. Generate Embedding ---
    # Move the face tensor to the same device as the model
    face_tensor = face_tensor.to(device)
    
    # Use torch.no_grad() for inference as we're not training the model
    with torch.no_grad():
        # unsqueeze(0) adds a batch dimension (model expects [batch_size, channels, H, W])
        embedding = resnet(face_tensor.unsqueeze(0)) 
    
    # Detach from GPU, convert to numpy array, and get the first (and only) item
    embedding_np = embedding.detach().cpu().numpy()[0]
    
    # Convert the numpy array to a standard Python list for JSON/database storage
    embedding_list = embedding_np.tolist()
    
    return embedding_list, "✅ Face embedding created successfully!"