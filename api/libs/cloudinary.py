import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader 
from setting import settings

cloudinary.config(
    secret=True,
    cloud_name=settings.CLOUDINARY_NAME,
    api_key = settings.CLOUDINARY_KEY,
    api_secret = settings.CLOUDINARY_SECRET
)

cloudinary_uploader = cloudinary.uploader