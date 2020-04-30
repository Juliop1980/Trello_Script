from __future__ import print_function
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
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

#crea una carpeta drive solo si no existe alguna carpeta con el mismo nombre, retorna el id de la carpeta existente o creada
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

	return folder_id


#retorna false si la carpeta no existe. De lo contrario retorna el id de la carpeta en el drive
def exists_carpeta_drive(carpeta):
	#gauth = GoogleAuth()
	#gauth.LocalWebserverAuth()
	#drive = GoogleDrive(gauth)
	query = "name = '" + carpeta + "' and mimeType='application/vnd.google-apps.folder' "
	page_token = None
	response = drive_service.files().list(q=query,spaces='drive',fields='nextPageToken, files(id, name)',pageToken=page_token).execute()
	
	for file in response.get('files', []):
		# Process change
		return file.get('id')
	page_token = response.get('nextPageToken', None)
	if page_token is None:
		return False


#retorna el id del archivo del drive subido
def subir_file(file,carpeta_dest):
	folder_id = crear_carpeta_drive(carpeta_dest)
	file_metadata = {
	    'name': file,
	    'parents': [folder_id]
	}
	media = MediaFileUpload(file,mimetype=None,resumable=True)

	file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
	print ('File ID: %s' % file.get('id'))
	return file.get('id')
#retorna el id del archivo del drive subido


	



if __name__ == '__main__':
	try:
		file_io_base = open('trello_data_api.csv','wb')
	#download_file_google_drive(sys.argv[1],file_io_base)
		crear_carpeta_drive("Trello_Data")
		subir_file('trello_data_api.csv',"Trello_Data")
	#procesar_json()

	except IndexError:
		print("Por favor colocar el nombre del board del cual quiere informacion como argumento")

