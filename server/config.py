import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',  'postgresql://ireporterdb_n4xt_user:XCBk77bs6KduKYUgO3xrhZhVlyrmbJBd@dpg-cqq6ubggph6c7385q0s0-a.oregon-postgres.render.com/ireporterdb_n4xt')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')    

    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']  # Allow JWT in headers and cookies
    JWT_COOKIE_SECURE = True 
    JWT_COOKIE_CSRF_PROTECT = True  # Protect against CSRF
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000']  # We'll add the frontend URL here