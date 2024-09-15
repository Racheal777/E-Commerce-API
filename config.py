import uuid

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os

from dotenv import  load_dotenv



load_dotenv()

# Configuration
cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('API_KEY'),
    api_secret = os.getenv('API_SECRET'),
    secure=True
)

# Upload an image
def upload_file(file):
    upload_result = cloudinary.uploader.upload(file, public_id=str(uuid.uuid4()))
    return upload_result.get('secure_url')
