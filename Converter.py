try:
    from PIL import Image
    from PIL import ImageDraw
except ImportError:
    import Image
import pytesseract
from pdf2image import convert_from_path
from ics import Calendar, Event
import re
import datetime
import os

# turn .pdf. to .png
pages = convert_from_path('V.pdf', 500)
for page in pages:
    page.save('out.png', 'png')

# turn img greyscale
img = Image.open('out.png').convert('L')
img.save('greyscale.png')
os.remove('out.png')


i = 0
gap1 = 550
gap2 = 540

#cut Vorlesungsplan into columns
while i < 6:
    im = Image.open("greyscale.png")
    width, height = im.size
    cropped = im.crop((340+gap1*i, 405, width-3200+gap2*i, height-350))
    cropped.save('section'+ str(i) +'.png')
    i += 1
os.remove('greyscale.png')

def ocr_core(filename):
     """
     This function will handle the core OCR processing of images.
     """
     pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
     text = pytesseract.image_to_string(Image.open(filename), lang='deu')
     return text


# Gobale Variablen
dates = []
startIndex = []
endIndex = []
missingdates = []
startTimeIndex = []
endTimeIndex = []
startTime = []
endTime = []

def find_missing(dates):
    groupeddates = []
    g = 0
    groupeddates.append([])
    try: 
        for i in range(len(dates)):
            x = dates[i] + datetime.timedelta(days=1)
            y = dates[i] + datetime.timedelta(days=2)
            z = dates[i] + datetime.timedelta(days=3)
            if dates[i+1] == x:
                groupeddates[g].append(dates[i])
            elif dates[i+1] == y:
                groupeddates[g].append(dates[i])
                missingdates.append(x)
            elif dates[i+1] == z:
                groupeddates[g].append(dates[i])
                missingdates.append(x)
                missingdates.append(y)
            else:
                groupeddates[g].append(dates[i])
                groupeddates.append([])
                g += 1
    except IndexError:
        groupeddates[g].append(dates[-1])
    #Multidimensional representation of grouped dates
    #print(dates)

i = 0
while i <6:
    t = ocr_core('section'+ str(i) +'.png')
    #Print text in console
    #print(t)
    with open('my.txt', 'a+') as f:
         f.writelines(t)
    os.remove('section'+ str(i) +'.png')
    i += 1

def find_date(s1): 
    text = s1
    pattern = re.compile('\d\d\.\d\d\.\d{4}')
    for match in re.finditer(pattern, text):
        # Start index of match (integer)
        sStart = match.start()
        # Final index of match (integer)
        sEnd = match.end()
        # Complete match (string)
        sGroup = match.group()
        # Print match with indexes
        #print('Match "{}" found at: [{},{}]'.format(sGroup, sStart,sEnd))
        dt = datetime.datetime.strptime(sGroup, '%d.%m.%Y')
        d = dt.date()
        dates.append(d)
        startIndex.append(sStart)
        endIndex.append(sEnd)
    print('Find Dates with Indexes SUCCESS')

def find_time(s2): 
    text = s2
    pattern = re.compile('\d?\d\.\d\d\s?-\s?\d?\d\.\d\d')
    for match in re.finditer(pattern, text):
        sStart = match.start()
        sEnd = match.end()
        sGroup = match.group()
        # Print match with indexes
        # print('Match "{}" found at: [{},{}]'.format(sGroup, sStart, sEnd))
        startTimeIndex.append(sStart)
        endTimeIndex.append(sEnd)
        check = re.compile('\d')
        if check.search(sGroup[4]):
            bT = sGroup[:5]
        else:
            bT = sGroup[:4]
        if check.search(sGroup[-5]):
            eT = sGroup[-5:]
        else:
            eT = sGroup[-4:]
        # time to utc
        bT2 = datetime.datetime.strptime(bT, '%H.%M') - datetime.timedelta(hours= 2)
        eT2 = datetime.datetime.strptime(eT, '%H.%M') - datetime.timedelta(hours= 2)
        bT2 = datetime.datetime.time(bT2)
        eT2 = datetime.datetime.time(eT2) 
        startTime.append(bT2)
        endTime.append(eT2)

with open('my.txt', 'r') as f:
        s1 = f.read()
find_date(s1)
find_missing(dates)
print(missingdates)
print('Find missing dates SUCCESS')
print('Creating Calender ...')
cal = Calendar()



def createCal(name, date, begin, end):
    name1 = name.strip()
    # cancelled/ striked out meetings are seen as u
    cancelled = re.compile('^u')
    if re.match(cancelled, name1):
        name1 = ''
    #correction of Weekdays 
    name1[:name1.find('Montag,')]
    name1[:name1.find('Dienstag,')]
    name1[:name1.find('Mittwoch,')]
    name1[:name1.find('Donnerstag,')]
    name1[:name1.find('Freitag,')]
    name1[:name1.find('Samstag,')]
    name1[:name1.find('Sonntag,')]
    # if re.match(monday, name1):
    #     name1 = name1[:-7]
    #     name1 = name1.strip()
    # tuesday = re.compile('Dienstag,')
    # wednesday = re.compile('Mittwoch,')
    # if re.match(tuesday, name1) or re.match(wednesday, name1):
    #     name1 = name1[:-9]
    #     name1 = name1.strip()
    # thursday = re.compile('Donnerstag,')
    # if re.match(thursday, name1):
    #     name1 = name1[:-11]
    #     name1 = name1.strip()
    # friday = re.compile('Freitag,')
    # if re.match(thursday, name1):
    #     name1 = name1[:-8]
    #     name1 = name1.strip()
    # saturday = re.compile('Samstag,')
    # sunday = re.compile('Sonntag,')
    # if re.match(saturday, name1) or re.match(sunday, name1):
    #     name1 = name1[:-8]
    #     name1 = name1.strip()
    #print(name1)
    # correction of weeks
    weeks = re.compile('$(Woche\s\d\d\s?)')
    if re.match(weeks, name1):
        name1 = name1[:-8]
        name1 = name1.strip()
    print(name1)
    if name1 != '':
        e = Event()
        e.name = name1
        e.begin = str(date.isoformat()+ ' '+ str(begin))
        e.end = str(date.isoformat()+ ' '+ str(end))
        cal.events.add(e)
        cal.events

