import asyncio
import time
import threading
import os
from datetime import datetime
from open_gopro import WiredGoPro
import open_gopro.models.constants as constants
from open_gopro import models
from open_gopro.domain.exceptions import FailedToFindDevice, ResponseTimeout
from open_gopro.util import setup_logging
import veeringVideo

log = setup_logging(__name__, "log.txt")

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
    log.info(cameraName + " is now online")

    async with WiredGoPro(gp) as gopro:

        if del_all:
            response = await gopro.http_command.delete_all_media()
            print("Delete All for "+str(cameraName)+" Finished with Response Code - "+str(response.status))
            log.info("Delete All for "+str(cameraName)+" Finished with Response Code - "+str(response.status))

        response = await gopro.http_command.set_date_time(date_time=datetime.now())
        print("Time Set for "+str(cameraName)+" Finished with Response Code - "+str(response.status))
        log.info("Time Set for "+str(cameraName)+" Finished with Response Code - "+str(response.status))

        response = await gopro.http_command.set_shutter(shutter=constants.Toggle.ENABLE)
        print(str(cameraName)+" Has started recording withResponse Code "+str(response.status))
        log.info("Has started recording withResponse Code "+str(response.status))

        state = True
        while state:
            await asyncio.sleep(180)
            response = await gopro.http_command.get_camera_state()
            state = response.data[constants.StatusId.ENCODING]
            if state:
                response = await gopro.http_command.get_camera_state()
                battery = response.data[constants.StatusId.INTERNAL_BATTERY_PERCENTAGE]
                sdCard = response.data[constants.StatusId.SD_CARD_REMAINING]
                temp = response.data[constants.StatusId.TEMPERATURE]
                log.info(str(cameraName)+" - "+str(battery)+" - "+str(sdCard)+" - "+str(temp))

        print(str(cameraName)+" Has stopped recording - Starting download")
        log.info(str(cameraName)+"Has stopped recording - Starting download")

        startTime = time.time()
        response = await (gopro.http_command).get_media_list()
        fileNames = []
        for i in range(len(response.data.media[0].file_system)):
            fileNames.append(response.data.media[0].file_system[i].filename)

        print(str(cameraName)+" has "+str(len(fileNames))+ "files to download and starts downloading at "+str(datetime.now().date()))

        export_folder_path = export_path
        for addition in [str(datetime.now().date()), cameraName]:
            export_folder_path = os.path.join(export_folder_path, addition)
            if not os.path.exists(export_folder_path):
                os.makedirs(export_folder_path)

        for file in fileNames:
            print("Fram"+str(cameraName)+" downloading: "+str(file)+" - "+str(fileNames.index(file))+" of "+str(len(fileNames)))
            export_file = os.path.split(file)[1]
            export_file = os.path.join(export_folder_path, export_file)
            response = await (gopro.http_command).download_file(camera_file=file, local_file=export_file)
            intTime = time.time()
            print("File # "+str(fileNames.index(file))+" Downloaded in "+str((intTime-startTime)/60)+"min - with Response Code "+str(response.status))

        pass
        endTime = time.time()
        print("Total Time to download "+str(cameraName)+" was - "+str((endTime-startTime)/60))

        folder,file = os.path.split(export_file)
        timeStamps = veeringVideo.Video_TimeStamping(folder)
        timeStamps.Add_CSV()

if __name__ == "__main__":
    cameraName = ['portMain', 'stbMain', 'jib', 'aftFacing', 'fwdFacing']
    serialNumbers = ['14032', '09228', '09121', '09185', '05420']
    format = [True, False, False, True, True]
    export_folder_path = '/mnt/camcontrol/FlyingJenny'
    threads = []

    def function_to_thread(params):
        asyncio.run(main(params[0], params[1], params[2], params[3]))

    for i in range(len(cameraName)):
        params = [serialNumbers[i], format[i], cameraName[i],export_folder_path]
        thread = threading.Thread(target=function_to_thread, args=(params,),name=params[2])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()







