from rev_ai import apiclient
import json
import time
from mutagen.mp3 import MP3

access_token  = '022gwT0xupiKtOgnqCY57Q0HpO1XSAiJEoTPYFMkZo_kLTv7x36ZdcNac3qFwiWhnRU4S0F84SMw15HM8iOeMe8gmeeWk'
client = apiclient.RevAiAPIClient('022gwT0xupiKtOgnqCY57Q0HpO1XSAiJEoTPYFMkZo_kLTv7x36ZdcNac3qFwiWhnRU4S0F84SMw15HM8iOeMe8gmeeWk')
file_name = 'hack_audio.mp3'
temp_file = file_name.split('.')
json_name = temp_file[0] + '.json'

def rev_json_from_mp3(file_name):
    audio = MP3(file_name)
    audio_length = audio.info.length

    #send local file
    job = client.submit_job_local_file(file_name)
    #job_details = client.get_job_details(job.id)

    time.sleep(audio_length/3.5 + 120)
    print('pause over')

    #transcribe as JSON
    transcript_json = client.get_transcript_json(job.id)

    #save file
    with open(json_name, 'w') as json_file:
        json.dump(transcript_json, json_file)

    print('done (:')

#rev_json_from_mp3(file_name)