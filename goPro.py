import asyncio
from open_gopro import WiredGoPro
import time
import threading


async def main(gp) -> None:


    async with WiredGoPro(gp) as gopro:
        startTime = time.time()
        response = await (gopro.http_command.get_media_list())
        fileNames = []
        for i in range(len(response.data.media[0].file_system)):
            print(i)
            fileNames.append(response.data.media[0].file_system[i].filename)

        print(fileNames)

        for file in fileNames:
            print('downloading: '+str(file))
            await gopro.http_command.download_file(camera_file=file, )

            intTime = time.time()
            print(intTime-startTime)




        print("down")

        pass
        endTime = time.time()
        runTime = (endTime-startTime)/60
        print('total Time')
        print(runTime)

if __name__ == "__main__":
    print('here1')
    def af():
        asyncio.run(main('14032'))

    def ff():
        asyncio.run(main('05420'))

    threading.Thread(target=af).start()
    print('here2')
    threading.Thread(target=ff).start()
    print('here3')

