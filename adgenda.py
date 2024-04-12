#!/usr/bin/env python3
#Required module for the Linux-based calendar utility for blind users
#Copyright Blazie Technologies LLC, All rights reserved
#by Stephen Blazie

import os, re, json, configparser
from BTSpeak import dialogs, host, script, braille
from datetime import datetime

dateFormats = [
    "%B %d, %Y",    #January 01, 2024
    "%B %d %Y",    # January 01 2024
    "%b %-d, %Y", # Jan 1, 2024
    "%b %-d %Y",    # Jan 1 2024
    "%B %d",    # January 01
    "%m-%d",    # 01-01
    "%b %d",    # Jan 01
    "%b %-d",    # Jan 1
    "%m/%d",    # 1/01 or 1/1
    "%m/%d/%y",    # 1/1/24
    "%m-%d",    # 1-01 or 1-1
    "%m-%d-%y",    #01-01-2024
]

invalidDateMessage = "The date is invalid. " \
                     "Enter date in one of the following formats: " \
                     "1/1, 01/01, 1/1/24, 01-01, 01-01-24, Jan 01, " \
                     "Jan 1, January 01, January 01, 2024, or January 1, 2024"

class DateError(Exception):
    pass

class calendar:
    def __init__(self, invalidDateMessage = invalidDateMessage, calendarFile=os.path.join(host.stateDirectory, "calendar")):
        self.calendarFile=calendarFile
        self.load()
        self.invalidDateMessage = invalidDateMessage

        settings = Settings().getSettings()
        self.contractedBraille = settings.getboolean('braille input')

        if settings.getboolean('default date') == True:
            self.defaultDatePrompt = todaysDate()
        else:
            self.defaultDatePrompt = None

    def load(self):
        try:
            with open(self.calendarFile, 'r') as file:
                self.calendar = json.load(file)
        except FileNotFoundError:
            self.calendar={}

    def save(self):
        with open(self.calendarFile, 'w') as file:
            json.dump(self.calendar, file, indent=4)

    def saveAsText(self, calendarTextPath):
        with open(calendarTextPath, 'w') as calendarTextFile:
            for date, entries in self.calendar.items():
                for entry in entries:
                    time = entry['time']
                    event = entry['event']
                    calendarTextFile.write(f"{date}, {time}, {event}\n")

    def parseUserEntry(self):
        initialText = None

        if self.defaultDatePrompt and self.contractedBraille:
            initialText = translateInitial(self.defaultDatePrompt, self.contractedBraille)
        elif self.defaultDatePrompt:
            initialText = self.defaultDatePrompt

        crudeDate = dialogs.requestInput("Date?", initialText = initialText)

        if crudeDate is None:
            exit(0)

        else:
            if self.contractedBraille:
                crudeDate = translateBraille(crudeDate, backTranslate=True)

            crudeDate, date = parseDate(crudeDate)

            if date is None:
                raise DateError("Date is None")
                return

            crudeTime = dialogs.requestInput("Time?")
            event = dialogs.requestInput("Event?")

            if self.contractedBraille:
                crudeTime = translateBraille(crudeTime, backTranslate=True)
                event = translateBraille(event, backTranslate=True)

            time = parseTime(crudeTime)
            reminder = parseReminder(event)
            print(date, reminder, time, event)
            return date, reminder, time, event

    def appendEntry(self, entryString = None, fullEntry = False):
        try:
            if fullEntry:
                date, reminder, time, event = parseFullEntry(entryString)
            else:
                date, reminder, time, event = self.parseUserEntry()

            if time is None:
                time = 'All day'

            newEvent = {'event':event, 'time':time, 'reminder':reminder}

            if date is None:
                raise DateError("Date is None")

        except DateError:
            dialogs.showMessage(self.invalidDateMessage,
                                    okayLabel = "Back"
                               )
            return

        if date in self.calendar:
            if newEvent in self.calendar[date]:
                dialogs.showMessage("Not added to calendar: That event already exists for the given date.",
                                    okayLabel = "Back"
                                   )
                return

            for existing_event in self.calendar[date]:
                if existing_event['time'] == time and time is not None:
                    confirmationValue = dialogs.requestConfirmation(f"Another event already exists at {time} on {date}. Are you sure you would like to add the event?")
                    if not confirmationValue:
                        return

        self.calendar.setdefault(date, []).append(newEvent)
        self.save()
        dialogs.showMessage(f"New event added to your calendar on {date}",
                            okayLabel = "Back"
                           )
        return  date

    def removeEntry(self, date, time, eventString):
        if date in self.calendar:
            events = self.calendar[date]

            for event in events:
                if event['event'] == eventString:
                    request = dialogs.requestConfirmation(
                                                          f"Are you sure you want to remove {date} {eventString} from your calendar?", 
                                                          yesLabel = True, 
                                                          noLabel = True
                                                         )

                    if request == True:
                        self.calendar[date].remove(event)
                        if len(self.calendar[date])==0:
                            del self.calendar[date]
                        self.save()
                        dialogs.showMessage(f"Removed {eventString} on {date} from your calendar",
                                            okayLabel = "Okay"
                                           )

                    elif request == False:
                        return

    def showEvents(self, dateList):
        eventsDict={}
        for date in dateList:
            if date in self.calendar:
                eventsDict[date]=self.calendar[date]
        return eventsDict

    def editDate(self, date, eventString, time, newDate):

        if newDate == date:
            return

        crudeDate, newDate = parseDate(newDate)
        if newDate is None:
            dialogs.showMessage(self.invalidDateMessage,
                                okayLabel = "Back"
                               )
            return


        if date in self.calendar:
            events = self.calendar[date]

            for event in events:
                if event['event'] == eventString:
                    events.remove(event)
                    if len(self.calendar[date])==0:
                        del self.calendar[date]

                    if newDate in self.calendar:
                        self.calendar[newDate].append(event)
                    else:
                        self.calendar[newDate] = [event]
                    dialogs.showMessage(f"Event date changed to {newDate}",
                                        okayLabel = "okay"
                                       )
                    self.save()
        return

    def editTime(self, date, eventString, time, newTime):
        newTime=parseTime(newTime)
        if newTime == time:
            return
        if newTime == None:
            newTime = 'All day'

        if date in self.calendar:
            events = self.calendar[date]
            for event in events:
                if event['event'] == eventString and event['time'] == time:
                    event['time'] = newTime
                    dialogs.showMessage(f"Event time changed to {newTime}",
                                        okayLabel = "okay"
                                       )
            self.save()
            return

    def editEvent(self, date, eventString, time, newEvent):
        if newEvent == eventString or newEvent == None:
            return

        if date in self.calendar:
            events = self.calendar[date]
            for event in events:
                if event['event'] == eventString and event['time'] == time:
                    event['event'] = newEvent
                    dialogs.showMessage(f"Event changed to {newEvent}",
                                        okayLabel = "okay"
                                       )
            self.save()
            return

    def searchDate(self, date):
        crudeDate, date = parseDate(date)
        if date == None:
            dialogs.showMessage(self.invalidDateMessage,
                                okayLabel = "Back"
                               )
            return None

        searchResultCalendar = {}
        for key, value in self.calendar.items():
            if date == key:
                searchResultCalendar[key] = value
        return searchResultCalendar

    def searchEvent(self, event):
        searchResultCalendar = {}
        for key, value in self.calendar.items():
            matchingEntries = []
            for entry in value:
                if event.lower() in entry['event'].lower():
                    matchingEntries.append(entry)
            if matchingEntries:
                searchResultCalendar[key] = matchingEntries
        return searchResultCalendar

