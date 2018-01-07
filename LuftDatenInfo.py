import requests
from datetime import timedelta,date,datetime
import csv
from pathlib import Path
import pandas as pd
import os

class LuftDatenInfo:
    
    def __init__(self,sensorID,sensorPrefix):
        
        # predefined paths
        self.url  = "https://archive.luftdaten.info/"
        self.repository = "testData/"
        if not os.path.exists(self.repository):
            os.makedirs(self.repository)
        
        if((type(sensorPrefix) is not str) or (type(sensorID) is not str)):
            print("sensorPrefix AND sensorID must be of type STRING!")
        
        if ("sds" in sensorPrefix):
            self.sensorPrefix = "sds" 
            self.CSVFilename = "_sds011_sensor_"+sensorID+".csv"
            df = pd.DataFrame(data = [],columns =["timestamp","P1","P2"] )
        else:
            if ("dht" in sensorPrefix):
                self.sensorPrefix = "dht"
                self.CSVFilename = "_dht22_sensor_"+sensorID+".csv"
                df = pd.DataFrame(data = [],columns =["timestamp","temperature","humidity"] )
            else:
                print("sensorprefix must contain sds XOR dht to determine the sensor type!")
        
        
        # time information
        self.initdate  = date(2017,9,4)
        self.localDate = date.today() - timedelta(1)
        self.validDates = []
        
        # dummy data container
        self.data = {"dummy" : df}
        
        
    def retrieveDatafromWebsiteandDump2File(self,date):
        url4Date = self.url + (date + "/" + date + self.CSVFilename)
        filename =  date + self.CSVFilename
        r = requests.get(url4Date)
        if not r.status_code == 404:
            # get backup copy of files
            with open(self.repository+filename,"w",newline = "") as csvfile:
                writeCSV    = csv.writer(csvfile, delimiter=',')
                
                # split into header and data
                length = len(r.text.split(sep="\n"))
                
                header  = (r.text.split(sep="\n"))[0]
                header  = header.split(sep = ";")
                
                idxTime = header.index(self.data["dummy"].columns[0])
                idxQ1   = header.index(self.data["dummy"].columns[1])
                idxQ2   = header.index(self.data["dummy"].columns[2])
                    
                writeCSV.writerow(header)
                
                dataList = []
                
                for datarow in (r.text.split(sep="\n"))[1:length-1]:
                    outputdata = datarow.split(sep=";")
                    writeCSV.writerow(outputdata)
                    
                    dataList.append([outputdata[idxTime],float(outputdata[idxQ1]),float(outputdata[idxQ2])])
                
                self.data[date] = pd.DataFrame(data = dataList,columns =[self.data["dummy"].columns[0],self.data["dummy"].columns[1],self.data["dummy"].columns[2]] )
                self.validDates.append(datetime.strptime(date,"%Y-%m-%d"))
    
    def retrieveDatafromFile(self,filename,date):
        with open(filename) as csvfile:
            readCSV             = csv.reader(csvfile,delimiter=',')
            dataList = []
            for row in enumerate(readCSV):
                if row[0] == 0:
                    idxTime = row[1].index(self.data["dummy"].columns[0])
                    idxQ1   = row[1].index(self.data["dummy"].columns[1])
                    idxQ2   = row[1].index(self.data["dummy"].columns[2])
                    
                else:
                    values  = row[1]                
                    dataList.append([values[idxTime],float(values[idxQ1]),float(values[idxQ2])])
            
            self.data[date] = pd.DataFrame(data = dataList,columns =[self.data["dummy"].columns[0],self.data["dummy"].columns[1],self.data["dummy"].columns[2]] )
            self.validDates.append(datetime.strptime(date,"%Y-%m-%d"))
                
    def retrieveData(self):

        daysBetween = self.localDate - self.initdate
        if abs(daysBetween.days)<1:
            print("cannot fetch data from web site as all data is already available!")
            return
        
        for dayShift in range(0,daysBetween.days+1):
            curDate = timedelta(dayShift) + self.initdate
            stringDate  = curDate.strftime("%Y-%m-%d")
            
            # first test for csv file
            # if not found obtain data from web site and dump stuff to HD 
            csvFile = Path(os.getcwd() +"/"+self.repository +stringDate + self.CSVFilename)
            if not csvFile.is_file():
                self.retrieveDatafromWebsiteandDump2File(stringDate)
            else:
                self.retrieveDatafromFile(csvFile,stringDate)
            
        # remove dummy (how to avoid the dummy attribution in first place?)    
        del self.data["dummy"]
        


        