from google.cloud.speech_v1p1beta1.types.cloud_speech import RecognitionConfig, SpeechContext
from nba_api.stats.library.parameters import PlayerExperience
from pydub import AudioSegment
import io
import os
from google.cloud import speech_v1p1beta1 as speech
import wave
import json
from google.cloud import storage
from nba_api.stats.endpoints import boxscoretraditionalv2

filepath = "C:\\Users\\visha\\Documents\\Python Scripts\\NBA-Defense_Analysis\\"

"""
from moviepy.editor import *
video = VideoFileClip("C:\\Users\\visha\\Documents\\Python Scripts\\NBA-Defense_Analysis\\Audio\\nba1.mp4")
video.audio.write_audiofile(filepath + "nba1.mp3")
"""


def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':    
        sound = AudioSegment.from_file(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name, timeout=120)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

def google_transcribe(audio_file_name):
    
    file_name = filepath + audio_file_name
    mp3_to_wav(file_name)

    audio_file_name = audio_file_name[:-3] + "wav"

    file_name = filepath + audio_file_name
    print(audio_file_name)
    # The name of the audio file to transcribe
    
    frame_rate, channels = frame_rate_channel(file_name)
    
    if channels > 1:
        stereo_to_mono(file_name)
    
    bucket_name = 'nbaaudioanalysis'
    source_file_name = filepath + audio_file_name
    destination_blob_name = audio_file_name
    
    upload_blob(bucket_name, source_file_name, destination_blob_name)
    
    gcs_uri = 'gs://nbaaudioanalysis/' + audio_file_name
    transcript = ''
    
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    print(type(audio))

    config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=frame_rate,
    language_code='en-US',
    model='video',
    enable_word_time_offsets=True,
    speech_contexts=[speech.types.SpeechContext(phrases=common_words)],
    enable_automatic_punctuation=True, 
    )

    # Detects speech in the audio file
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=10000)

    timeStamps = []

    for result in response.results:
        words_info = result.alternatives[0].words
        transcript += result.alternatives[0].transcript
        for word_info in words_info:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            timeStamps.append(
                {"Word" : word, 
                "Start_Time" : start_time.total_seconds(),
                "End_Time" : end_time.total_seconds()})
    
    #delete_blob(bucket_name, destination_blob_name)
    return transcript, timeStamps

def write_transcripts(output_Filepath, transcript_filename, timeStamps_filename, transcript, timeStampDict):
    f = open(output_Filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close()

    f = open(output_Filepath + timeStamps_filename, "w")
    json.dump(timeStampDict, f)
    f.close()

if __name__ == "__main__":
    for audio_file_name in os.listdir(filepath):
        if audio_file_name[-4:] == ".mp3":
            gameID = audio_file_name[:-4]
            output_filepath = "C:\\Users\\visha\\Documents\\Python Scripts\\NBA-Defense_Analysis\\" + gameID + "\\"
            os.mkdir(output_filepath)
            game = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=gameID)
            players = []
            for player in game.data_sets[0].data['data']:
                players.extend(player[5].split())
            print(players)
            common_words = players + ["defense", "block", "steal", "pick-and-roll", "depth", "box-out"]
            transcript, timeStampTranscript = google_transcribe(audio_file_name)
            transcript_filename = audio_file_name.split('.')[0] + '.txt'
            timeStamps_filename = audio_file_name.split('.')[0] + '.json'
            write_transcripts(output_filepath, transcript_filename, timeStamps_filename, transcript, timeStampTranscript)
        