class Settings():

    def __init__(self):
        config = configparser.ConfigParser()
        self.config = config
        self.configFile = os.path.join(host.stateDirectory, "calendar.config")
        self.getSettings()

    def getSettings(self):
        self.config.read(self.configFile)
        return self.config['Settings']

    def writeSettings(self, settingName, value):
        self.config.set('Settings', settingName, str(value))
        with open(self.configFile, 'w') as file:
            self.config.write(file)
        return

    def listSettings(self):
        settings = []
        for setting in self.getSettings():
            settings.append(setting)
        return settings

    def promptSettings(self, settingName):
        defaultChoice = None
        settings = ['Off', 'On']

        if self.getSettings().getboolean(settingName):
            choiceIndex = settings.index('On')
        else:
            choiceIndex = settings.index('Off')
        currentSetting = settings[choiceIndex]
        choiceIndex+=1

        while True:
            choice=dialogs.requestChoice(settings,
                                         default=choiceIndex,
                                         allowEmptyChoice=True,
                                         okayLabel="Select",
                                         cancelLabel="Back",
                                         message= f"{settingName} is currently {currentSetting}"
                                        )
            if choice is None:
                return

            if choice.label == 'On':
                value = 'True'
            elif choice.label == 'Off':
                value = 'False'
            self.writeSettings(settingName, value)
            choiceIndex = choice.key
            currentSetting = choice.label
        return

    def saveCalendar(self):
        now = datetime.now().strftime("%y%m%d")
        calendarTextPath = os.path.join(os.getenv("HOME"), f"{now}-{script.scriptName}.txt")
        try:
            calendar().saveAsText(calendarTextPath)
            dialogs.showMessage(f"Calendar saved as {now}-{script.scriptName}.txt to your home directory",
                                okayLabel = "okay"
                               )
        except: pass
        return


