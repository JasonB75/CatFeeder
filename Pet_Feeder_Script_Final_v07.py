import I2C_LCD_driver
import CatFeeder
import time
import RPi.GPIO as GPIO
import datetime
import random
from subprocess import call
import smtplib
import pickle
import EmptyMachine

#Sets the GPIO to the BCM state
GPIO.setmode(GPIO.BCM) 
#Intalizes the Display
mylcd = I2C_LCD_driver.lcd()

#Loads the specific GPIO pins into the program
GPIO.setup(12,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21,GPIO.IN, pull_up_down=GPIO.PUD_UP)


DEBOUCE_TIME = 500 #Sets the defualt debouce time for the buttons

currentScreen1 = 0 #This variable is used to determin what screen the program is putting to the display

mylcd.lcd_clear() # Clears the display


blinkingText = True
Running = True
blinkingTextChar = 0
runnum = 0
clockPlace = 1
isFeeding = True
feedCountDown = 75
changeTimeMin = 5

editFeedTimeNum = 2
viewFeedTimeNum =1
seeingFeedTimeNum = 11
powerOffNum1 = 3
powerOffNum2 = 4
editBreakNum = 21
editDinnerNum = 31
stopScriptNum = 45
emptyMachineNum = 55


""" 
'The following functions act as callbacks. AKA when a button is pressed they are called. 
'They will act as the navigational views for the program to set feed times
"""
def setScreen(num):
	global currentScreen1
	currentScreen1  = num
	print currentScreen1

def callBack_backBut(channel):
	print "back Button hit"
	global currentScreen1
	global blinkingTextChar
	if currentScreen1 == 0:
		first_screen(channel)
	
	elif currentScreen1 == seeingFeedTimeNum:
		first_screen(channel)
		
	elif currentScreen1 == viewFeedTimeNum:
		mylcd.lcd_clear()
		currentScreen1 = 0
	elif currentScreen1 == powerOffNum1:
		first_screen(channel)
		
	elif currentScreen1 == emptyMachineNum:
		mylcd.lcd_clear()
		currentScreen1 = 0
		
	elif currentScreen1 == stopScriptNum:
		mylcd.lcd_clear()
		currentScreen1 =0
	elif currentScreen1 == powerOffNum2:
		currentScreen1 = powerOffNum1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Power Off?")
		
	elif currentScreen1 == editBreakNum and blinkingTextChar ==0:
		pickle.dump(feedTimes, open("feedTimes.dat","wb"))
		first_screen(channel)
		
	elif currentScreen1 == editBreakNum and blinkingTextChar ==1:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Hour", 2)
		blinkingTextChar = 0
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar ==0:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Minute", 2)
		blinkingTextChar = 1
		currentScreen1 = editBreakNum
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar ==1:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Hour", 2)
		blinkingTextChar = 0
		
def callBack_enterBut(channel):
	#time.sleep(.01)
	global currentScreen1
	global blinkingTextChar ##Brings in the global variables that will be needed
	global blinkingText
	global Running
	print "enter Button hit"
	if currentScreen1 == 0:
		first_screen(channel)

	elif currentScreen1 == editFeedTimeNum:
		print "entered feed times screen - Breakfast"
		currentScreen1 = editBreakNum
		blinkingTextChar = 0
		print currentScreen1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Hour", 2)
		#time.sleep(0.5)
	elif currentScreen1 == viewFeedTimeNum:
		currentScreen1 = seeingFeedTimeNum
		mylcd.lcd_clear()
		mylcd.lcd_display_string("Breakfast: " + str(feedTimes[0][0]) + ":" + str(feedTimes[0][1]),1)
		mylcd.lcd_display_string("Dinner: " + str(feedTimes[1][0]) + ":" + str(feedTimes[1][1]),2)
		
	elif currentScreen1 == powerOffNum1:
		currentScreen1 = powerOffNum2
		mylcd.lcd_clear()
		pickle.dump(feedTimes, open("feedTimes.dat","wb"))
		mylcd.lcd_display_string("Sure?")
		
	elif currentScreen1 == powerOffNum2:
		mylcd.lcd_clear()
		mylcd.backlight(0)
		call("sudo nohup shutdown -h now", shell=True)
	
	elif currentScreen1 == stopScriptNum:
		Running = False
		mylcd.lcd_clear()
		currentScreen1 = 0
		
	elif currentScreen1 == emptyMachineNum:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("Emptying...")
		EmptyMachine.feed()
		mylcd.lcd_clear()
		currentScreen1 = 0
		
		
	elif currentScreen1 == editBreakNum and blinkingTextChar == 0:
		blinkingTextChar = 1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Minute", 2)
		#time.sleep(0.5)
		
	elif currentScreen1 == editBreakNum and blinkingTextChar == 1:
		print "entered feed times screen - Dinner"
		currentScreen1 = editDinnerNum
		blinkingTextChar = 0
		print currentScreen1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Hour", 2)
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar == 0:
		blinkingTextChar = 1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Minute", 2)
		
	elif currentScreen1 ==editDinnerNum and blinkingTextChar == 1:
		mylcd.lcd_clear()
		pickle.dump(feedTimes, open("feedTimes.dat","wb"))
		currentScreen1 = 0
	
		
