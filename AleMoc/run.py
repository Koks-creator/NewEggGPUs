import uvicorn
from AleMoc import app

from AleMoc import uvicorn_log_config
from AleMoc.config import Config


if __name__ == '__main__':
    uvicorn.run(app, host=Config.HOST, port=Config.PORT, log_config=uvicorn_log_config)
