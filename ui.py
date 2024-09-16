from PySide6 import QtWidgets, QtGui, QtCore
import time

VERSION = "0.1.0"
DAYS_OF_WEEK = "Понеділок Вівторок Середа Четвер П'ятниця Субота Неділя".split()

class Ui:
	def __init__(self, menu_callback, periodic_task):
		self.app = QtWidgets.QApplication([])
		self.app.setQuitOnLastWindowClosed(False)
		self.window = MainWindow()
		self.menu_actions = MenuActions(self.window, menu_callback)
		self.menu_bar = MenuBar(self.window, self.menu_actions)
		self.toolbar = ToolBar(self.window, self.menu_actions)
		self.tray = Tray(self.window)

		# timer for starting bells
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(periodic_task)
		self.timer.start(1000)

	def run(self):
		self.window.show()
		self.tray.setVisible(True)
		self.app.exec()

	def get_settings(self):
		return self.window.get_settings()

	def set_settings(self, *args):
		self.window.set_settings(*args)

	def set_schedule(self, bells):
		self.window.set_schedule(bells)

	def select_bell(self, bell_n):
		self.window.select_bell(bell_n)

class Tray(QtWidgets.QSystemTrayIcon):
	def __init__(self, window):
		super().__init__()
		self.window = window
		self.setIcon(QtGui.QIcon("icon.png"))
		self.setVisible(True)

		self.menu = QtWidgets.QMenu(self.window)
		open_window = QtGui.QAction("Показати головне вікно", self)
		close_all = QtGui.QAction("Вийти", self)
		open_window.triggered.connect(self.window.show)
		close_all.triggered.connect(self.close_all_diag)
		self.menu.addAction(open_window)
		self.menu.addAction(close_all)
		self.setContextMenu(self.menu)

	def close_all_diag(self):
		if QtWidgets.QMessageBox.question(self.window, "SBC - Вихід", \
			"Ви дійсно хочете вийти з програми? Після цього дітки кричатимуть чого в них уроки по 5 годин...", \
			QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No) == QtWidgets.QMessageBox.StandardButton.Yes:
			exit()

class MenuActions:
	def __init__(self, window, callback):
		self.window = window
		self.callback = callback
		self.button_apply = QtGui.QAction(QtGui.QIcon("apply.png"), "Застосувати",           window)
		self.button_save  = QtGui.QAction(QtGui.QIcon("save.png"),  "Зберегти налаштування", window)
		self.button_start = QtGui.QAction(QtGui.QIcon("start.png"), "Запустити дзвоники",    window)
		self.button_stop  = QtGui.QAction(QtGui.QIcon("stop.png"),  "Зупинити все",          window)
		self.button_about = QtGui.QAction(                          "Про програму",          window)

		self.button_start.setEnabled(False)

		self.button_apply.triggered.connect(lambda: self.handle_button(0))
		self.button_save .triggered.connect(lambda: self.handle_button(1))
		self.button_start.triggered.connect(lambda: self.handle_button(2))
		self.button_stop .triggered.connect(lambda: self.handle_button(3))
		self.button_about.triggered.connect(lambda: self.handle_button(4))

	def handle_button(self, button):
		match button:
			case 0 | 1 | 2 | 3:
				self.callback(button)
				match button:
					case 0: QtWidgets.QMessageBox.information(self.window, "SBC - Інформація", "Налаштування застосовано!")
					case 1: QtWidgets.QMessageBox.information(self.window, "SBC - Інформація", "Налаштування збережено!")
					case 2:
						self.button_start.setEnabled(False)
						self.button_stop .setEnabled(True) 
						QtWidgets.QMessageBox.information(self.window, "SBC - Інформація", "Дзвінки запущено. Якщо ви налаштували щось не так, самі винні!")
					case 3:
						self.button_start.setEnabled(True)
						self.button_stop .setEnabled(False)
						QtWidgets.QMessageBox.information(self.window, "SBC - Інформація", "Дзвінки зупинено. Щось пішло не так, еге ж? Піди і виправи це негайно!")
			case 4: QtWidgets.QMessageBox.information(self.window, "SBC - Про програму", \
				f"SBC v.{VERSION}\nАвтор: 2o\nTelegram: @xfdtw\nDiscord: @2o___\nЯкщо щось не зрозуміло/не працює пишіть туди.")

