import os
import dotenv

# env
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

account = {
    'id': os.environ["instagramId"],
    'pw': os.environ["instagramPassword"],
}

# @todo auto gen
