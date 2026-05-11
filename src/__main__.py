import uvicorn

from core.config import config
from main_app import app

if __name__ == '__main__':
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT, log_level='critical')
