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

#Select Video File
gameID = ''
videoFileName = ''
jsonFileName = ''
whichFile = 0
for subdir, dirs, files in os.walk(rootdir):
    print(dirs[whichFile])
    gameID = dirs[whichFile].split()[0]
    print(subdir)
    videoFileName = os.path.join(subdir, dirs[whichFile], gameID + '.mp4')
    print(videoFileName)
    break

#Get Box Score, PlaybyPlay and Game Rotation
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import playbyplay
from nba_api.stats.endpoints import gamerotation

HomeTeam = gamerotation.GameRotation(gameID).get_dict()["resultSets"][1]["rowSet"][0][2]
RoadTeam = gamerotation.GameRotation(gameID).get_dict()["resultSets"][0]["rowSet"][0][2]

from enum import Enum

#Setup enum for matching event msg number with an event name
class EventMsgType(Enum):
    FIELD_GOAL_MADE = 1
    FIELD_GOAL_MISSED = 2
    FREE_THROWfree_throw_attempt = 3
    REBOUND = 4
    TURNOVER = 5
    FOUL = 6
    VIOLATION = 7
    SUBSTITUTION = 8
    TIMEOUT = 9
    JUMP_BALL = 10
    EJECTION = 11
    PERIOD_BEGIN = 12
    PERIOD_END = 13

#Sort different types of calls into a dictionayr with key (event msg type) and value (array of descriptions)
PBP = playbyplay.PlayByPlay(gameID).get_data_frames()[0]
Calls = {}
for index, row in PBP.iterrows():
    if row["EVENTMSGTYPE"] != 12 and row["EVENTMSGTYPE"] != 13:
        if row["HOMEDESCRIPTION"] and row["VISITORDESCRIPTION"] != None:
            if EventMsgType(row["EVENTMSGTYPE"]).name in Calls:
                Calls[EventMsgType(row["EVENTMSGTYPE"]).name].append(row["HOMEDESCRIPTION"] + " - " + row["VISITORDESCRIPTION"])
            else:
                Calls[EventMsgType(row["EVENTMSGTYPE"]).name] = [row["HOMEDESCRIPTION"] + " - " + row["VISITORDESCRIPTION"]]
        elif row["HOMEDESCRIPTION"] and row["VISITORDESCRIPTION"] == None:
            pass
        else:
            if EventMsgType(row["EVENTMSGTYPE"]).name in Calls:
                Calls[EventMsgType(row["EVENTMSGTYPE"]).name].append(row["HOMEDESCRIPTION"]) if row["VISITORDESCRIPTION"] == None else Calls[EventMsgType(row["EVENTMSGTYPE"]).name].append(row["VISITORDESCRIPTION"])
            else:
                Calls[EventMsgType(row["EVENTMSGTYPE"]).name] = [row["HOMEDESCRIPTION"]] if row["VISITORDESCRIPTION"] == None else [row["VISITORDESCRIPTION"]]

#Turn dictionary into more easily accessible dataframe
SortedCalls = pd.DataFrame.from_dict(Calls, orient='index').T
print(SortedCalls)