import tensorflow as tensorflow
import DataAnalyzer
from datetime import datetime, timedelta,date
import pandas as pd



myClass = DataAnalyzer.DataAnalyzer()
#buckets = []
#time = datetime(2017,9,4,0,0,0)
myClass.getIntraDayAverages(2)
#myClass.getDailyAverages()
#myClass.plotCalculatedData()
myClass.dumpData2Excel()