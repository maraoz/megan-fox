from pyglet import window
from pyglet import clock
from pyglet import font

class SpaceGameWindow(window.Window):

    def __init__(self, *args, **kwargs):

        #Let all of the standard stuff pass through
        window.Window.__init__(self, *args, **kwargs)

    def main_loop(self):

        #Create a font for our FPS clock
        ft = font.load('Arial', 28)
        #The pyglet.font.Text object to display the FPS
        fps_text = font.Text(ft, y=10)

        while not self.has_exit:
            self.dispatch_events()
            self.clear()

            #Tick the clock
            clock.tick()
            #Gets fps and draw it
            fps_text.text = ("fps: %d") % (clock.get_fps())
            fps_text.draw()

            self.flip()

if __name__ == "__main__":
    # Someone is launching this directly
    space = SpaceGameWindow()
    space.main_loop()