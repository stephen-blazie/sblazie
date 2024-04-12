#!/usr/bin/env python3
#Copyright Blazie Technologies LLC., All rights reserved
#Stephen Blazie

import calendar, configparser, os, louis, time
from BTSpeak import host, dialogs, script, adgenda, braille
from datetime import datetime, timedelta
from calendar import monthrange

class Browse():

    def __init__(self):
        settings = adgenda.Settings()
        self.contractedBraille = settings.getSettings().getboolean('braille input')

        if settings.getSettings().getboolean('default date') == True:
            self.defaultDatePrompt = adgenda.todaysDate()
        else:
            self.defaultDatePrompt = None

    def promptChoice(self, listChoices, message, defaultChoice):
        while True:

            choice=dialogs.requestChoice(listChoices,
                                         default=defaultChoice,
                                         allowEmptyChoice=True,
                                         okayLabel="Select",
                                         cancelLabel="Back",
                                         message=message
                                        )
            if choice is None:
                return None, None
            else:
                choiceName, defaultChoice = choice
                choiceLabel = choice.label
                return choiceLabel, defaultChoice

    def editEvents(self, event, date, time):
        defaultChoice = None

        editMenu=[
               'Edit event',
               'Edit time',
               'Edit date',
               'Delete event'
               ]

        calendar = adgenda.calendar()
        editMenuMessage = f"Select an operation to perform on calendar entry {date} {time} {event}"
        editAction, defaultChoice = self.promptChoice(editMenu, editMenuMessage, defaultChoice) 

        if editAction is None:
            return

        elif editAction == 'Edit event':
            newEvent = dialogs.requestInput("Edit the event:",
                                            initialText = adgenda.translateInitial(event, self.contractedBraille)
                                           )
            if newEvent is None: return
            if self.contractedBraille:
                newEvent = adgenda.translateBraille(newEvent, backTranslate=True)

            calendar.editEvent(date, event, time, newEvent)

        elif editAction == 'Edit time':
            newTime = dialogs.requestInput(f"Edit the time for {event}:",
                                           initialText = adgenda.translateInitial(time, self.contractedBraille)
                                          )
            if newTime is None: return
            if self.contractedBraille:
                newTime = adgenda.translateBraille(newTime, backTranslate=True)

            calendar.editTime(date, event, time, newTime)

        elif editAction == 'Edit date':
            date = convertDateFormat(date)
            newDate = dialogs.requestInput("Edit the date:",
                                           initialText = adgenda.translateInitial(date, self.contractedBraille)
                                          )
            if newDate is None: return
            if self.contractedBraille:
                newDate = adgenda.translateBraille(newDate, backTranslate=True)

            calendar.editDate(convertDateFormat(date), event, time, newDate)

        elif editAction == 'Delete event':
            calendar.removeEntry(date, time, event)
        return

    def getEventData(self, eventsDict, eventString):
        date = eventsDict[eventString]['date']
        time = eventsDict[eventString]['time']
        event = eventsDict[eventString]['event']
        reminder = eventsDict[eventString]['reminder']
        return date, time, event, reminder


    def todaysEvents(self):
        defaultChoice = 1

        while True:
            calendar=adgenda.calendar()
            dateList = [adgenda.todaysDate()]
            todaysCalendar=calendar.showEvents(dateList)

            if todaysCalendar:
                todayDict = self.getEntries(todaysCalendar, dailyEntries = True)
                eventStrings = list(todayDict.keys())

                eventsMessage=f"Calendar entries for {list(todaysCalendar.keys())[0]}"
                eventStringChoice, defaultChoice = self.promptChoice(eventStrings, eventsMessage, defaultChoice)

                if eventStringChoice is None:
                    return

                date, time, event, reminder = self.getEventData(todayDict, eventStringChoice)
                self.editEvents(event, date, time) 

            else:
                dialogs.showMessage(f"Nothing in your calendar today, {adgenda.todaysDate()}",
                                   okayLabel="Back"
                                   )
                return

    def generateWeeklyList(self, dateString, next=True):

        date = datetime.strptime(dateString, '%A, %B %d, %Y')
        dateRange = []
        if next:
            for i in range(7):
                dateRange.append((date + timedelta(days=i)).strftime('%A, %B %d, %Y'))

        else:
            for i in range(6, -1, -1):
                dateRange.append((date - timedelta(days=i)).strftime('%A, %B %d, %Y'))
        return dateRange

    def generateDateRange(self, dateString, monthly=False, next=True):
        date = datetime.strptime(dateString, '%A, %B %d, %Y')
        dateRange = []

        if monthly:
            _, lastDay = monthrange(date.year, date.month)
            startDate = datetime(date.year, date.month, 1)
            endDate = datetime(date.year, date.month, lastDay)

            while startDate <= endDate:
                dateRange.append(startDate.strftime('%A, %B %d, %Y'))
                startDate += timedelta(days=1)
        else:
            dateRange = self.generateWeeklyList(dateString, next)

        return dateRange

    def getEntries(self, weekCalendar, dailyEntries = False):
        entriesDict = {}

        for date, eventsList in weekCalendar.items():
            for event in eventsList:

                if dailyEntries:
                    eventString = f"{event['time']} {event['event']}" if event['time'] else f"{event['event']}"

                else:
                    eventString = f"{date} {event['time']} {event['event']}" if event['time'] else f"{date} {event['event']}"
                entriesDict[eventString] = {'date': date, 'time': event['time'], 'event': event['event'], 'reminder': event['reminder']}

        return entriesDict

    def browseDateRange(self, monthly=False):
        startDate = adgenda.todaysDate()
        dateRange = self.generateDateRange(startDate, monthly)
        defaultChoice = 2
        eventStringChoice = None

        while True:
            startDateDT = convertToDatetime(startDate, "%A, %B %d, %Y")
            weekCalendar = adgenda.calendar().showEvents(dateRange)

            if weekCalendar:
                eventStrings, weekDict = self.getEventStrings(weekCalendar)
            else:
                eventStrings = ['No events']

            eventStrings.insert(0, 'previous')
            eventStrings.append('next')

            eventStringChoice, defaultChoice = self.promptChoice(eventStrings, 
                                                                 self.getMessage(startDateDT, dateRange, monthly), 
                                                                 defaultChoice
                                                                )

            if eventStringChoice is None:
                return

            if eventStringChoice == 'previous':
                startDate, dateRange = self.handlePrevious(startDate, dateRange, monthly)
                defaultChoice = 2
            elif eventStringChoice == 'next':
                startDate, dateRange = self.handleNext(startDate, dateRange, monthly)
                defaultChoice = 2
            elif eventStringChoice != 'No events':
                date, time, event, reminder = self.getEventData(weekDict, eventStringChoice)
                self.editEvents(event, date, time)

    def getEventStrings(self, weekCalendar):
        weekDict = self.getEntries(weekCalendar)
        return list(weekDict.keys()), weekDict

    def getMessage(self, startDate, dateRange, monthly):
        if monthly:
            return f"Entries for month of {calendar.month_name[startDate.month]} {startDate.year}"
        else:
            return f"Entries for week of {dateRange[0]} to {dateRange[-1]}"

    def handlePrevious(self, startDate, dateRange, monthly):
        startDate = convertToDatetime(dateRange[0], "%A, %B %d, %Y") - timedelta(days=1)
        startDate = startDate.strftime("%A, %B %d, %Y")
        dateRange = self.generateDateRange(startDate, monthly, next=False)
        return startDate, dateRange

    def handleNext(self, startDate, dateRange, monthly):
        startDate = convertToDatetime(dateRange[-1], "%A, %B %d, %Y") + timedelta(days=1)
        startDate = startDate.strftime("%A, %B %d, %Y")
        dateRange = self.generateDateRange(startDate, monthly, next=True)
        return startDate, dateRange 


    def searchEvent(self):
        eventQuery = dialogs.requestInput("Event to search:")
        defaultChoice = None

        if len(eventQuery)==0:
            return

        if self.contractedBraille:
            eventQuery = adgenda.translateBraille(eventQuery, backTranslate=True)

        while True:
            searchResultsCalendar = adgenda.calendar().searchEvent(eventQuery)

            if searchResultsCalendar:
                host.say(f"Showing results for {eventQuery}")
                searchResultsDict = self.getEntries(searchResultsCalendar, dailyEntries = False)
                eventStrings = list(searchResultsDict.keys())

                eventsMessage=f"Calendar entries containing {eventQuery}"
                eventStringChoice, defaultChoice = self.promptChoice(eventStrings, eventsMessage, defaultChoice)

                if eventStringChoice is None:
                    return

                date, time, event, reminder = self.getEventData(searchResultsDict, eventStringChoice)
                self.editEvents(event, date, time) 

            else:
                dialogs.showMessage(f"No events in your calendar match {eventQuery}",
                                   okayLabel="Back"
                                   )
                return

    def searchDate(self):
        dateQuery = dialogs.requestInput("Date to search:")
        defaultChoice = None

        if dateQuery is None or len(dateQuery) == 0:
            return

        if self.contractedBraille:
            dateQuery = adgenda.translateBraille(dateQuery, backTranslate=True)

        while True:
            searchResultsCalendar = adgenda.calendar().searchDate(dateQuery)

            if searchResultsCalendar is None:
                return

            elif not searchResultsCalendar:
                dialogs.showMessage(f"Nothing in your calendar for {dateQuery}",
                                    okayLabel="Back"
                                   )
                return

            else:
                host.say(f"Showing results for {dateQuery}")
                searchResultsDict = self.getEntries(searchResultsCalendar, dailyEntries = True)
                eventStrings = list(searchResultsDict.keys())

                eventsMessage=f"Calendar entries for {list(searchResultsCalendar.keys())[0]}"
                eventStringChoice, defaultChoice = self.promptChoice(eventStrings, eventsMessage, defaultChoice)

                if eventStringChoice is None:
                    return

                date, time, event, reminder = self.getEventData(searchResultsDict, eventStringChoice)
                self.editEvents(event, date, time)

    def addEntry(self):
        return adgenda.calendar().appendEntry()

