import dropbox
import os
from zipfile import ZipFile
import json
import datetime as dt
import pandas as pd

from dropbox.dropbox_client import Dropbox

appkey = '3d3lqdzah65hct6'
appsecret = 'eybf9o1k5avf1v1'
token = 'RK3ZY-z72xkAAAAAAAAAAYRSIGuoMEAJ8EQeMd1WeG4W3jmjZcckN3a_Y5tBMnyX'
#### YOU MUST CREATE AN APP ON DROPBOX THAT IS FULL SCOPED!!!!!!!


###relative path to the folder that houses your files on DROPBOX
#(IE OMIT 'Dropbox' from path displayed when viewing folder in UI)
dbxPath = '/Apps/RunGap/export'

# #folder relative to this script you want to store retrieved files in.
dataPath = 'Data/'

##current folder path of script
scriptPath = os.getcwd()
scriptPath = scriptPath.replace("\\","/")


##dictionary which will hold all runs
runs = {}



def downloadData(dbx: Dropbox):
    '''Function will download all files available witin a Dropbox folder using variables already initialized (dbxPath,dataPath,scriptPath)
    Accepts/Requires 1 parameter: dbx = Dropbox object reference'''    
    
    #populate variable(class 'dropbox.files.ListFolderResult) with all files available for download.
    result = dbx.files_list_folder(dbxPath)    

    ##iterate each entry found and download to the relative path specified in dataPath
    ##will overwrite existing files.
    for entry in result.entries:
        dbx.files_download_to_file(dataPath+entry.name,entry.path_lower)


    ##unzip each csv file from archie
    for fileName in os.listdir(dataPath):
        print("Extracting ",fileName)
        with ZipFile(scriptPath + '/' + dataPath + fileName,'r') as zipObj:
            zipObj.extractall(dataPath)


def clearVars():
    distance_KM = ""
    outStartDate = ""
    outStartTime = ""
    distance_Miles = ""
    timeZone = ""

def convertKMToMiles(inKM):
    miles=  inKM * .62137119
    return miles



# ##CONSTRUCT AND INIT YOUR DROPBOX OBJECT
#dbx = dropbox.Dropbox(token)

##download/refresh local directory with Nike Run Club data from Dropbox
#downloadData(dbx)


##this needs to be a dict or something.
distance_Miles = ""
outStartDate = ""
outStartTime = ""
distance_KM = ""
timeZone = ""


for fileName in os.listdir(dataPath):
    ### limit to metadata files, their detail is suffice
    if fileName.endswith('metadata.json'):
        print("Reading... ",fileName)
        
        ## read the entire json string of the file into a dictionary
        with open(scriptPath + '/' + dataPath + fileName,'r') as string:
            file_dict=json.load(string)
        string.close()

        

        for key in file_dict:          
            # DATE, TIME, TIMEZONE, DURATION, DISTANCE, AVG SPEED, MAX SPEED, CALORIES, AVG HR, MAX HR, ELE GAIN, ELE LOSS, MIN ELE, MAX ELE
            #AVGCADENCE, MAXCADENCE, STEPS,             
           

            if key == 'distance':                
                distance_KM = str(file_dict[key])
                distance_KM = float(distance_KM) / 1000
                distance_Miles = convertKMToMiles(distance_KM)

            elif key == 'startTime':
                startTime = file_dict[key]['time']                
                startTime = startTime.replace('Z','').replace('T',' ') ##format the value for constructing date time from pandas...
                
                startDateTimeObj = pd.to_datetime(startTime) ##cast to datetime using Pandas               
                outStartDate = startDateTimeObj.strftime("%Y-%m-%d")
                outStartTime = startDateTimeObj.time()  

                ##try to get timezone
                try:
                    timeZone = file_dict[key]['timeZone']   
                except:
                    timeZone = 'unknown'


            #### CONSTRUCT THE DICT BEFORE ADDING TO RUNS DICT
            data = {'date':outStartDate,'time':outStartTime, 'timeZone': timeZone,'distance (km)':distance_KM,'distance (miles)':distance_Miles}
            
            ##ADD THE DICT TO THE RUNS DICT
            runs[fileName]=data            
            
            ##CLEAR THE VARIABLES
            clearVars()  
       

for item in runs.items():
    print(item)




