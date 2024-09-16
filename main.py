from ui import Ui
from scheduler import Scheduler
import sys

sc = Scheduler()
ui = Ui(sc.menu_event, sc.update)
sc.set_ui_class(ui)

ui.run()

# ensure everything is closed, because the playing sound may block
# the application exit, if no explicit close statement exists
sys.exit()
