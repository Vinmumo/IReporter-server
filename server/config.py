import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',  'postgresql://ireporterdb_n4xt_user:XCBk77bs6KduKYUgO3xrhZhVlyrmbJBd@dpg-cqq6ubggph6c7385q0s0-a.oregon-postgres.render.com/ireporterdb_n4xt')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