class ToolBar(QtWidgets.QToolBar):
	def __init__(self, window, menu_actions):
		super().__init__("Toolbar")
		window.addToolBar(self)
		self.setIconSize(QtCore.QSize(16, 16))

		self.addAction(menu_actions.button_apply)
		self.addAction(menu_actions.button_save)
		self.addSeparator()
		self.addAction(menu_actions.button_start)
		self.addAction(menu_actions.button_stop)	

class MenuBar(QtWidgets.QMenuBar):
	def __init__(self, window, menu_actions):
		super().__init__()
		window.setMenuBar(self)
		self.settings_menu = self.addMenu("&Налаштування")
		self.bells_menu    = self.addMenu("&Дзвінки")
		self.help_menu     = self.addMenu("Д&опомога")

		self.settings_menu.addAction(menu_actions.button_apply)
		self.settings_menu.addAction(menu_actions.button_save)
		self.bells_menu.addAction(menu_actions.button_start)
		self.bells_menu.addAction(menu_actions.button_stop)
		self.help_menu.addAction(menu_actions.button_about)

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("SBC - Головне вікно")
		self.setWindowIcon(QtGui.QIcon("icon.png"))
		self.setMinimumSize(800, 600)
		self.main_widget = QtWidgets.QWidget()
		self.main_layout = QtWidgets.QGridLayout(self.main_widget)

		self.bell_status_box = BellStatusBox()
		self.schedule_box = ScheduleBox()
		self.days_select_box = DaysSelectBox()
		self.status_box = StatusBox()
		self.sound_files_box = SoundFilesBox()

		self.main_layout.addWidget(self.bell_status_box, 0, 0, 2, 1)
		self.main_layout.addWidget(self.schedule_box,    0, 1, 1, 1)
		self.main_layout.addWidget(self.days_select_box, 1, 1, 1, 1)
		self.main_layout.addWidget(self.status_box,      0, 2, 1, 1)
		self.main_layout.addWidget(self.sound_files_box, 1, 2, 1, 1)
		self.setCentralWidget(self.main_widget)

	def get_settings(self):
		first_lesson_input  = self.schedule_box.first_lesson_input .time()
		silent_minute_input = self.schedule_box.silent_minute_input.time()

		first_lesson  = (first_lesson_input .hour(), first_lesson_input .minute())
		silent_minute = (silent_minute_input.hour(), silent_minute_input.minute())
		lesson_length = self.schedule_box.lesson_length_input.value()
		break_length  = self.schedule_box.break_length_input .value()
		first_bell    = self.schedule_box.first_bell_input   .value()
		num_lessons   = self.schedule_box.num_lessons_input  .value()
		workdays = [checkbox.isChecked() for checkbox in self.days_select_box.days_checkboxes]
		sound_files = (
			self.sound_files_box.first_bell_file_text   .text(),
			self.sound_files_box.second_bell_file_text  .text(),
			self.sound_files_box.break_file_text        .text(),
			self.sound_files_box.silent_minute_file_text.text()
		)

		return (first_lesson, silent_minute, lesson_length, break_length, first_bell, num_lessons, workdays, sound_files)

	def set_settings(self, *args):
		self.schedule_box.first_lesson_input .setTime (QtCore.QTime(*args[0]))
		self.schedule_box.silent_minute_input.setTime (QtCore.QTime(*args[1]))
		self.schedule_box.lesson_length_input.setValue(args[2])
		self.schedule_box.break_length_input .setValue(args[3])
		self.schedule_box.first_bell_input   .setValue(args[4])
		self.schedule_box.num_lessons_input  .setValue(args[5])
		for i in range(0, 7): self.days_select_box.days_checkboxes[i].setChecked(args[6][i])
		self.sound_files_box.first_bell_file_text   .setText(args[7][0])
		self.sound_files_box.second_bell_file_text  .setText(args[7][1])
		self.sound_files_box.break_file_text        .setText(args[7][2])
		self.sound_files_box.silent_minute_file_text.setText(args[7][3])

	def set_schedule(self, bells):
		self.bell_status_box.bells_list.clear()
		for bell in bells:
			self.bell_status_box.bells_list.addItem(bell)

	def select_bell(self, bell_n):
		self.bell_status_box.bells_list.setCurrentItem(self.bell_status_box.bells_list.item(bell_n))

