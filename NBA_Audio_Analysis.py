import json
import time
import string
import pandas as pd
import os
import cv2
import pytesseract
import matplotlib.pyplot as plt
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import numpy as np
#Set variables
rootdir = 'C:/Users/visha/Documents/Python Scripts/NBA-Defense_Analysis'

gameID = ''
videoFileName = ''
jsonFileName = ''
whichFile = 1
for subdir, dirs, files in os.walk(rootdir):
    print(dirs[whichFile])
    gameID = dirs[whichFile].split()[0]
    print(subdir)
    videoFileName = os.path.join(subdir, dirs[whichFile], gameID + '.mp4')
    jsonFileName = os.path.join(subdir, dirs[whichFile], gameID + '.json')
    print(videoFileName)
    break

broadcaster = "espn"

def getTime(filename, broadcaster, frameTime):
    vidcap = cv2.VideoCapture(filename)
    #length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    frame = frameTime*fps
    vidcap.set(1, frame)
    success, image = vidcap.read()
    ogimage = image
    if broadcaster.lower() == "espn":
        #For ESPN Streams
        image = image[580:610, 720:890]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        #For TNT Streams
        image = image[550:650, 800:1200]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.bitwise_not(image)
    image = cv2.resize(image, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    #image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    d = pytesseract.image_to_data(image, output_type=Output.DICT)
    n_boxes = len(d['level'])
    time = ""
    quarter = 0
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    """
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        if time == "" or quarter == 0:
            crop_img = image[y:y+h, x:x+w]
            str = pytesseract.image_to_string(crop_img)
            str = str.replace("\f", "")
            if ":" in str or "." in str and any(char.isdigit() for char in str):
                if time == "":
                    try:
                        index_sub_str = str.index(":")
                        if str[index_sub_str - 2].isdigit():
                            time += str[index_sub_str - 2]
                            time += str[index_sub_str - 1]
                            time += ":"
                            time += str[index_sub_str + 1 : index_sub_str + 3]
                        else:
                            time += str[index_sub_str - 1]
                            time += ":"
                            time += str[index_sub_str + 1 : index_sub_str + 3]
                    except:
                        index_sub_str = str.index(".")
                        if str[index_sub_str - 2].isdigit():
                            time += str[index_sub_str - 2]
                            time += str[index_sub_str - 1]
                            time += "."
                            time += str[index_sub_str + 1]
            """
            else:
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                crop_img = cv2.filter2D(crop_img, -1, kernel)
                crop_img = cv2.bitwise_not(crop_img)
                try:
                    num = int(pytesseract.image_to_string(crop_img))
                except Exception as e:
                    num = None
                    #Do Nothing
            """
            str = str.lower()
            if "1st" in str or "ist" in str:
                quarter = 1
            elif "2nd" in str:
                quarter = 2
            elif "3rd" in str:
                quarter = 3
            elif "4th" in str:
                quarter = 4
            elif "ot" in str:
                quarter = 5
            elif "2ot" in str:
                quarter = 6
            elif "3ot" in str:
                quarter = 7
            elif "4ot" in str:
                quarter = 8
        else:
            break
    return quarter, time, image

def stringTimeToInt(stringTime):
    if stringTime[1] == ":":
        intTime = int(stringTime[0])*60 + int(stringTime[-2:])
    else:
        intTime = int(stringTime[0:2])*60 + int(stringTime[-2:])
    return intTime

def getSentence(json_transcript, index):
    x = 0
    periodsFound = 0
    rightIndex = 0
    leftIndex = 0
    while periodsFound < 2:
        if periodsFound == -1 or periodsFound == 0:
            tempWord = json_transcript[i+x]["Word"]
            if "." in tempWord or "?" in tempWord or "!" in tempWord:
                rightIndex = i+x
                periodsFound = abs(periodsFound) + 1
        x += 1
        if periodsFound == 1 or periodsFound == 0:
            tempWord = json_transcript[i-x]["Word"]
            if "." in tempWord or "?" in tempWord or "!" in tempWord:
                leftIndex = i-x
                if periodsFound == 0:
                    periodsFound -= 1
                else:
                    periodsFound = 2
    return alldata[leftIndex + 1 : rightIndex + 1], rightIndex, leftIndex

#For play-by-play basically find what plays relate to possesion and the use 
#that as well what player relates to that stat to find which team has possesion
def WhoHasPossesion(time, quarter, df):
    findTime = stringTimeToInt(time)
    """
    for i in range(100):    
        print(df.iloc[i])
        input("Any Key: ")

    for col in df.columns:
        print(col)
    """
    for index, row in df.iterrows():
        if int(row["PERIOD"]) == quarter:      
            rowTime = stringTimeToInt(row["PCTIMESTRING"])
            if rowTime < findTime:
                tempIndex = index - 1
                lastPlayIndex = 0
                while lastPlayIndex == 0:
                    if df.iloc[tempIndex]["EVENTMSGTYPE"] == 1 or df.iloc[tempIndex]["EVENTMSGTYPE"] == 3 or df.iloc[tempIndex]["EVENTMSGTYPE"]== 4 or df.iloc[tempIndex]["EVENTMSGTYPE"] == 5:
                        lastPlayIndex = tempIndex
                        break
                    else:
                        tempIndex = tempIndex - 1
                    
                if lastPlayIndex != 0:
                    break
    playType = df.iloc[lastPlayIndex]["EVENTMSGTYPE"]
    returnValue = ""
    if playType == 1 or playType == 4 or playType == 5 or playType == 3:
        if playType == 5:
            if "Turnover" in df.iloc[lastPlayIndex]["HOMEDESCRIPTION"]:
                returnValue = "Home"
            else:
                returnValue = "Road"
        else:
            if playType == 4:
                if df.iloc[lastPlayIndex]["HOMEDESCRIPTION"] == None:
                    returnValue = "Road"
                else:
                    returnValue = "Home"
            if playType == 1:
                if df.iloc[lastPlayIndex]["HOMEDESCRIPTION"] == None:
                    returnValue =  "Home"
                else:
                    returnValue = "Road"
    nextPlayIndex = lastPlayIndex + 1
    while 1==1:
        playType = df.iloc[nextPlayIndex]["EVENTMSGTYPE"]
        if playType == 1 or playType == 4 or playType == 5 or playType == 3:
            timeDifNext = findTime - stringTimeToInt(df.iloc[nextPlayIndex]["PCTIMESTRING"])
            timeDifLast = findTime - stringTimeToInt(df.iloc[lastPlayIndex]["PCTIMESTRING"])
            return returnValue, timeDifNext, timeDifLast
        else:
            nextPlayIndex += 1

def TeamWithPossesion(roadOrHome, Home_Team, Road_Team):
    if roadOrHome == "Home":
        return HomeTeam
    else:
        return RoadTeam

from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import playbyplay
from nba_api.stats.endpoints import gamerotation

HomeTeam = gamerotation.GameRotation(gameID).get_dict()["resultSets"][1]["rowSet"][0][2]
RoadTeam = gamerotation.GameRotation(gameID).get_dict()["resultSets"][0]["rowSet"][0][2]

PBP = playbyplay.PlayByPlay(gameID).get_data_frames()[0]


box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=gameID)

#Get list of players
players = []
playersFormatted = []
playerTeams = []
for player in box_score.data_sets[0].data['data']:
    playerTeams.append(player[3])
    playerTeams.append(player[3])
    players.extend(player[5].split())
#players.extend(box_score.data_sets[2].data['data'][0][2:5])
#players.extend(box_score.data_sets[2].data['data'][-1][2:5])
for i in range(0, len(players)):
    playersFormatted.append(players[i].lower())

with open(jsonFileName, "r") as read_file:
    alldata = json.load(read_file)

alldataFormatted = []
for i in range(0, len(alldata)):
    alldataFormatted.append(alldata[i]["Word"].translate(str.maketrans("","", string.punctuation)).lower())

nameIndices = []
connotations = []
timeStamps = []
nameTeams = []

positiveAdjectives = ["good", "great", "terrific"]
negativeAdjectives = ["bad", "terrible", "poor", "miscommunication"]

#Have to implement phrases
negativePhrases = ["not in the right position"]

for i in range(0, len(alldataFormatted)):
    if alldataFormatted[i] == "defense" or alldataFormatted[i] == "box-out":
        
        """
        dictSentence, rightIndex, leftIndex = getSentence(alldata, i)
        sentence = ""
        for dictWord in dictSentence:
            word = dictWord["Word"].translate(str.maketrans("","", string.punctuation)).lower()
            sentence += (word + " ")
        #True is good, False is bad
        connotation = None
        nameIndex = -1
        for x in range(i + 1, rightIndex + 1):           
            if nameIndex == -1:
                if alldataFormatted[x] in playersFormatted:
                    nameIndex = playersFormatted.index(alldataFormatted[x])
            if connotation == None:
                if alldataFormatted[x] in positiveAdjectives:
                    connotation = True
                elif alldataFormatted[x] in negativeAdjectives:
                    connotation = False
            if nameIndex != -1 and connotation != None:
                break
        for x in range(i - 1, leftIndex, -1):
            if nameIndex == -1:
                if alldataFormatted[x] in playersFormatted:
                    nameIndex = playersFormatted.index(alldataFormatted[x])
            if connotation == None:
                if alldataFormatted[x] in positiveAdjectives:
                    connotation = True
                elif alldataFormatted[x] in negativeAdjectives:
                    connotation = False
            if nameIndex != -1 and connotation != None:
                break
        if connotation != None and nameIndex != -1:
            startTime = alldata[i]["Start_Time"]
            currQuarter, currTime, image = getTime(videoFileName, broadcaster, startTime)
            while ":" not in currTime or currQuarter == 0:
                startTime -= 1
                currQuarter, currTime, image = getTime(videoFileName, broadcaster, startTime)
            whoHasPossesion, time_Dif_Next, time_Dif_Last = WhoHasPossesion(currTime, currQuarter, PBP)
            teamWithPossesion = TeamWithPossesion(whoHasPossesion, HomeTeam, RoadTeam)
            if teamWithPossesion != playerTeams[nameIndex]:
                print(currTime, currQuarter)
                print(teamWithPossesion)
                timeStamps.append([alldata[leftIndex]["Start_Time"] + time_Dif_Last, alldata[leftIndex]["Start_Time"] + time_Dif_Next])
                nameIndices.append(nameIndex)
                nameTeams.append(playerTeams[nameIndex])
                connotations.append(connotation)
        """

"""
from moviepy.tools import subprocess_call
from moviepy.config import get_setting

print(timeStamps)
print("Hello")

def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)

    cmd = [get_setting("FFMPEG_BINARY"),"-y",
           "-ss", "%0.2f"%t1,
           "-i", filename,
           "-t", "%0.2f"%(t2-t1),
           #"-an",
           targetname]
    subprocess_call(cmd)

x = 0
for timeStamp in timeStamps:
    ffmpeg_extract_subclip(videoFileName, timeStamp[0], timeStamp[1], targetname=f"play{x}.mp4")
    x+=1
allinfo = []
for x in range(0, len(nameIndices)):
    allinfo.append({"Start_Time" : timeStamps[x][0], "End_Time" : timeStamps[x][1] - 1,
        "Connotation" : connotations[x], "Name" : players[nameIndices[x]], "Team" : nameTeams[x]})
with open('chunks_info.json', 'w') as outfile:
    json.dump(allinfo, outfile)
"""