def callBack_leftBut(channel):
	time.sleep(.01)
	global currentScreen1
	global blinkingTextChar
	global blinkingText
	global feedTimes
	blinkingText = False
	print "left Button hit"
	if currentScreen1 == 0:
		first_screen(channel)
	
	elif currentScreen1 == powerOffNum1:
		second_screen()
	elif currentScreen1 == editFeedTimeNum:
		first_screen(channel)
	elif currentScreen1 == viewFeedTimeNum:
		fith_screen()
		
	elif currentScreen1 == stopScriptNum:
		third_screen()
	
	elif currentScreen1 == emptyMachineNum:
		fourth_screen()
		
	elif currentScreen1 == editBreakNum and blinkingTextChar == 0:
		feedTimes[0][0] -=1
		if feedTimes[0][0] <=0:
			feedTimes[0][0] = 23
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Hour", 2)
		#time.sleep(0.5)
		
	elif currentScreen1 == editBreakNum and blinkingTextChar == 1:
		feedTimes[0][1] -=changeTimeMin
		if feedTimes[0][1] <=0:
			feedTimes[0][1] = 59
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Minute", 2)
		#time.sleep(0.5)
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar == 0:
		feedTimes[1][0] -=1
		if feedTimes[1][0] <=0:
			feedTimes[1][0] = 23
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Hour", 2)
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar == 1:
		feedTimes[1][1] -=changeTimeMin
		if feedTimes[1][1] <=0:
			feedTimes[1][1] = 59
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Minute", 2)
		
		
def callBack_rightBut(channel):
	time.sleep(.01)
	global currentScreen1
	global blinkingTextChar
	global blinkingText
	global feedTimes
	blinkingText = False
	print "right Button hit"
	if currentScreen1 == 0:
		first_screen(channel)
	
	elif currentScreen1 == viewFeedTimeNum:
		second_screen()
	elif currentScreen1 == editFeedTimeNum:
		third_screen()
	elif currentScreen1 == powerOffNum1:
		print "exitingpower"
		fourth_screen()
	elif currentScreen1 == stopScriptNum:
		fith_screen()
		
	elif currentScreen1 == emptyMachineNum:
		first_screen(channel)
	
	elif currentScreen1 == editBreakNum and blinkingTextChar == 0:
		feedTimes[0][0] +=1
		if feedTimes[0][0] >=24:
			feedTimes[0][0] = 1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Hour", 2)
		#time.sleep(0.5)
		
	elif currentScreen1 == editBreakNum and blinkingTextChar == 1:
		feedTimes[0][1] +=changeTimeMin
		if feedTimes[0][1] >=60:
			feedTimes[0][1] = 1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("1.Breakfast")
		if feedTimes[0][1] <10: mylcd.lcd_display_string(str(feedTimes[0][0])+":0" +str(feedTimes[0][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[0][0])+":" +str(feedTimes[0][1]) + " Minute", 2)
		#time.sleep(0.5)
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar == 0:
		feedTimes[1][0] +=1
		if feedTimes[1][0] >=24:
			feedTimes[1][0] = 1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Hour", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Hour", 2)
		
	elif currentScreen1 == editDinnerNum and blinkingTextChar == 1:
		feedTimes[1][1] +=changeTimeMin
		if feedTimes[1][1] >=60:
			feedTimes[1][1] = 1
		mylcd.lcd_clear()
		mylcd.lcd_display_string("2.Dinner")
		if feedTimes[1][1] <10: mylcd.lcd_display_string(str(feedTimes[1][0])+":0" +str(feedTimes[1][1]) + " Minute", 2)
		else: mylcd.lcd_display_string(str(feedTimes[1][0])+":" +str(feedTimes[1][1]) + " Minute", 2)

