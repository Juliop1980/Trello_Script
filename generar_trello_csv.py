from __future__ import print_function
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
from trello_credentials import *  
import json
# importing the requests library 
import requests
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

# defining a params dict for the parameters to be sent to the Trello API
PARAMS = {'key':API_Key, 'token': API_Token}


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
		file_metadata = {'name': carpeta,'mimeType': 'application/vnd.google-apps.folder'}
		file = drive_service.files().create(body=file_metadata,fields='id').execute()

		folder_id = file.get('id')

	else:
		folder_id = folder_id_exists

	return folder_id


#retorna false si la carpeta no existe. De lo contrario retorna el id de la carpeta en el drive
def exists_carpeta_drive(carpeta):
	#gauth = GoogleAuth()
	#gauth.LocalWebserverAuth()
	#drive = GoogleDrive(gauth)
	query = "name = '" + carpeta + "' and mimeType='application/vnd.google-apps.folder' and trashed = false"
	page_token = None
	response = drive_service.files().list(q=query,spaces='drive',fields='nextPageToken, files(id, name)',pageToken=page_token).execute()
	
	for file in response.get('files', []):
		# Process change
		return file.get('id')
	page_token = response.get('nextPageToken', None)
	if page_token is None:
		return False


#retorna el id del archivo del drive subido, chequea si ya esta el archivo en la carpeta. Si no, lo crea
def subir_file(file,carpeta_dest):
	folder_id = crear_carpeta_drive(carpeta_dest)
	file_id = exist_file_in_carpeta(file, carpeta_dest)
	if not file_id:
		file_metadata = {
			'name': file,
			'parents': [folder_id]
		}
		media = MediaFileUpload(file,mimetype=None,resumable=True)

		file_id_aux = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
		file_id = file_id_aux.get('id')

	if file_id:
		text = input("Ya existe un archivo con el nombre " + file + " en la carpeta " + carpeta_dest + ". Desea reemplazar el archivo? (S/N)")
		if text == 's' or text == 'S':
			delete_file(drive_service, file_id)
			file_metadata = {'name': file,'parents': [folder_id]}
			media = MediaFileUpload(file,mimetype=None,resumable=True)

			file_id_aux = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
			file_id = file_id_aux.get('id')



	print ('File ID: %s' % file_id)
	return file_id
#retorna el id del archivo del drive subido

#chequea si existe un archivo dentro de una carpeta y devuelve el id si existe. De lo contrario devuelve False
def exist_file_in_carpeta(file_name, carpeta_name):
	id_carpeta = crear_carpeta_drive(carpeta_name)
	query = "'" + id_carpeta + "' in parents and " + "name = '" + file_name + "' and mimeType != 'application/vnd.google-apps.folder' "
	#print(query)
	page_token = None
	response = drive_service.files().list(q=query,spaces='drive',fields='nextPageToken, files(id, name)',pageToken=page_token).execute()
	
	for file in response.get('files', []):
		# Process change
		return file.get('id')
	page_token = response.get('nextPageToken', None)
	if page_token is None:
		return False
	return False

def delete_file(service, file_id):

	"""Permanently delete a file, skipping the trash.

	Args:
	service: Drive API service instance.
	file_id: ID of the file to delete.
	"""
	try:
		service.files().delete(fileId=file_id).execute()
	except:
		print ('An error occurred:')


#hace lo mismo que subir_file, solo que lo pasa a google sheets desde csv
def subir_file_csv_spreadsheet(file_name, carpeta_name):
	folder_id = crear_carpeta_drive(carpeta_name)
	file_aux = file_name + ".gs"
	file_id = exist_file_in_carpeta(file_aux, carpeta_name)
		#text = input("Ya existe un archivo con el nombre " + file_aux + " en la carpeta " + carpeta_name + ". Desea reemplazar el archivo? (S/N)")
	delete_file(drive_service, file_id)
	file_metadata = {'name': file_aux,'mimeType': 'application/vnd.google-apps.spreadsheet','parents': [folder_id]}
	media = MediaFileUpload(file_name,mimetype='text/csv',resumable=True)

	file_id_aux = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
	file_id = file_id_aux.get('id')

	#move_file(file_id,carpeta_name)
	#file = drive_service.files().update(fileId=file_id,addParents=folder_id).execute()

	#print ('File ID: %s' % file_id)
	return file_id

# def move_file(file_id, carpeta_name):
# 	folder_id = crear_carpeta_drive(carpeta_name)

# 	file = drive_service.files().update(fileId=file_id,
#                                     addParents=folder_id).execute()

#retorna el board, si no lo encuentra retorna False
def search_board(board_name):
	# defining a params dict for the parameters to be sent to the API
	# Trello api-endpoint
	# Trello api-endpoint 
	URL = 'https://api.trello.com/1/members/me/boards'
	#url = 'https://api.trello.com/1/members/me/boards?key=' + API_Key + '&token=' + API_Token
	# sending get request and saving the response as response object 
	r = requests.get(url = URL, params = PARAMS) 
	# extracting data in json format 
	boards_dict = r.json()

	for key in boards_dict:
		if key['name'] == board_name:
			return key
	return False
	
	#print (requests.get(url).json())
	#print(data)

	



if __name__ == '__main__':
	try:
		#file_io_base = open('trello_data_api.csv','wb')
	#download_file_google_drive(sys.argv[1],file_io_base)
		#crear_carpeta_drive("Trello_Data")
		#subir_file_csv_spreadsheet('Processed_Trello_Data.csv',"Trello_Data")

	#procesar_json()
		with open('trello_data.json', 'r') as f, open('Processed_Trello_Data.csv', 'w', newline= '') as faux:
			target_board = search_board(sys.argv[1])
			print(target_board)


	except IndexError:
		print("Por favor colocar el nombre del board del cual quiere informacion como argumento")

