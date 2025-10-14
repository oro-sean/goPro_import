import os
import pandas as pd
import datetime
import ffmpeg
import csv

class Video_TimeStamping:
    def __init__(self,folder):
        self.folder = folder

    def GetFiles(self):
        self.files = os.listdir(self.folder)

    def SortFiles(self):
        videos = []
        chapters = []
        prefix = []
        suffix = []
        s=''
        for file in self.files:
            if file.endswith('.MP4'):
                videos.append(s.join(list(file)[4:8]))
                chapters.append(s.join(list(file)[2:4]))
                prefix.append(s.join(list(file)[:2]))
                suffix.append(s.join(list(file)[8:]))

        df = pd.DataFrame({'video': videos, 'chapter': chapters, 'prefix': prefix, 'suffix':suffix})
        df.sort_values(by=['video', 'chapter'],inplace=True, ignore_index=True)

        files = []
        currentVideo = []
        firstChapters_ind = []
        otherChapters_ind = []
        for i in range(len(df)):
            if currentVideo != str(df['video'][i]):
                currentVideo = str(df['video'][i])
                firstChapters_ind.append(i)
            else:
                otherChapters_ind.append(i)
            files.append(str(df['prefix'][i])+str(df['chapter'][i])+str(df['video'][i])+str(df['suffix'][i]))

        self.files_sorted = files
        self.firstChapters_ind = firstChapters_ind
        self.otherChapters_ind = otherChapters_ind

    def GetTimeStamps(self):

        timeStamps = []
        timeDeltas = []
        for i in range(len(self.files_sorted)):
            metaData = ffmpeg.probe(os.path.join(self.folder,self.files_sorted[i]))
            if i in self.firstChapters_ind:
                origin = datetime.datetime.strptime(metaData['streams'][0]['tags']['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                timeStamp = datetime.datetime.strptime(metaData['streams'][0]['tags']['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                duration =  datetime.timedelta(seconds=float(metaData['streams'][0]['duration']))
                timeSince = datetime.timedelta(seconds=float(metaData['streams'][0]['duration']))
                timeDeltas.append(datetime.timedelta(seconds=0))
                timeStamps.append(timeStamp)
            else:
                timeStamp = origin + timeSince
                duration =  datetime.timedelta(seconds=float(metaData['streams'][0]['duration']))
                timeDeltas.append(timeSince)
                timeStamps.append(timeStamp)
                timeSince = timeSince + duration
        self.timeStamps = timeStamps
        self.timeDeltas = timeDeltas

    def Write_CSV(self):
        with open(os.path.join(self.folder,'timeStamping.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['File', 'TimeStamp', 'NjordOffset'])
            for i in range(len(self.timeStamps)):
                writer.writerow([self.files_sorted[i], str(self.timeStamps[i]), str(self.timeDeltas[i].seconds)+'.'+str(self.timeDeltas[i].microseconds) ])

        csvfile.close()

    def Add_CSV(self):
        self.GetFiles()
        self.SortFiles()
        self.GetTimeStamps()
        self.Write_CSV()



#%%