def callback_end(channel):
	global Running
	print "end button hit"
	mylcd.lcd_clear()
	Running = False
	
def first_screen(channel): ##Used to standardize the first screan aka coming from blank to the first
	print "opened first screen"
	mylcd.lcd_clear()
	mylcd.lcd_display_string("1.View feed",1)
	mylcd.lcd_display_string("times",2)
	setScreen(viewFeedTimeNum)
	
def second_screen():
	mylcd.lcd_clear()
	mylcd.lcd_display_string("2.Edit feed",1)
	mylcd.lcd_display_string("times",2)
	setScreen(editFeedTimeNum)
def third_screen():
	setScreen(powerOffNum1)
	mylcd.lcd_clear()
	mylcd.lcd_display_string("3.Power Off?")
	
def fourth_screen():
	mylcd.lcd_clear()
	mylcd.lcd_display_string("4.End Script",1)
	setScreen(stopScriptNum)
	
def fith_screen():
	mylcd.lcd_clear()
	mylcd.lcd_display_string("5.Empty Machine",1)
	setScreen(emptyMachineNum)
def blinkingTime():
	global currentScreen1
	global blinkingTextChar
	global blinkingText
	global feedTimes
	
	
def startButtons():
	GPIO.add_event_detect(12, GPIO.FALLING, callback=callBack_backBut , bouncetime=DEBOUCE_TIME)##These wait for the buttons to be pressed and calls the appropreat callback when they are
	GPIO.add_event_detect(16, GPIO.FALLING, callback=callBack_enterBut, bouncetime=DEBOUCE_TIME)
	GPIO.add_event_detect(20, GPIO.FALLING, callback=callBack_leftBut , bouncetime=DEBOUCE_TIME)
	GPIO.add_event_detect(21, GPIO.FALLING, callback=callBack_rightBut , bouncetime=DEBOUCE_TIME)	
	
def sendEmail():
	emailVar = smtplib.SMTP('smtp.gmail.com', 587)
	# start TLS for security 
	emailVar.starttls()
	# Authentication 
	emailVar.login("BaldPetFeeder@gmail.com", "1mYsteriousRedundantSidwalk") 
	# message to be sent 
	message = """\
	Subject: Feeding Stuart

	Stuart was just fed at %s""" %time.strftime("%H:%M")
	# sending the mail 
	emailVar.sendmail("BaldPetFeeder@gmail.com", "jasonbaldwin301@gmail.com", message)
	# terminating the session 
	emailVar.quit()	

try:
    feedTimes = pickle.load(open("feedTimes.dat", "rb"))
    print "Found the feed file"
except IOError:
	print "can't Find File"
	feedTimes = [[7,45],[16,45]]
	pickle.dump(feedTimes, open("feedTimes.dat","wb"))
	print "Saved New Data"

	
	
	
startButtons()

try:  
	
    while Running:
		if currentScreen1 == 0:
			currentDT = datetime.datetime.now()
			if currentDT.hour == feedTimes[0][0] and currentDT.minute == feedTimes[0][1] and isFeeding:
				CatFeeder.feed()
				isFeeding = False
				sendEmail()
				print "Isfeeding False"
				#startButtons()
			
			elif currentDT.hour == feedTimes[1][0] and currentDT.minute == feedTimes[1][1] and isFeeding:
				CatFeeder.feed()
				isFeeding = False
				sendEmail()
				print "Isfeeding False"
				#startButtons()
			elif isFeeding == False:
				feedCountDown -=1
				if feedCountDown <= 0:
					isFeeding = True
					feedCountDown = 75
					print "Isfeeding TRUE"
					
		time.sleep(0.8)
		runnum+=1
		if runnum%5 ==0:
			if currentScreen1 == 0:
				if clockPlace == 1: clockPlace =2
				else: clockPlace =1
				mylcd.lcd_clear()
				mylcd.lcd_display_string("Time: %s" %time.strftime("%H:%M"), clockPlace,random.randint(0,5))
			
			print "*"
			
except KeyboardInterrupt: 
	mylcd.lcd_clear() 
	GPIO.cleanup()       # clean up GPIO on CTRL+C exit
	
mylcd.lcd_clear()
GPIO.cleanup()           # clean up GPIO on normal exit  

