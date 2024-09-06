import requests
import base64
import time
import os
import logging

# Replace with your repo details and file path
owner = 'Human-Augment-Analytics'
repo = 'HAAG-Scripts-Repo'
path = ''

# url_specific = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
# url = f'https://api.github.com/repos/{owner}/{repo}/contents'
# response = requests.get(url)
# files = response.json()

# Replace with your marker
marker = '# TESTED AND DOCUMENTED'

# Get the personal access token from the environment variable
token = os.getenv('GH_PAT')

headers = {
    'Authorization': f'token {token}',
}

def get(url):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers['Retry-After'])
            time.sleep(retry_after)
        else:
            return response

def check_directory(path):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents'
    response = get(url)
    files = response.json()

    if isinstance(files, list):
        for file in files:
            if file['type'] == 'file':
                file_url = file['url']
                file_response = get(file_url)
                file_content = file_response.json()
                print(f"file {file['name']}")
                if file_content['encoding'] == 'base64':
                    try:
                        content = base64.b64decode(file_content['content']).decode('utf-8')

                        if marker in content:
                            logging.info(f"The file {file['path']} is tested and finalized.")
                        else:
                            logging.info(f"The file {file['path']} is not tested and finalized.")
                    except UnicodeDecodeError:
                        logging.info(f"Skipping file {file['path']} as it could not be decoded as UTF-8 text.")
                else:
                    logging.info(f"Skipping non-text file {file['path']}")
            elif file['type'] == 'dir':
                # Construct the full path for the subdirectory
                subdirectory_path = os.path.join(path, file['name'])
                check_directory(subdirectory_path)
    else:
        logging.error(f"Error checking directory {path}: {files['message']}")

check_directory(path)