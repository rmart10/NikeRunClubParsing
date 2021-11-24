import dropbox
import os
from zipfile import ZipFile
import json
import datetime as dt
import pandas as pd

from dropbox.dropbox_client import Dropbox

appkey = '3d3lqdzah65hct6'
appsecret = 'eybf9o1k5avf1v1'
token = '{}'
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


def convertKMToMiles(inKM):
    miles=  inKM * .62137119
    return miles

def convertMetersSecondToMPH(inMS):
    mph = inMS * 2.23693629
    return mph

def calculateRunType(inRunDict:dict):

    '''Searches the dictionary passed in for the boundingBox value and returns 'Outdoors/Mobile' if the run is 
    found to be an outdoors run, else 'Stationary' is returned.   
    '''
    try:
        inRunDict.get('boundingBox')[0]
        return 'Outdoors/Mobile'
    except:
        return 'Stationary'




# ##CONSTRUCT AND INIT YOUR DROPBOX OBJECT
#dbx = dropbox.Dropbox(token)

##download/refresh local directory with Nike Run Club data from Dropbox
#downloadData(dbx)


##this needs to be a dict or something.
runType = ""
distance_Miles = ""
outStartDate = ""
outStartTime = ""
distance_KM = ""
timeZone = ""
duration_Seconds = ""
avgSpeed_MetersSec = ""
avgSpeed_MPH = ""
maxSpeed_MetersSec = ""
maxSpeed_MPH = ""
calories = ""
avgHR = ""
maxHR = ""
elevationGain = ""
elevationLoss = ""
minElevation = ""
maxElevation = ""
avgCadence = ""
maxCadence = ""
steps = ""




for fileName in os.listdir(dataPath):
    ### limit to metadata files, their detail is suffice
    if fileName.endswith('metadata.json'):
        print("Reading... ",fileName)
        
        ## read the entire json string of the file into a dictionary
        with open(scriptPath + '/' + dataPath + fileName,'r') as string:
            file_dict=json.load(string)
        string.close()

        

        runType = calculateRunType(file_dict)

        for key in file_dict:          
            # DATE, TIME, TIMEZONE, DURATION, DISTANCE, AVG SPEED, MAX SPEED, CALORIES, AVG HR, MAX HR, ELE GAIN, ELE LOSS, MIN ELE, MAX ELE
            #AVGCADENCE, MAXCADENCE, STEPS,
            #                    
           

            

            
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

            elif key == 'duration':
                duration_Seconds = file_dict[key]

            elif key == 'avgSpeed':
                avgSpeed_MetersSec = file_dict[key]
                avgSpeed_MPH = convertMetersSecondToMPH(avgSpeed_MetersSec)

            elif key == 'maxSpeed':
                maxSpeed_MetersSec = file_dict[key]
                maxSpeed_MPH = convertMetersSecondToMPH(maxSpeed_MetersSec)

            elif key == 'calories':
                calories = file_dict[key]                

            elif key == 'avgHeartrate':
                avgHR = file_dict[key]            

            elif key == 'maxHeartrate':
                maxHR = file_dict[key]                

            elif key == 'elevationGain':
                elevationGain = file_dict[key]                

            elif key == 'elevationLoss':
                elevationLoss = file_dict[key]            

            elif key == 'minElevation':
                minElevation = file_dict[key]
            
            elif key == 'maxElevation':
                maxElevation = file_dict[key]
            
            elif key == 'avgCadence':
                avgCadence = file_dict[key]

            elif key == 'maxCadence':
                maxCadence = file_dict[key]

            elif key == 'steps':
                steps = file_dict[key]
                  

            

            #### CONSTRUCT THE DICT BEFORE ADDING TO RUNS DICT
            data = {'file name':fileName,'run type':runType,'date':outStartDate,'time':outStartTime, 'timeZone': timeZone, 'duration(sec)':duration_Seconds,
            'distance (km)':distance_KM,'distance (miles)':distance_Miles,'avg speed (meters/second)':avgSpeed_MetersSec,
            'avg speed (MPH)':avgSpeed_MPH,'max speed (meters/second)':maxSpeed_MetersSec,'max speed (MPH)':maxSpeed_MPH,
            'calories':calories,'avg HR':avgHR,'max HR':maxHR,'elevation gain':elevationGain,'elevation loss':elevationLoss,
            'min elevation':minElevation,'max elevation':maxElevation,'avg cadence':avgCadence,'max cadence':maxCadence,'steps':steps}
            
            ##ADD THE DICT TO THE RUNS DICT
            runs[fileName]=data            
            
            
       

# for item in runs.items():
#     print(item)

runsDF = pd.DataFrame.from_dict(runs)
print(runsDF.head)
runsDF_Melted = runsDF.unstack().reset_index(name='file name')
runsDF_Melted.to_csv('melted.csv') ### now its really tall!