class BasicBox(QtWidgets.QScrollArea):
	def __init__(self, title):
		super().__init__()
		self.widget = QtWidgets.QWidget()
		self.setWidgetResizable(True)
		self.setWidget(self.widget)
		self.layout = QtWidgets.QVBoxLayout(self.widget)
		font = QtGui.QFont()
		font.setPointSize(16)
		title = QtWidgets.QLabel(title)
		title.setFont(font)
		self.layout.addWidget(title)

class BellStatusBox(BasicBox):
	def __init__(self):
		super().__init__("Розклад дзвінків")
		self.bells_list = QtWidgets.QListWidget()
		self.layout.addWidget(self.bells_list)

class ScheduleBox(BasicBox):
	def __init__(self):
		super().__init__("Налаштування розкладу")
		self.grid_widget = QtWidgets.QWidget()
		self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
		self.grid_widget.setLayout(self.grid_layout)

		self.first_lesson_input  = QtWidgets.QTimeEdit(QtCore.QTime(8, 0))
		self.silent_minute_input = QtWidgets.QTimeEdit(QtCore.QTime(9, 0))
		self.lesson_length_input = QtWidgets.QSpinBox()
		self.break_length_input  = QtWidgets.QSpinBox()
		self.first_bell_input    = QtWidgets.QSpinBox()
		self.num_lessons_input   = QtWidgets.QSpinBox()

		self.lesson_length_input.setRange(20, 90)
		self.break_length_input.setRange(2, 59)
		self.first_bell_input.setRange(1, 4)
		self.num_lessons_input.setRange(1, 20)

		self.break_length_input.valueChanged.connect(self.update_limits)

		self.grid_layout.addWidget(QtWidgets.QLabel("Перший урок о"),      0, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Хвилина мовчання о"), 1, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Тривалість уроку:"),  2, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Перерва"),            3, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Перший дзвоник за"),  4, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Кількість уроків:"),  5, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("хвилин"),             2, 2)
		self.grid_layout.addWidget(QtWidgets.QLabel("хвилин"),             3, 2)
		self.grid_layout.addWidget(QtWidgets.QLabel("хвилин до уроку"),    4, 2)
		self.grid_layout.addWidget(self.first_lesson_input,  0, 1)
		self.grid_layout.addWidget(self.silent_minute_input, 1, 1)
		self.grid_layout.addWidget(self.lesson_length_input, 2, 1)
		self.grid_layout.addWidget(self.break_length_input,  3, 1)
		self.grid_layout.addWidget(self.first_bell_input,    4, 1)
		self.grid_layout.addWidget(self.num_lessons_input,   5, 1)

		self.layout.addWidget(self.grid_widget)
		self.layout.addStretch(1)

	def update_limits(self, value):
		self.first_bell_input.setRange(1, value - 1)

class DaysSelectBox(BasicBox):
	def __init__(self):
		super().__init__("Робочі дні")
		self.days_checkboxes = []
		for day_name in DAYS_OF_WEEK:
			self.days_checkboxes.append(QtWidgets.QCheckBox(day_name))
			self.layout.addWidget(self.days_checkboxes[-1])
		self.layout.addStretch(1)

