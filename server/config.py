import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://ireporterdb_user:SzQDVnhIAcSC4N70WDio7k70LpqvBNJN@dpg-cqobjv3v2p9s73an63tg-a.oregon-postgres.render.com/ireporterdb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
