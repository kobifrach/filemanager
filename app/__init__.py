import os
from flask import Flask
from dotenv import load_dotenv
from .routes.Customers import customers_bp
from .routes.Customers_Files import customer_files_bp
from .routes.Customers_Folders import customer_folders_bp
from .routes.Documents import documents_bp
from .routes.Files import files_bp
from .routes.Folders import folders_bp
from .routes.Folders_Files import foldersFiles_bp
from .routes.Users import users_bp
from .routes.User_Type import userTypes_bp
from .routes.Auth import auth_bp

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def create_app():
    app = Flask(__name__)

    # קונפיגורציית JWT או דברים רגישים
    app.config['SECRET_KEY'] = SECRET_KEY

    

    app.register_blueprint(customers_bp)
    app.register_blueprint(customer_files_bp)
    app.register_blueprint(customer_folders_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(folders_bp)
    app.register_blueprint(foldersFiles_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(userTypes_bp)
    app.register_blueprint(auth_bp)

    return app