for i in range(len(dates)):
#i = 0
    try:
        #find times in range for date
        s2 = s1[endIndex[i]:startIndex[i+1]]
        # wipe Time arrays of previous date 
        startTime = []
        endTime = []
        startTimeIndex = []
        endTimeIndex = []

        find_time(s2)
        print(startTime)
        print(endTime)
        missingex = False
        # c = times
        for c in range(len(startTime)):
            # check if multiple times for one date -> missing date?
            try: # not the last start time
                if startTime[c] < startTime[c+1] and missingex == False: #time in date
                    createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], dates[i], startTime[c], endTime[c])
                    #print(dates[i], startTime[c], startTime[c+1], missingex)
                      
                else: # c+1 > c 
                    if missingex == False: # add c to date
                        createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], dates[i], startTime[c], endTime[c])
                        missingex = True
                        #print(dates[i], startTime[c], startTime[c], missingex)
                    else: #missingex is true 
                        # multiple c for one missing date
                        try: # c+2 could be out of bounds or smaller
                            if startTime[c] < startTime[c+1]:
                                createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], missingdates[0], startTime[c], endTime[c])
                                #print(missingdates[0], startTime[c], startTime[c+1], missingex)
                            else: #another missing date c > c+1
                                createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], missingdates[0], startTime[c], endTime[c])
                                missingex = False
                                #print(missingdates[0], startTime[c], endTime[c], missingex)
                                missingdates.pop(0)
                                #print(missingdates)
                        except IndexError: #c last index
                            createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], missingdates[0], startTime[c], endTime[c])
                            missingex = False
                            #print(missingdates[0], startTime[c], endTime[c], missingex)
                            missingdates.pop(0)
                            #print(missingdates)
            except IndexError: #c is last index
                if missingex == False:
                    createCal(s2[endTimeIndex[c]+1:-1], dates[i], startTime[c], endTime[c])
                    #print(dates[i], startTime[c], endTime[c], missingex)
                else:
                    createCal(s2[endTimeIndex[c]+1:-1], missingdates[0], startTime[c], endTime[c])
                    missingex = False
                    #print(missingdates[0], startTime[c], endTime[c], missingex)
                    missingdates.pop(0)
                    #print(missingdates)
            
    except IndexError:
        s2 = s1[endIndex[i]:-1]
        startTime = []
        endTime = []
        startTimeIndex = []
        endTimeIndex = []

        find_time(s2)
        print(startTime)
        print(endTime)
        missingex = False

        for c in range(len(startTime)):
            # check if multiple times for one date -> missing date?
            try: # not the last start time
                if startTime[c] < startTime[c+1] and missingex == False: #time in date
                    createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], dates[i], startTime[c], endTime[c])
                    print(startTime[c], startTime[c+1], missingex)
                      
                else: # c+1 > c 
                    if missingex == False: # add c to date
                        createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], dates[i], startTime[c], endTime[c])
                        missingex = True
                        print(startTime[c], startTime[c], missingex)
                    else: #missingex is true 
                        # multiple c for one missing date
                        try: # c+2 could be out of bounds or smaller
                            if startTime[c] < startTime[c+1]:
                                createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], missingdates[0], startTime[c], endTime[c])
                                print(startTime[c], startTime[c+1], missingex)
                            else: #another missing date c > c+1
                                createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], missingdates[0], startTime[c], endTime[c])
                                missingdates.pop(0)
                                missingex = False
                                print(startTime[c], endTime[c], missingex)
                                print(missingdates)
                        except IndexError: #c last index
                            createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], missingdates[0], startTime[c], endTime[c])
                            missingdates.pop(0)
                            missingex = False
                            print(startTime[c], endTime[c], missingex)
                            print(missingdates)
            except IndexError: #c is last index
                if missingex == False:
                    createCal(s2[endTimeIndex[c]+1:-1], dates[i], startTime[c], endTime[c])
                    print(startTime[c], endTime[c], missingex)
                else:
                    createCal(s2[endTimeIndex[c]+1:-1], missingdates[0], startTime[c], endTime[c])
                    missingdates.pop(0)
                    missingex = False
                    print(startTime[c], endTime[c], missingex)
                    print(missingdates)

        
        # for c in range(len(startTime)): 
        #     try:

        #         createCal(s2[endTimeIndex[c]+1:startTimeIndex[c+1]-1], dates[i], startTime[c], endTime[c])
        #     except IndexError: 
        #         createCal(s2[endTimeIndex[c]+1:-1], dates[i], startTime[c], endTime[c])
        #     print(startTime[c], endTime[c])
        
with open('my.ics', 'a') as f:
        f.writelines(cal)    

