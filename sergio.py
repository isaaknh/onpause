def decrement(time):
    '''time: a string in X:XX format
        returns: time 1 second before input'''
    minute = int(time[0])
    second = int(time[2:])
    #If the time is 0:00, we can't go back any further
    if minute <= 0 and second <= 0:
        return None
    if second == 0:
        return str(minute-1) + ':' + '59'
    else:
        if second - 1 < 10:
            return str(minute) + ':0' + str(second - 1)
        else:
            return str(minute) + ':' + str(second - 1)

def format_dict(decimal_dict):
    '''decimal_dict: dictionary as {X.XXX..:word}
        Makes copy and converts it to {X:XX:word} dict'''
    formatted_dict={}
    for entry in decimal_dict:
        formatted_dict[form(entry)]=decimal_dict[entry]
    return formatted_dict

def form(time):
    '''Takes a time in X.XX... and converts it to X:XX'''
    seconds = float('0.' + time[2:])
    formatted_seconds = (seconds * 60) / 100
    string_sec = str(round(formatted_seconds, 2))[2:4]
    if len(string_sec) == 1:
        return time[0] + ':' + string_sec + '0'
    else:
        return time[0] + ':' + string_sec

def display_words(timestamp,timestamp_to_word,word_number):
    ''' timestamp: Str time when video was paused
        timestamp_to_word: Dictionary containing REV data str:str
        total_words: Int odd# of words to return in list

        Returns: dictionary with {timestamp:word}, where the number of entries is the word_number
                closest words that come before timestamp.
        '''
    #Stores {time:word}
    result = {}
    current_time = timestamp
    while len(result) < word_number:
        if current_time is None: #If we reach 0:00
            break
        if current_time in timestamp_to_word:
            result[current_time]=timestamp_to_word[current_time]
        current_time = decrement(current_time)
    return result

def recent_words(a_dict,time_stamp, num_words = 3):

    #Dictionary in {'X:XX':'word'} format
    formatted_dict=format_dict(a_dict)

    return display_words(form(time_stamp),formatted_dict,num_words)