class StatusBox(BasicBox):
	def __init__(self):
		super().__init__("Стан")
		self.grid_widget = QtWidgets.QWidget()
		self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
		self.grid_widget.setLayout(self.grid_layout)

		self.day_of_week_widget = QtWidgets.QLabel()
		self.current_time_widget = QtWidgets.QLabel()
		self.uptime_widget = QtWidgets.QLabel()
		self.grid_layout.addWidget(QtWidgets.QLabel("День тижня:"),    0, 0)
		self.grid_layout.addWidget(self.day_of_week_widget,            0, 1)
		self.grid_layout.addWidget(QtWidgets.QLabel("Поточний час:"),  1, 0)
		self.grid_layout.addWidget(self.current_time_widget,           1, 1)
		self.grid_layout.addWidget(QtWidgets.QLabel("Зі запуску:"),    2, 0)
		self.grid_layout.addWidget(self.uptime_widget,                 2, 1)

		self.layout.addWidget(self.grid_widget)
		self.layout.addStretch(1)

		self.uptime_timer = QtCore.QElapsedTimer()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.uptime_timer.start()
		self.timer.start(1000)
		self.update()

	def update(self):
		t = time.localtime()
		self.day_of_week_widget.setText(DAYS_OF_WEEK[t.tm_wday])
		self.current_time_widget.setText(f"{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}")
		seconds = self.uptime_timer.elapsed() / 1000
		minutes = seconds / 60
		hours = minutes / 60
		days = hours / 24
		self.uptime_widget.setText(f"{int(days)} днів, {int(hours % 24):02}:{int(minutes % 60):02}:{int(seconds % 60):02}")

class SoundFilesBox(BasicBox):
	def __init__(self):
		super().__init__("Звуки")
		self.grid_widget = QtWidgets.QWidget()
		self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
		self.grid_widget.setLayout(self.grid_layout)

		self.first_bell_file_text      = QtWidgets.QLabel()
		self.second_bell_file_text     = QtWidgets.QLabel()
		self.break_file_text           = QtWidgets.QLabel()
		self.silent_minute_file_text   = QtWidgets.QLabel()
		self.first_bell_file_button    = QtWidgets.QPushButton("Огляд")
		self.second_bell_file_button   = QtWidgets.QPushButton("Огляд")
		self.break_file_button         = QtWidgets.QPushButton("Огляд")
		self.silent_minute_file_button = QtWidgets.QPushButton("Огляд")

		self.first_bell_file_button   .clicked.connect(lambda: self.file_select_diag(0))
		self.second_bell_file_button  .clicked.connect(lambda: self.file_select_diag(1))
		self.break_file_button        .clicked.connect(lambda: self.file_select_diag(2))
		self.silent_minute_file_button.clicked.connect(lambda: self.file_select_diag(3))

		self.grid_layout.addWidget(QtWidgets.QLabel("Перший дзвоник:"),   0, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Другий дзвоник:"),   1, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Перерва:"),          2, 0)
		self.grid_layout.addWidget(QtWidgets.QLabel("Хвилина мовчання:"), 3, 0)
		self.grid_layout.addWidget(self.first_bell_file_text,             0, 1)
		self.grid_layout.addWidget(self.second_bell_file_text,            1, 1)
		self.grid_layout.addWidget(self.break_file_text,                  2, 1)
		self.grid_layout.addWidget(self.silent_minute_file_text,          3, 1)
		self.grid_layout.addWidget(self.first_bell_file_button,           0, 2)
		self.grid_layout.addWidget(self.second_bell_file_button,          1, 2)
		self.grid_layout.addWidget(self.break_file_button,                2, 2)
		self.grid_layout.addWidget(self.silent_minute_file_button,        3, 2)

		self.layout.addWidget(self.grid_widget)
		self.layout.addStretch(1)

	def file_select_diag(self, sound_type):
		file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self.grid_widget, "SBC - Відкрити файл", "", "Підтримувані файли (*.wav *.mp3 *.flac)")
		if file_name is None:
			return
		match sound_type:
			case 0: self.first_bell_file_text   .setText(file_name)
			case 1: self.second_bell_file_text  .setText(file_name)
			case 2: self.break_file_text        .setText(file_name)
			case 3: self.silent_minute_file_text.setText(file_name)
