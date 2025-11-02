#****************************************************************************
#    Application:   Annerkennung Ai Cockpit
#    Module:        config         
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

import os
from dotenv import load_dotenv
load_dotenv()

#=== Configuration Classes

class BaseConfig:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

class StrictConfig(BaseConfig):
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "16")) * 1024 * 1024
    MAX_FILES_PER_UPLOAD = int(os.getenv("MAX_FILES_PER_UPLOAD", "20"))
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
    }
    SUPPORTED_STATES = os.getenv("SUPPORTED_STATES", "BE,BY,NRW").split(",")