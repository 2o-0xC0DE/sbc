import time, json
from dataclasses import dataclass
from enum import Enum
from playsound import playsound

class SoundType(Enum):
	FIRST_BELL = 1
	SECOND_BELL = 2
	BREAK = 3
	SILENT_MINUTE = 4

BELL_NAMES = {
	SoundType.FIRST_BELL:    "1-й дзвоник",
	SoundType.SECOND_BELL:   "2-й дзвоник",
	SoundType.BREAK:         "Перерва",
	SoundType.SILENT_MINUTE: "Хвилина мовчання"
}

CONFIG_VERSION = 0

DEFAULT_CONFIG = {
	"version": CONFIG_VERSION,
	"lessons_start": (8, 0),
	"silent_minute": (9, 0),
	"lesson_length": 40,
	"break_time": 5,
	"first_bell": 1,
	"num_lessons": 8,
	"workdays": (True, True, True, True, True, True, False),
	"sound_files": {
		"first_bell": "",
		"second_bell": "",
		"break": "",
		"silent_minute": ""
	}
}

@dataclass
class Bell:
	sound: SoundType
	hour: int
	minute: int
	played: bool = False

class Scheduler:
	def __init__(self) -> None:
		self.bells: list[Bell] = []
		self.bells_enabled: bool = True
		self.CONFIG_VERSION: int = CONFIG_VERSION # bypass for match-case statement insensitivity to non-class variables
		
		self.lessons_start: tuple = (None, None)
		self.silent_minute: tuple = (None, None)
		self.lesson_length: int = None
		self.break_time: int = None
		self.first_bell: int = None
		self.num_lessons: int = None
		self.workdays: list = None
		self.bell_sound_files: tuple = None
		self.load_config()

	def set_ui_class(self, ui_class) -> None:
		self.ui = ui_class
		self.ui.set_settings(self.lessons_start, self.silent_minute, self.lesson_length, self.break_time, self.first_bell, self.num_lessons, self.workdays, self.bell_sound_files)
		self.generate_bells()

	def apply_config(self):
		self.lessons_start, self.silent_minute, self.lesson_length, self.break_time, self.first_bell, self.num_lessons, self.workdays, self.bell_sound_files = self.ui.get_settings()

	def generate_bells(self) -> None:
		self.apply_config()
		
		self.bells = []
		if not self.workdays[time.localtime().tm_wday]:
			self.ui.set_schedule(self.get_bells_list())
			return

		self.bells.append(Bell(SoundType.SILENT_MINUTE, *self.silent_minute))
		day_minute: int = self.lessons_start[0] * 60 + self.lessons_start[1] - self.first_bell
		for lesson_number in range(self.num_lessons):
			if day_minute >= 0: # so that the lessons can't possibly start yesterday
				self.bells.append(Bell(SoundType.FIRST_BELL, day_minute // 60, day_minute % 60))
			day_minute += self.first_bell
			self.bells.append(Bell(SoundType.SECOND_BELL, day_minute // 60, day_minute % 60))
			day_minute += self.lesson_length
			self.bells.append(Bell(SoundType.BREAK, day_minute // 60, day_minute % 60))
			day_minute += self.break_time - self.first_bell

		self.bells = [bell for bell in self.bells if bell.hour <= 23]
		self.bells.sort(key=lambda bell: bell.hour * 60 + bell.minute)

		self.ui.set_schedule(self.get_bells_list())

	def get_bells_list(self) -> list[str]:
		return [f"{bell.hour:02}:{bell.minute:02} - {BELL_NAMES[bell.sound]}" for bell in self.bells]

	def menu_event(self, button) -> None:
		match button:
			case 0: self.generate_bells()
			case 1: self.save_config()
			case 2: self.bells_enabled = True
			case 3: self.bells_enabled = False

	def update(self):
		if not self.bells_enabled:
			return
		t = time.localtime()
		for bell_n, bell in enumerate(self.bells):
			if (not bell.played) and (bell.hour == t.tm_hour) and (bell.minute == t.tm_min):
				bell.played = True
				self.ui.select_bell(bell_n)
				match bell.sound:
					case SoundType.FIRST_BELL:    playsound(self.bell_sound_files[0])
					case SoundType.SECOND_BELL:   playsound(self.bell_sound_files[1])
					case SoundType.BREAK:         playsound(self.bell_sound_files[2])
					case SoundType.SILENT_MINUTE: playsound(self.bell_sound_files[3])
				return # there should be, in practice, no bells left. if you want to play two at the same time, what's wrong with you?

	def load_config(self):
		try:
			with open("config.json", "r") as fp:
				self.parse_config(json.load(fp))
		except (json.JSONDecodeError, OSError, KeyError):
			self.parse_config(DEFAULT_CONFIG) # now this shouldn't fail, or else you screwed up the default config 

	def parse_config(self, config):
		match config["version"]:
			case 0 | self.CONFIG_VERSION:
				self.lessons_start = config["lessons_start"]
				self.silent_minute = config["silent_minute"]
				self.lesson_length = config["lesson_length"]
				self.break_time    = config["break_time"]
				self.first_bell    = config["first_bell"]
				self.num_lessons   = config["num_lessons"]
				self.workdays      = config["workdays"]
				sf = config["sound_files"]
				self.bell_sound_files = (sf["first_bell"], sf["second_bell"], sf["break"], sf["silent_minute"])

	def save_config(self):
		with open("config.json", "w") as fp:
			c = self.ui.get_settings()
			config = {
				"version":       CONFIG_VERSION,
				"lessons_start": c[0],
				"silent_minute": c[1],
				"lesson_length": c[2],
				"break_time":    c[3],
				"first_bell":    c[4],
				"num_lessons":   c[5],
				"workdays":      c[6],
				"sound_files": {
					"first_bell":    c[7][0],
					"second_bell":   c[7][1],
					"break":         c[7][2],
					"silent_minute": c[7][3]
				}
			}
			json.dump(config, fp)
