import asyncio
from open_gopro import WiredGoPro
import time
import threading
import os

import open_gopro.models.constants as constants
from open_gopro import models

from datetime import datetime

from open_gopro.domain.exceptions import FailedToFindDevice, ResponseTimeout


async def main(gp, del_all, cameraName, export_path) -> None:

    found = False
    while not found:
        try:
            gopro = WiredGoPro(gp)
            await gopro.open()
            found = True

        except ResponseTimeout:
            print("Pausing Search for "+str(cameraName))
            await asyncio.sleep(120)

    print(str(cameraName) + " is now online")

    async with WiredGoPro(gp) as gopro:

        if del_all:
            response = await gopro.http_command.delete_all_media()
            print("Delete All for "+str(cameraName)+" Finished with Error Code - "+str(response.status))

        response = await gopro.http_command.set_date_time(date_time=datetime.now())
        print("Time Set for "+str(cameraName)+" Finished with Error Code - "+str(response.status))

        response = await gopro.http_command.set_shutter(shutter=constants.Toggle.ENABLE)
        print(response.status)

        state = True
        while state:
            await asyncio.sleep(180)
            response = await gopro.http_command.get_camera_state()
            state = response.data[constants.StatusId.ENCODING]
            if state:
                response = await gopro.http_command.get_camera_state()
                battery = response.data[constants.StatusId.INTERNAL_BATTERY_PERCENTAGE]
                sdCard = response.data[constants.StatusId.SD_CARD_REMAINING]
                print(str(cameraName)+" Battery is "+str(battery))
                print(str(cameraName) + " SD Card is " + str(sdCard))

        print(str(cameraName)+" Has stopped recording - Starting download")

        startTime = time.time()
        response = await (gopro.http_command).get_media_list()
        fileNames = []
        for i in range(len(response.data.media[0].file_system)):
            fileNames.append(response.data.media[0].file_system[i].filename)

        print(fileNames)
        print(str(datetime.now().date()))
        export_folder_path = export_path
        for addition in [str(datetime.now().date()), cameraName]:
            export_folder_path = os.path.join(export_folder_path, addition)
            if not os.path.exists(export_folder_path):
                os.makedirs(export_folder_path)

        for file in fileNames:
            print('downloading: '+str(file))
            export_file = os.path.split(file)[1]
            export_file = os.path.join(export_folder_path, export_file)
            await gopro.http_command.download_file(camera_file=file, local_file=export_file)

            intTime = time.time()
            print(intTime-startTime)






        print("down")

        pass
        endTime = time.time()
        runTime = (endTime-startTime)/60
        print('total Time')
        print(runTime)


if __name__ == "__main__":
    cameraName = ['portMain', 'stbMain', 'jib', 'aftFacing', 'fwdFacing', 'transom']
    #cameraName = ['portMain', 'aftFacing']
    serialNumbers = ['14032', '09228', '09121', '09185', '05420', '38646']
    #serialNumbers = ['14032', '09185']
    format = [True, False, False, True, True, True]
    #format = [True, True]
    export_folder_path = '/media/camcontrol/veerignSSD2'
    threads = []
    def function_to_thread(params):
        asyncio.run(main(params[0], params[1], params[2], params[3]))

    for i in range(len(cameraName)):
        params = [serialNumbers[i], format[i], cameraName[i],export_folder_path]
        thread = threading.Thread(target=function_to_thread, args=(params,),name=params[2])
        threads.append(thread)
        thread.start()


    #while True:
     #   for thread in threads:
      #      if not thread.is_alive():
       #         print("Restarting "+str(thread.name))
        #        i = cameraName.index(thread.name)
         #       threads.remove(thread)
          #      params = [serialNumbers[i], format[i], cameraName[i],export_folder_path]
           #     print("Restartign with "+str(params))
            #    thread = threading.Thread(target=function_to_thread, args=(params,),name=params[2])
             #   threads.append(thread)
              #  thread.start()






