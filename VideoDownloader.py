from pytube import YouTube
import youtube_dl
import time
import os

filepath = "C:\\Users\\visha\\Documents\\Python Scripts\\NBA-Defense_Analysis\\"

for file_name in os.listdir(filepath):
    if file_name[-4:] == ".mp3" or file_name[-4:] == ".mp4":
        try:
            os.rename(filepath+file_name, filepath+file_name[:-4]+"\\"+file_name)
        except:
            pass


"""
def downloadVideo(url):
    youtubeVideo = YouTube(url)
    downloaded = False
    while not downloaded:
        try:
            out_file = youtubeVideo.streams.filter(only_video=True, resolution="720p", file_extension="mp4")[0].download()
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            downloaded = True
        except Exception as e:
            print("Error Downloading ... Trying Again")
            print(e)
        time.sleep(1)
def downloadAudio(url):
    youtubeVideo = YouTube(url)
    downloaded = False
    while not downloaded:
        try:
            out_file = youtubeVideo.streams.filter(only_audio=True, file_extension="mp4")[0].download()
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            downloaded = True
        except Exception as e:
            print("Error Downloading ... Trying Again")
            print(e)
        time.sleep(1)

def newFuncAudio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg-location': './',
        'outtmpl': "./%(id)s.%(ext)s",
        'keepvideo': 'false'
    }
    _id = link.strip()
    meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(_id)

def newFuncVideo(link):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': "./%(id)s.%(ext)s",
    }
    _id = link.strip()
    meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(_id)

links = ['https://www.youtube.com/watch?v=wvM9VNFrLLU',
'https://www.youtube.com/watch?v=kLzDbqh_K4k',
'https://www.youtube.com/watch?v=JkrNl3x87no',
'https://www.youtube.com/watch?v=UThRbwtNbnE',
'https://www.youtube.com/watch?v=DOH4og6sRC0',
'https://www.youtube.com/watch?v=o2TKJPVAw_c',
'https://www.youtube.com/watch?v=1sIiR8LWqio',
'https://www.youtube.com/watch?v=9R9mKqQZWE4',
'https://www.youtube.com/watch?v=FXA8XdiqSXI',
'https://www.youtube.com/watch?v=ZKCTdpSGA6E',
'https://www.youtube.com/watch?v=bkMMEoF6owE',
'https://www.youtube.com/watch?v=sITD7nrOVos',
'https://www.youtube.com/watch?v=6sAFbDBBAZc',
'https://www.youtube.com/watch?v=-BhVP1sAo7c',
'https://www.youtube.com/watch?v=wL-a9Ql6-J0',
'https://www.youtube.com/watch?v=j6yDGNTyyzg',
'https://www.youtube.com/watch?v=AkiRMsuIZlQ',
'https://www.youtube.com/watch?v=zxb4EkhtUEQ',
'https://www.youtube.com/watch?v=-zzSYS3DRg0',
'https://www.youtube.com/watch?v=SB4exk_QQwU',
'https://www.youtube.com/watch?v=bWTvCZjQx3c',
'https://www.youtube.com/watch?v=6WPSYIdbhF8',
'https://www.youtube.com/watch?v=F7XPb0hlXAk',
'https://www.youtube.com/watch?v=ayQN1aJSy0o',
'https://www.youtube.com/watch?v=SnNSIiSs-Yk',
'https://www.youtube.com/watch?v=VTVINrxiKtM',
'https://www.youtube.com/watch?v=-fRuFW6j-TE',
'https://www.youtube.com/watch?v=0sDrYFtBOc4',
'https://www.youtube.com/watch?v=lKr5NocH5XM',
'https://www.youtube.com/watch?v=Y9Qw4vqhXvs',
'https://www.youtube.com/watch?v=A5uTixcmr9E',
'https://www.youtube.com/watch?v=EkYGl7OeDCM']
for link in links:
    newFuncAudio(link)
    newFuncVideo(link)
"""