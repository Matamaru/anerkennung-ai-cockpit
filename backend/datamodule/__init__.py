from backend.datamodule.config import config_db
from backend.datamodule.datamodule import DataBase

params = config_db()
db = DataBase(params)