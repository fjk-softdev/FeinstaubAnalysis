import numpy as numpy
from datetime import datetime, timedelta,date
import LuftDatenInfo
import pandas as pd
import matplotlib.pyplot as plt
import xlwt

class DataAnalyzer:

    def __init__(self):
        self.dataStorageParticles = LuftDatenInfo.LuftDatenInfo("5475","sds")
        self.dataStorageParticles.retrieveData()
        
        self.dataStorageEnv = LuftDatenInfo.LuftDatenInfo("5476","dht")
        self.dataStorageEnv.retrieveData()
        
        self.excelOuputFile = "Averages.xls"
        


    #-------------------------------------------------------
    # analyze functions:        
    def getDailyAverages(self):

        datalist1 = []
        datalist2 = []      
        for date in self.dataStorageParticles.validDates:
            curdata = (self.dataStorageParticles.data)[date.strftime('%Y-%m-%d')]
            
            datalist1.append( [date,curdata.P1.mean()])
            datalist2.append( [date,curdata.P2.mean()])

        self.p1Averages         = pd.DataFrame(data = datalist1,columns = ["dateTime","data"])
        self.p2Averages         = pd.DataFrame(data = datalist2,columns = ["dateTime","data"])

        datalist1.clear()
        datalist2.clear()        
        for date in self.dataStorageEnv.validDates:
            curdata = (self.dataStorageEnv.data)[date.strftime('%Y-%m-%d')]
            
            datalist1.append( [date,curdata.temperature.mean()])
            datalist2.append( [date,curdata.humidity.mean()])
       
        self.tempAverages       = pd.DataFrame(data = datalist1,columns = ["dateTime","data"])
        self.humidityAverages   = pd.DataFrame(data = datalist2,columns = ["dateTime","data"])
       
    
    def getIntraDayAverages(self,timeinHours):
        
        p1Av,p2Av = self.getDatainTimeBuckets(self.dataStorageParticles, timeinHours)
        
        self.p1Averages= pd.DataFrame(data = p1Av,columns = ["dateTime","data"])
        self.p2Averages= pd.DataFrame(data = p2Av,columns = ["dateTime","data"])

        TempAv,HumidityAv = self.getDatainTimeBuckets(self.dataStorageEnv, timeinHours)

        self.tempAverages= pd.DataFrame(data = TempAv,columns = ["dateTime","data"])
        self.humidityAverages= pd.DataFrame(data = HumidityAv ,columns = ["dateTime","data"])
    
       
    def getDatainTimeBuckets(self,dataSample,timeAverage):
        
        timeAverage = int(timeAverage)
        if timeAverage == 0:
            print("timeAverage input is 0 .. will change to 24")
            timeAverage = 24
        
        dataOutput1 = []
        dataOutput2 = []
        
        for date in dataSample.validDates:
            curdata = (dataSample.data)[date.strftime('%Y-%m-%d')]
            
  
            timebuckets = [datetime.strptime(date.strftime('%Y-%m-%d'),"%Y-%m-%d") + timedelta(hours=timeAverage*(i+1)) for i in range(int(24/timeAverage))] 
            
            bucketsp1       = [0 for i in range(int(24/timeAverage))]
            bucketsp2       = [0 for i in range(int(24/timeAverage))] 
            normalize       = [0.0000001 for i in range(int(24/timeAverage))]
            
            for index,row in curdata.iterrows():
                localtime = datetime.strptime(row.timestamp,"%Y-%m-%dT%H:%M:%S")
                bucketIndex = int(localtime.hour)//timeAverage # // means int division!

                bucketsp1[bucketIndex]   += row[1]
                bucketsp2[bucketIndex]   += row[2]
                normalize[bucketIndex]   += 1

            for i in range(int(24/timeAverage)):
                bucketsp1[i]    = bucketsp1[i]/float(normalize[i])
                bucketsp2[i]    = bucketsp2[i]/float(normalize[i])

                # shift to middle of bucket
                dataOutput1.append([timebuckets[i]-timedelta(hours = float(timeAverage)/2),bucketsp1[i]])
                dataOutput2.append([timebuckets[i]-timedelta(hours = float(timeAverage)/2),bucketsp2[i]])
            
        return dataOutput1,dataOutput2
    

    
    
    
    #-------------------------------------------------------
    # output functions
    def plotCalculatedData(self):    

        fig, (ax1, ax2) = plt.subplots(nrows =2, sharex = True)
        
        # plot p1 data
        ax1.plot(numpy.array(self.p1Averages.dateTime), numpy.array(self.p1Averages.data), 'b-')

        #plot temp and humidity
        ax1.plot(numpy.array(self.tempAverages.dateTime), numpy.array(self.tempAverages.data), 'g-')
        ax1.plot(numpy.array(self.humidityAverages.dateTime), numpy.array(self.humidityAverages.data), 'm-')

        # plot p1 data
        ax2.plot(numpy.array(self.p2Averages.dateTime), numpy.array(self.p2Averages.data), 'r-')

        #plot temp and humidity
        ax2.plot(numpy.array(self.tempAverages.dateTime), numpy.array(self.tempAverages.data), 'g-')
        ax2.plot(numpy.array(self.humidityAverages.dateTime), numpy.array(self.humidityAverages.data), 'm-')
        
        plt.show()        
    
    
    def dumpData2Excel(self):
        
        writer = pd.ExcelWriter(self.excelOuputFile)
        
        if self.p1Averages is not None and self.p2Averages is not None:
            self.p1Averages.to_excel(writer, "P1")
            self.p2Averages.to_excel(writer, "P2")
            writer.save()
        
        if self.tempAverages is not None and self.humidityAverages is not None:
            self.tempAverages.to_excel(writer, "temperature")
            self.humidityAverages.to_excel(writer, "humidity")
            writer.save()
        
        writer.close()
    
    #-------------------------------------------------------        