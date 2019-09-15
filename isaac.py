#!/usr/bin/env python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import sys

#from pyglet.gl import *
import pyglet
#from pyglet.window import key
import json
#import tkinter
from translate import Translator
import requests
#from threading import Thread

english_lst = []
translation_d = {}

def draw_rect(x, y, width, height):
    pyglet.gl.glBegin(pyglet.gl.GL_LINE_LOOP)
    pyglet.gl.glVertex2f(x, y)
    pyglet.gl.glVertex2f(x + width, y)
    pyglet.gl.glVertex2f(x + width, y + height)
    pyglet.gl.glVertex2f(x, y + height)
    pyglet.gl.glEnd()

class Control(pyglet.event.EventDispatcher):
    x = y = 0
    width = height = 10

    def __init__(self, parent):
        super(Control, self).__init__()
        self.parent = parent

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and  
                self.y < y < self.y + self.height)

    def capture_events(self):
        self.parent.push_handlers(self)

    def release_events(self):
        self.parent.remove_handlers(self)

class Button(Control):
    charged = False

    def draw(self):
        if self.charged:
            pyglet.gl.glColor3f(1, 0, 0)
        draw_rect(self.x, self.y, self.width, self.height)
        pyglet.gl.glColor3f(1, 1, 1)
        self.draw_label()

    def on_mouse_press(self, x, y, button, modifiers):
        self.capture_events()
        self.charged = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.charged = self.hit_test(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        if self.hit_test(x, y):
            self.dispatch_event('on_press')
        self.charged = False

Button.register_event_type('on_press')
    
class TextButton(Button):
    def __init__(self, *args, **kwargs):
        super(TextButton, self).__init__(*args, **kwargs)
        self._text = pyglet.text.Label('', anchor_x='center', anchor_y='center')

    def draw_label(self):
        self._text.x = self.x + self.width / 2
        self._text.y = self.y + self.height / 2
        self._text.draw()

    def set_text(self, text):
        self._text.text = text

    text = property(lambda self: self._text.text,
                    set_text)

class Slider(Control):
    THUMB_WIDTH = 6
    THUMB_HEIGHT = 10
    GROOVE_HEIGHT = 2

    def draw(self):
        center_y = self.y + self.height / 2
        draw_rect(self.x, center_y - self.GROOVE_HEIGHT / 2, 
                  self.width, self.GROOVE_HEIGHT)
        pos = self.x + self.value * self.width / (self.max - self.min)
        draw_rect(pos - self.THUMB_WIDTH / 2, center_y - self.THUMB_HEIGHT / 2, 
                  self.THUMB_WIDTH, self.THUMB_HEIGHT)

    def coordinate_to_value(self, x):
        return float(x - self.x) / self.width * (self.max - self.min) + self.min

    def on_mouse_press(self, x, y, button, modifiers):
        value = self.coordinate_to_value(x)
        self.capture_events()
        self.dispatch_event('on_begin_scroll')
        self.dispatch_event('on_change', value)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        value = min(max(self.coordinate_to_value(x), self.min), self.max)
        self.dispatch_event('on_change', value)
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        self.dispatch_event('on_end_scroll')

Slider.register_event_type('on_begin_scroll')
Slider.register_event_type('on_end_scroll')
Slider.register_event_type('on_change')

class PlayerWindow(pyglet.window.Window):
    GUI_WIDTH = 400
    GUI_HEIGHT = 40
    GUI_PADDING = 4
    GUI_BUTTON_HEIGHT = 16

    def __init__(self, player):
        super(PlayerWindow, self).__init__(caption='Media Player',
                                           visible=False, 
                                           resizable=True)
        self.player = player
        self.player.push_handlers(self)
        # TODO compat #self.player.eos_action = self.player.EOS_PAUSE

        self.slider = Slider(self)
        self.slider.x = self.GUI_PADDING
        self.slider.y = self.GUI_PADDING * 2 + self.GUI_BUTTON_HEIGHT
        self.slider.on_begin_scroll = lambda: player.pause()
        # time_stamps.append(self.player.time)
        # print (time_stamps)
        self.slider.on_end_scroll = lambda: player.play()
        self.slider.on_change = lambda value: player.seek(value)

        self.play_pause_button = TextButton(self)
        self.play_pause_button.x = self.GUI_PADDING
        self.play_pause_button.y = self.GUI_PADDING
        self.play_pause_button.height = self.GUI_BUTTON_HEIGHT
        self.play_pause_button.width = 45
        self.play_pause_button.on_press = self.on_play_pause

        win = self
        self.window_button = TextButton(self)
        self.window_button.x = self.play_pause_button.x + \
                               self.play_pause_button.width + self.GUI_PADDING
        self.window_button.y = self.GUI_PADDING
        self.window_button.height = self.GUI_BUTTON_HEIGHT
        self.window_button.width = 90
        self.window_button.text = 'Windowed'
        self.window_button.on_press = lambda: win.set_fullscreen(False)

        self.controls = [
            self.slider, 
            self.play_pause_button,
            self.window_button,
        ]

        x = self.window_button.x + self.window_button.width + self.GUI_PADDING
        i = 0
        for screen in self.display.get_screens():
            screen_button = TextButton(self)
            screen_button.x = x
            screen_button.y = self.GUI_PADDING
            screen_button.height = self.GUI_BUTTON_HEIGHT
            screen_button.width = 80
            screen_button.text = 'Screen %d' % (i + 1)
            screen_button.on_press = \
                (lambda s: lambda: win.set_fullscreen(True, screen=s))(screen)
            self.controls.append(screen_button)
            i += 1
            x += screen_button.width + self.GUI_PADDING


    def on_eos(self):
        self.gui_update_state()

    def gui_update_source(self):
        if self.player.source:
            source = self.player.source
            self.slider.min = 0.
            self.slider.max = source.duration
        self.gui_update_state()

    def gui_update_state(self):
        if self.player.playing:
            self.play_pause_button.text = 'Pause'
        else:
            self.play_pause_button.text = 'Play'

    def get_video_size(self):
        if not self.player.source or not self.player.source.video_format:
            return 0, 0
        video_format = self.player.source.video_format
        width = video_format.width
        height = video_format.height
        if video_format.sample_aspect > 1:
            width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            height /= video_format.sample_aspect
        return width, height

    def set_default_video_size(self):
        '''Make the window size just big enough to show the current
        video and the GUI.'''
        width = self.GUI_WIDTH
        height = self.GUI_HEIGHT
        video_width, video_height = self.get_video_size()
        width = max(width, video_width)
        height += video_height
        self.set_size(int(width), int(height))

    def on_resize(self, width, height):
        '''Position and size video image.'''
        super(PlayerWindow, self).on_resize(width, height)

        self.slider.width = width - self.GUI_PADDING * 2

        height -= self.GUI_HEIGHT
        if height <= 0:
            return

        video_width, video_height = self.get_video_size()
        if video_width == 0 or video_height == 0:
            return

        display_aspect = width / float(height)
        video_aspect = video_width / float(video_height)
        if video_aspect > display_aspect:
            self.video_width = width
            self.video_height = width / video_aspect
        else:
            self.video_height = height
            self.video_width = height * video_aspect
        self.video_x = (width - self.video_width) / 2
        self.video_y = (height - self.video_height) / 2 + self.GUI_HEIGHT

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:
            if control.hit_test(x, y):
                control.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.on_play_pause()
        elif symbol == key.ESCAPE:
            self.dispatch_event('on_close')

    def on_close(self):
        self.player.pause()
        #time_stamps.append(self.player.time)
        # print (time_stamps)
        self.close()

    def on_play_pause(self):
        if self.player.playing:
            self.player.pause()


            #sergio's code
            def closest_words(pause_time,dictionary,word_count = 2):
                '''pause_time (float): time in seconds when video was paused
                    dictionary: Stores timestamps to words as {X.XX:'word'}
                    word_count (int): # of words desired in output
                    
                    returns: dictionary with word_count most recent words at given timestamp
                            {x.xx:'word'}'''

                result={}
                current = round(pause_time + 0.5 ,2)
                list_of_timez = []
                #While we still need more words to output
                while len(result)<word_count:
                    
                    #If we go back to time 0, no more words exist
                    if current<=0:
                        break
                    #If the current timestamp contains a word, save to output
                    if current in dictionary:
                        result[current] = dictionary[current]

                    #Look at earlier timestamp for more words
                    current = round(current-0.01,2)

                list_of_timez = sorted(result.keys())
                return (result,list_of_timez)

            

            #isaak's code
            def time_to_word(file_name):
                # loading our json file
                with open(file_name, 'r') as f:
                    word_time_dict = json.load(f)

                #getting to a list of dictionaries that contain info about each word
                list_of_dict = word_time_dict['monologues'][0]['elements']

                final_dict = {}
                list_of_time_stamps = []
                articles = ['and', 'the', 'a']
                for a_dict in list_of_dict:
                    if a_dict['type'] == 'text':
                        if a_dict['value'] not in articles:
                                final_dict[a_dict['end_ts']] = a_dict['value']
                                list_of_time_stamps.append(a_dict['end_ts'])
                list_of_time_stamps.sort()
                return (final_dict,list_of_time_stamps)


            #instantiating file name
            #creating final dict using functions defined above
            file_name = 'hack_audio.json'
            time_stamp = self.player.time
            a_dict = time_to_word(file_name)[0]
            list_of_times = closest_words(time_stamp,a_dict)[1]

            final_dict = closest_words(time_stamp,a_dict)[0]
            
            def corr_dict(L1, L2):
                dict_o = {}
                for t in range(len(L1)):
                    dict_o[L1[t]] = L2[t]
                return dict_o

            #Set Languages Of Translation
            lang_codes = ["ar","bn","es","fr","hi","id","pt","ru","zh", "ur", "en"]
            lang_names = ["Arabic", "Bengali", "Spanish", "French", "Hindi", "Indonesian", "Portuguese", "Russian", "Chinese", "Urdu", "English"]

            lang_dict = corr_dict(lang_codes, lang_names)
            
            def get_spanish_dict(word):

                app_id = "f253b36c"
                app_key = "05154548fb10d80a43f8705e23a4c4c9"
                language = "es"
                word_id = word
                url = "https://od-api.oxforddictionaries.com/api/v2/entries/" + language + "/" + word_id.lower()
                r = requests.get(url, headers={"app_id":app_id, "app_key":app_key})
                print((r).json())

                return ((r).json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'])


            #Find Words Needed
            transcription_dict = final_dict
            
            times_list = sorted(transcription_dict.keys())

            english_lst = []

            for time in times_list:
                english_lst.append(transcription_dict[time]) 

            #Translation
            from_l = 'en'
            to_l = 'es'
            #input(lang_names + "Which language would you like? "), TBA
            translator = Translator(from_lang=from_l, to_lang=to_l)
            
            translation_d = {}

    
            #translating and grabbing definition
            for word in english_lst:
                inter_list = []

                translation = translator.translate(word)
                inter_list.append(translation)
                
                try:
                    inter_list.append(get_spanish_dict(translation))
                except:
                    inter_list.append("Aun no tenemos esta palabra en nuestro diccionario. Lo siento")
                    
                translation_d[word] = inter_list#, definition

            #Initialization Of GUI

            window = pyglet.window.Window(1500,200)
            label = pyglet.text.Label(str(translation_d) ,font_name='Times New Roman',font_size=12,x= window.width//2, y=window.height//2,anchor_x='center', anchor_y='center')
            

            @window.event
            def on_draw():
                window.clear()
                label.draw()
            pyglet.app.run()
            


        else:
            if self.player.time >= self.player.source.duration:
                self.player.seek(0)
            self.player.play()
        self.gui_update_state()




    def on_draw(self):
        self.clear()
        
        # Video
        if self.player.source and self.player.source.video_format:
            self.player.get_texture().blit(self.video_x,
                                           self.video_y,
                                           width=self.video_width,
                                           height=self.video_height)

        # GUI
        self.slider.value = self.player.time
        for control in self.controls:
            control.draw()


# def tkloop(english_lst,translation_d):
#     window = tkinter.Tk()
#     window.title("Captions")
#     print('swag')
#     def trans(word):
#         return tkinter.Label(window, width = 10, text = translation_d[word]).pack()

#     for item in english_lst:
#         tkinter.Button(window, width = 10, text = item, command = trans(item)).pack()

#     window.mainloop()