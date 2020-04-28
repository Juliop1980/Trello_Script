from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import io
from googleapiclient.http import MediaIoBaseDownload
import json
import csv

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

"""Shows basic usage of the Drive v3 API.
Prints the names and ids of the first 10 files the user has access to.
"""
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

drive_service = build('drive', 'v3', credentials=creds)

def download_file_google_drive(file_id, local_fd):

  request = drive_service.files().get_media(fileId=file_id)
  media_request = MediaIoBaseDownload(local_fd, request)

  while True:    
    _, done = media_request.next_chunk()

    if done:
      print ('Download Complete')
      return

def procesar_json():
    with open('trello_data.json', 'r') as f, open('Processed_Trello_Data.csv', 'w', newline= '') as faux:
        trello_dict = json.load(f)
        thewriter = csv.writer(faux)
        thewriter.writerow(['key', 'card_id', 'card_name', 'member', 'estatus', 'ini_date', 'end_date'])
        cards_dict = trello_dict['cards']
        dict_miembros_asociados = miembros_asociados(trello_dict)
        print(dict_miembros_asociados)

def miembros_asociados(trello_dict):
    members_dict = trello_dict['members']
    result_dict ={}
    for key in members_dict:
        result_dict.update( {key['id'] : key['fullName']} )

    return result_dict






        

if __name__ == '__main__':
    file_io_base = open('trello_data.json','wb')
    try:
        download_file_google_drive(sys.argv[1],file_io_base)
    except IndexError:
        print("Por favor colocar el id del archivo json como argumento")

    procesar_json()
