from __future__ import print_function
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive

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

#crea una carpeta drive solo si no existe alguna carpeta con el mismo nombre
def crear_carpeta_drive(carpeta):
	folder_id_exists = exists_carpeta_drive(carpeta)
	if not folder_id_exists:
		file_metadata = {
	    'name': carpeta,
	    'mimeType': 'application/vnd.google-apps.folder'
		}
		file = drive_service.files().create(body=file_metadata,
		                                    fields='id').execute()

		folder_id = file.get('id')

	else:
		folder_id = folder_id_exists

	print ('Folder ID: %s' % folder_id)


def exists_carpeta_drive(carpeta):
	#gauth = GoogleAuth()
	#gauth.LocalWebserverAuth()
	#drive = GoogleDrive(gauth)
	response = drive_service.list(q="name='June 2019' and mimeType='application/vnd.google-apps.folder'",driveId='abcdef',corpora='drive', includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
	file_list = retrieve_all_files(drive_service)
	for item in response.get('files', []):
		return item['id']

	return false



if __name__ == '__main__':
	try:
		file_io_base = open('trello_data_api.json','wb')
	#download_file_google_drive(sys.argv[1],file_io_base)
		crear_carpeta_drive("hola")
	#procesar_json()

	except IndexError:
		print("Por favor colocar el nombre del board del cual quiere informacion como argumento")

