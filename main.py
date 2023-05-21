from dotenv import load_dotenv
import json
import os
from logger import Logger

if __name__ == '__main__':
    load_dotenv()
    VK_TOKEN = os.getenv('VK_TOKEN')
    YA_TOKEN = os.getenv('YA_TOKEN')
    log = Logger()
