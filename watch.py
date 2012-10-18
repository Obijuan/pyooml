import pyinotify
import os;


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        print "Modify!!", event.pathname
        os.system("python main.py > test.scad")

# Instanciate a new WatchManager (will be used to store watches).
wm = pyinotify.WatchManager()

handler = EventHandler()

# Associate this WatchManager with a Notifier (will be used to report and
# process events).
notifier = pyinotify.Notifier(wm, handler)


# Add a new watch on /tmp for ALL_EVENTS.
wm.add_watch('./main.py', pyinotify.IN_CLOSE_WRITE)


# Loop forever and handle events.
notifier.loop()

