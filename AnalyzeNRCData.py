import dropbox
import os
from zipfile import ZipFile
import json
import datetime as dt
import pandas as pd
from numpy.lib import function_base
import matplotlib.pyplot as plt
import seaborn as sns

## dropbox library
from dropbox.dropbox_client import Dropbox




###DROPBOX CREDENTIALS
appkey = '{}'
appsecret = '{}'
token = '{}'
#### YOU MUST CREATE AN APP ON DROPBOX THAT IS FULL SCOPED!!!!!!!


###relative path to the folder that houses your files on DROPBOX
#(IE OMIT 'Dropbox' from path displayed when viewing folder in UI)
dbxPath = '/Apps/RunGap/export'

# #folder relative to this script you want to store retrieved files in.
dataPath = 'Data/'

# #file name of processed, combined results
outputFileName = 'NRCDataCombined.csv'

##current folder path of script
scriptPath = os.getcwd()
scriptPath = scriptPath.replace("\\","/")



### columns list for data frame.
columns = [
'runType',
'distance_Miles',
'outStartDate',
'outStartTime',
'distance_KM',
'timeZone',
'duration_Seconds',
'avgSpeed_MetersSec',
'avgSpeed_MPH',
'maxSpeed_MetersSec',
'maxSpeed_MPH',
'calories',
'avgHR',
'maxHR',
'elevationGain',
'elevationLoss',
'minElevation',
'maxElevation',
'avgCadence',
'maxCadence',
'steps',
'startLatitude',
'startLongitude'
]


## blank df which will hold runs.
dfRuns = pd.DataFrame(columns=columns)



## bool that will control whether or not we make a call to dropbox to fetch all NRC files
refreshData = False


def downloadData(dbx: Dropbox):
    '''Function will download all files available witin a Dropbox folder using variables already initialized (dbxPath,dataPath,scriptPath)
    Accepts/Requires 1 parameter: dbx = Dropbox object reference'''    
    
    #populate variable(class 'dropbox.files.ListFolderResult) with all files available for download.
    result = dbx.files_list_folder(dbxPath) 

    print("###### Fetching new data...")  

    print("###### Found ", len(result.entries), " files...")  

    ##iterate each entry found and download to the relative path specified in dataPath
    ##will overwrite existing files.
    for entry in result.entries:
        dbx.files_download_to_file(dataPath+entry.name,entry.path_lower)

    ##unzip each csv file from archie
    for fileName in os.listdir(dataPath):
        print("Extracting ",fileName)
        if fileName.endswith('.zip'):
            with ZipFile(scriptPath + '/' + dataPath + fileName,'r') as zipObj:
                try:
                    zipObj.extractall(dataPath)
                except Exception as e:
                    print("Error", e)
    print("###### Done downloading and extracting files...") 




def convertKMToMiles(inKM):
    '''Function will convert KM to miles''' 
    miles=  inKM * .62137119
    return miles

def convertMetersSecondToMPH(inMS):
    '''Function will convert meters per second to mph''' 
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



if refreshData == True:
    ##CONSTRUCT AND INIT YOUR DROPBOX OBJECT
    dbx = dropbox.Dropbox(token)
    #download/refresh local directory with Nike Run Club data from Dropbox
    downloadData(dbx)
else:
    print("###### Not fetching new data...")


##init vars used for appending to df 
runType,distance_Miles,outStartDate,outStartTime,distance_KM,timeZone,duration_Seconds,avgSpeed_MetersSec, \
avgSpeed_MPH,maxSpeed_MetersSec,maxSpeed_MPH,calories,avgHR,maxHR,elevationGain,elevationLoss,minElevation, \
maxElevation,avgCadence,maxCadence,steps,startLatitude,startLongitude = "","","","","","","","","","","","","","","","","","","","","","",""


