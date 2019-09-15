#pulling the data from a json file and correlating each word to its end
#time stamp

import json
file_name = 'hack_audio.json'

def time_to_word(file_name):
     # loading our json file
     with open(file_name, 'r') as f:
          word_time_dict = json.load(f)

     #getting to a list of dictionaries that contain info about each word
     list_of_dict = word_time_dict['monologues'][0]['elements']

     final_dict = {}
     articles = ['and', 'the', 'a']
     for a_dict in list_of_dict:
          if a_dict['type'] == 'text':
               if a_dict['value'] not in articles:
                    final_dict[a_dict['end_ts']] = a_dict['value']
     return final_dict