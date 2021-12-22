from __future__ import print_function
import os.path
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import sys


############################## VERSION HISTORY
# MM/DD/YYYY - ...

 
class GoogleDriveClient:
    

 
################ INIT CLASS 
    
    def __init__(self, fileName, friendlyFileName, fileDescription, parentFolderId=None,spreadsheetId=None):
        '''spreadsheetId = the id of the Google Sheet being replaced (omit if creating file)\
         , fileName = the file name ('NRCCombined.csv') of the file in the same directory being uploaded to Google Drive,\
           friendlyFileName = The friendly name of the file as displayed in Google Drive ('Nike Run Club Data'),\
           fileDescription = A description of the file, parentFolderId= The ID of the folder you wish to place your Google Drive file in, only if creating file\
           spreadsheetId = the Google Drive spreadsheet id being replaced (omit if creating new)'''
        self.spreadsheetId = spreadsheetId
        self.fileName = fileName
        self.friendlyFileName = friendlyFileName
        self.fileDescription = fileDescription        
        self.parentFolderId = parentFolderId       

    
   
        

    
    def replaceFile(self):
        '''Function will replace the spreadsheet/Google Sheet Id used in the constructor with the physical file, friendly file name and file description passed into the constructor.'''
        try:
            media = MediaFileUpload(self.fileName,
                                mimetype='text/csv',
                                resumable=True)            
            body = {
                "name": self.friendlyFileName,
                "description": self.fileDescription,
                "mimeType": "application/vnd.google-apps.spreadsheet", ##upload as a google sheet          
            }
            ## REPLACE A FILE
            file = service.files().update(fileId=self.spreadsheetId,body=body,media_body=media).execute() ##overwrite existing gfile.
        except e as Exception:
            raise Exception("Error:", sys.exc_info()[0])

    
    def createFile(self):        
        '''Function will create a spreadsheet/Google Sheet with the physical file, friendly file name and file description passed into the constructor.'''
        try:
            # # ##try uploading a file   
            media = MediaFileUpload(self.fileName,
                                    mimetype='text/csv',
                                    resumable=True)

            if len(self.parentFolderId) > 5:
                body = {
                    "name": self.friendlyFileName,
                    "description": self.fileDescription,
                    "mimeType": "application/vnd.google-apps.spreadsheet", ##upload as a google sheet 
                    "parents": [self.parentFolderId] 
                }
            else:
                 body = {
                    "name": self.friendlyFileName,
                    "description": self.fileDescription,
                    "mimeType": "application/vnd.google-apps.spreadsheet", ##upload as a google sheet                     
                }

            
            # CREATE A FILE
            file = service.files().create(body=body,
                                                  media_body=media,
                                                  fields='id').execute() ## create new file.
            
        except e as Exception:
            raise Exception("Error:", sys.exc_info()[0])   
        



    def listFiles(self): 
        '''Function will list out all files in Google Drive and their associated Ids'''
        try:
            # Call the Drive v3 API
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

        except e as Exception:            
            raise Exception("Error:", sys.exc_info()[0])       

        return items         




### SCOPES DICT USED FOR GOOGLE DRIVE UPLOAD
# !!!!!!!! If modifying these scopes or if google auth expires, delete the file token.json!!!!!!!!! 
# This script will fire a browser to recreate it 
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly','https://www.googleapis.com/auth/drive']

creds = None

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
service = build('drive', 'v3', credentials=creds)


    
    
     
    
  
    
            
    



