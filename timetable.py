import time, threading, matrix
try:
	import RPi.GPIO as GPIO
except ImportError:
	print('GPIO module not found')

timetable = [
	["FREE", "MECH", "STATS", "FURTHER", "PHYS-CTE", "ISLAM", "CS-MWD"],
	["FREE", "FREE", "MECH", "CORE", "FURTHER", "CS-SCH", "PHYS-SBR"],
	["FREE", "CORE", "PHYS-CTE", "PHYS-SBR", "FREE", "STATS", "CS-SCH"],
	["STATS", "ISLAM", "CS-SCH", "CS-MWD", "CORE", "PHYS-SBR", "GAMES"],
	["CS-MWD", "STATS", "FREE", "PHYS-CTE", "CORE"]
]
periods = [((7,55),(8,45)), ((8,45),(9,35)), ((9,55),(10,45)),\
((10,45),(11,35)), ((11,35),(12,25)), ((13,55),(14,45)), ((14,45),(15,35))]
periods_thurs = [((7,55),(8,45)), ((8,45),(9,45)), ((9,35),(10,25)),\
((10,50),(11,40)), ((11,40),(12,30))]
cur_lesson="NONE"
remaining_lessons=[]

screen = matrix.pixelmatrix(dims=(8,8), BMP=0, _print=0)
#pin1 in top right
cathodes_led=(12,27,22,23,13,24,20,21)
anodes_led=(18,16,26,25,4,19,17,6)
#pin1 in bottom left
#cathodes_led=(6,24,25,17,16,27,19,26)
#anodes_led=(4,13,21,22,18,20,23,12)

def update():
	global cur_lesson
	global remaining_lessons
	tm = time.localtime()
	cur_time = (7,50)
	day = (tm.tm_wday + 1) % 7
	while True:
		cur_lesson=""
		if day < 5:
			remaining_lessons = list(timetable[day])
			for i, period in enumerate((periods_thurs if day == 4 else periods)):
				if cur_time < period[0]:
					break
				elif cur_time >= period[0] and cur_time < period[1]:
					cur_lesson = timetable[day][i]
				remaining_lessons.pop(0)
		else:
			remaining_lessons=[]
		print(cur_lesson, remaining_lessons)

		time.sleep(300)
		tm = time.localtime()
		day = (tm.tm_wday + 1) % 7
		while tm.tm_min % 5 != 0:
			time.sleep(15)
			tm = time.localtime()
		cur_time = (tm.tm_hour, tm.tm_min)

def led_modulate():
	global screen
	while True:
		for i, anode in enumerate(reversed(anodes_led)):
			row = [True if pixel == matrix.EMPTYTRIPLE else False for pixel in screen.matrix[i]]
			#print(row)
			try:
				for cathode, out in zip(reversed(cathodes_led), row):
					GPIO.output(cathode, out)
					pass
				GPIO.output(anode, True)
				time.sleep(0.002)
				GPIO.output(anode, False)
			except NameError:
				pass

try:
	GPIO.setmode(GPIO.BCM)
	for cathode in cathodes_led:
		GPIO.setup(cathode, GPIO.OUT)
		GPIO.output(cathode, False)
	for anode in anodes_led:
		GPIO.setup(anode, GPIO.OUT)
		GPIO.output(anode, True)
except NameError:
	pass

update_thread = threading.Thread(target=update)
update_thread.start()

led_thread = threading.Thread(target=led_modulate)
led_thread.start()

while True:
	if cur_lesson:
		screen.scrollText("NOW: "+cur_lesson)
		screen.scrollText(" ")
	try:
		screen.scrollText("NEXT: "+remaining_lessons[0])
		screen.scrollText(" ")
	except IndexError:
		if not cur_lesson:
			screen.scrollText("NO MORE LESSONS")
	try:
		screen.scrollText("THEN: "+remaining_lessons[1])
		screen.scrollText(" ")
	except IndexError:
		pass
