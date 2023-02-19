from app.web import Web
from app.config import Config

if __name__ == '__main__':
    Config.load()
    Web.start()