def convertToDatetime(dateString, dateFormat):
    dateStringDT = datetime.strptime(dateString, dateFormat)
    return dateStringDT

def convertDateFormat(dateString):
    try:
        date = datetime.strptime(dateString, '%A, %B %d, %Y')
        date = datetime.strftime(date, '%B %d, %Y')

    except ValueError:
        try:
            date = datetime.strptime(dateString, '%B %d, %Y')
            date = datetime.strftime(date, '%A, %B %d, %Y')

        except ValueError:
            date = None
    return date


script.addOption(
    "a", argument="action", label="action",
    default="action",
    help="Select a caledar option. Options are: today (shows a list of today's events, ordered by time of day), weeklyEvents (shows weekly events in the calendar ordered by date), searchEvent (executes a search prompt for specific event(s) in the calendar), searchDate (executes a search prompt for a specific date and displays the list of events for the chosen date)"
)

option = script.parseArguments().action

functions={
    "today": lambda: Browse.todaysEvents(),
    "week": lambda: Browse.browseDateRange(),
    "month": lambda: Browse.browseDateRange(monthly=True),
    "searchEvent": lambda: Browse.searchEvent(),
    "searchDate": lambda: Browse.searchDate(),
    "add": lambda: Browse.addEntry(),
    "brailleSettings": lambda: Settings.promptSettings(settingName = 'braille input'),
    "defaultDateSettings": lambda: Settings.promptSettings(settingName = 'default date'),
    "saveCalendar": lambda: Settings.saveCalendar()
}


if option in functions:
    Browse = Browse()
    Settings = adgenda.Settings()
    perform=functions[option]
    perform()


