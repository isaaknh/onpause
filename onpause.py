# from sergio import *
# from isaak_2 import *
from helper import *
import time


#creation and running of media player
for filename in sys.argv[1:]:
    player = pyglet.media.Player()
    window = PlayerWindow(player)

    source = pyglet.media.load(filename)
    player.queue(source)

    window.gui_update_source()
    window.set_default_video_size()
    window.set_visible(True)

    player.play()
    window.gui_update_state()

pyglet.app.run()


