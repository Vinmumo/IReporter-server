import cloudinary
import cloudinary.uploader
import os


cloudinary.config(
    cloud_name='dycrqnjcs',
    api_key='314272631384883',
    api_secret=os.getenv('CLOUDINARY_SECRET_KEY'),
)

def upload_file(file):
    result = cloudinary.uploader.upload(file)
    
    return result