print("###### Beginning processing of downloaded, extracted files...")
indexCounter = 0
for fileName in os.listdir(dataPath):
    ### limit to metadata files, their detail is suffice
    if fileName.endswith('metadata.json'):
        #print("Reading... ",fileName)
        
        ## read the entire json string of the file into a dictionary
        with open(scriptPath + '/' + dataPath + fileName,'r') as string:
            file_dict=json.load(string)
        string.close()       


        ##reset vars used for appending to df (23)
        runType,distance_Miles,outStartDate,outStartTime,distance_KM,timeZone,duration_Seconds,avgSpeed_MetersSec, \
        avgSpeed_MPH,maxSpeed_MetersSec,maxSpeed_MPH,calories,avgHR,maxHR,elevationGain,elevationLoss,minElevation, \
        maxElevation,avgCadence,maxCadence,steps,startLatitude,startLongitude,avgTemp = "","","","","","","","","","","","","","","","","","","","","","","",""

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
            
            elif key == 'displayPath':
                ##run type should be Outdoors/Mobile
                startLatitude = file_dict[key][0]['lat']
                startLongitude = file_dict[key][0]['lon']           

          
            
        row = pd.Series([runType,distance_Miles,outStartDate,outStartTime,distance_KM,timeZone,
        duration_Seconds,avgSpeed_MetersSec,avgSpeed_MPH,maxSpeed_MetersSec,maxSpeed_MPH
        ,calories,float(avgHR),maxHR,elevationGain,elevationLoss,minElevation,maxElevation,
        avgCadence,maxCadence,steps,startLatitude,startLongitude],index=dfRuns.columns)
        
        
        #append row to dataframe at counters index
        dfRuns.loc[indexCounter]=row
        indexCounter +=1 ##increment counter

        

            

               
           
print("###### Completed processing of downloaded, extracted files. See:" ,outputFileName)
dfRuns.to_csv(outputFileName,header=True)




############### PLOT OUT SOME HIGH LEVEL AGGREGATES using MATPLOTLIB

print("##### Total Runs by Run Type:")
dfRunTypes = dfRuns.groupby('runType').size()
print(dfRunTypes)
dfRunTypes.plot(x="runType",y="Count",kind="bar")
plt.xlabel('Run Types')
plt.xticks(rotation=0) ##rotate x axis labels, they were at 90
plt.ylabel('Run  Counts')
plt.title('Total Runs by Run Type')
plt.grid(axis='y') ## show gridlines on x axis only
plt.show()

print("##### Average Pace by Run Type:")
dfRunAvgPace = dfRuns.groupby('runType')['avgSpeed_MPH'].mean()
print(dfRunAvgPace)
dfRunAvgPace.plot(x="runType",y="mean",kind="bar")
plt.xlabel('Run Types')
plt.xticks(rotation=0) ##rotate x axis labels, they were at 90
plt.ylabel('Avg Pace')
plt.title('Average Pace by Run Type')
plt.grid(axis='y') ## show gridlines on x axis only
plt.show()

print("##### Average HR by Run Type:")

dfRunAvgHR = dfRuns.groupby('runType')['avgHR'].mean()
print(dfRunAvgHR)
dfRunAvgHR.plot(x="runType",y="mean",kind="bar")
plt.xlabel('Run Types')
plt.xticks(rotation=0) ##rotate x axis labels, they were at 90
plt.ylabel('Avg HR')
plt.title('Average HR by Run Type')
plt.grid(axis='y') ## show gridlines on x axis only
plt.show()





## SEABORN PLOTS

dfCleanAvgHRDistance = dfRuns.dropna(subset=['distance_Miles','avgHR']) ##remove rows from the dfRuns DF that have nulls in either of these columns.
dfCleanAvgHRDistance = dfCleanAvgHRDistance.query("distance_Miles >= 1").query("avgHR > 0") ## remove rows where less than 1 mile was run, no HR was captured
dfCleanAvgHRDistance['distance_Miles'] = dfCleanAvgHRDistance['distance_Miles'].astype(float)
dfCleanAvgHRDistance['avgHR'] = dfCleanAvgHRDistance['avgHR'].astype(float)
sns.regplot(x="avgHR",y="distance_Miles",data=dfCleanAvgHRDistance)
plt.title("Linear Regression Model Fit: Average HR and Distance Run")
plt.show()









