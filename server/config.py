import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',  'postgresql://ireporterdb_n4xt_user:XCBk77bs6KduKYUgO3xrhZhVlyrmbJBd@dpg-cqq6ubggph6c7385q0s0-a.oregon-postgres.render.com/ireporterdb_n4xt')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
    SECRET_KEY = os.getenv('SECRET_KEY', '73981265e98c2ba8c7ae4db286969872c4ed8cf99bc983e1233a102df40b5ed7')    

    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fb7735a66fa196e5ed0eb045e3f00f12e6722f88b1793840fb273c4b37dc1d5a') 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']  
    JWT_COOKIE_SECURE = True 
    JWT_COOKIE_CSRF_PROTECT = True  
    

    #Flaskmail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'vinnymummo@gmail.com'
    MAIL_PASSWORD = 'vzyo avvc ltqz gzvt'
    MAIL_DEFAULT_SENDER = 'vinnymummo@gmail.com'
    FRONTEND_URL = 'http://localhost:3000'  

    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000']  