def translateInitial(text, contractedBraille):
    if contractedBraille:
        return translateBraille(text, backTranslate=False)
    else:
        return text

def translateBraille(text, backTranslate=False):
    translation = braille.translateText (text, backTranslate=backTranslate, table=None)
    return translation

def formatDate(date, dateFormats):
    for fmt in dateFormats:
        try:
            dtDate = datetime.strptime(date, fmt)
            if "%Y" not in fmt and "%y" not in fmt:
                dtDate = dtDate.replace(year=datetime.now().year)
            formattedDate = dtDate.strftime('%A, %B %d, %Y')
            return formattedDate
        except ValueError:
            pass
    return None

def parseDate(entry):
    datePattern = r"(\w{3,9} \d{1,2}(?:,? \d{4})?|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{1,2}/\d{1,2}(?:/\d{2,4})?|\w{3,9} \d{1,2})"
    match=re.search(datePattern, entry, re.IGNORECASE)
    if match:
        crudeDate=match.group(0)
        return crudeDate, formatDate(crudeDate.upper(), dateFormats)
    else:
        return "", None

def parseTime(entry):
    timePattern=r'\b\d{1,2}(:\d{2})?\s*(?:am|pm)\b'
    match=re.search(timePattern, entry, re.IGNORECASE)
    if match:
        return match.group(0)
    else:
        return None


def parseReminder(entry):
    if entry.endswith("*"):
        return True
    else:
        return False

def todaysDate():
    return datetime.now().strftime("%A, %B %d, %Y")

def parseFullEntry(entryString):
    if entryString.startswith(".cal"):
        entryString = entryString[len(".cal"):].lstrip()
    crudeDate, date = parseDate(entryString)

    if date is None:
        return

    reminder = parseReminder(entryString)
    time = parseTime(entryString)
    event = entryString.replace(crudeDate, "")
    if time is not None:
        event = event.replace(time, "")

    event = re.sub(r'^[^a-zA-Z0-9]+', '', event)
    return date, reminder, time, event

if __name__=="__main__":
    entryString = "March 27, 8pm Appointment"
    calendar().appendEntry(entryString)
