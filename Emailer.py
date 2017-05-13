    #!/usr/bin/env python
#cron: 0 7,15,23 * * * cd /path/to/script && python emailer.py

''' Written by Mark Laubender 12/16/2015'''

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from subprocess import Popen, PIPE
import time
import datetime
import traceback

'''
takes input from a foswiki shift log text file, strips, cleans, and stores the data 
in a python list structure
'''
class FileParser:
    def __init__(self):
        try:
            self.title = None #populated by getTableDataStart()
            self.data = self.openFile()
            self.tableDataStart = self.getTableDataStart()
            self.tableData = self.populateTableData()
        except:
            print "FileParser: error creating FileParser object. The correct Shift log .txt file may be missing"

    #find the right report by building the correct path based on the current shift
    def buildPath(self):
        path = path
        date = datetime.datetime.now().strftime('%b' + '%d' + '20' + '%y')
        shift = self.findShift(int(time.asctime()[11:13]))
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%b' + '%d' + '20' + '%y')

        #date = datetime.date(2016, 2, 3).strftime('%b' + '%d' + '20' + '%y') #uncomment to specify date
        #shift = self.findShift(int(('Fri Feb  5 23:05:33 2016')[11:13])) #template shift, rewrite accordingly for testing
        #yesterday = (datetime.date(2016, 2, 3) - datetime.timedelta(days=1)).strftime('%b' + '%d' + '20' + '%y')

        if shift[2] == 'Night':
            self.title = format("Report %i - %s - %s" % (shift[0], str(datetime.datetime.now()-datetime.timedelta(days=1))[0:10], shift[1]))
            return path + shift[2] + yesterday + ".txt"
        else: 
            self.title = format("Report %i - %s - %s" % (shift[0], str(datetime.datetime.now())[0:10], shift[1]))
            return path + shift[2] + date + ".txt"

    #find the right shift depending on the current time
    #shift overlap of one hour (<=) - no chance of missing the right shift
    def findShift(self, hour):
        if hour <= 7: 
            return (3, '2300-700', 'Night')
        elif hour > 15 and hour <= 23: 
            return (2, '1500-2300', 'Swing')
        else: 
            return (1, '0700-1500', 'Morning')

    def openFile(self):
        outerList = []
        try:
            sFile = open(self.buildPath(), "r") #TODO: make a method for sending emails WITHOUT checking shift
            
            for row in sFile.read().splitlines():
                tempRow = ""
                for word in row.split():
                    if word[0] == '!': #scrubbing out wiki artifacts
                        newString = word[1:]
                        word = newString
                    tempRow += word + ' '       
                innerList = []
                if tempRow != '': #get rid of blank lines right away
                    innerList.append(self.unicodetoascii(tempRow))
                    outerList.append(innerList)

            sFile.close
        except:
            print 'FileParser: error opening shift report txt file'
            traceback.print_exc()
        return outerList

    #because fuck you python 2
    def unicodetoascii(self, text):
        uni2ascii = {
            ord('\xe2\x80\x99'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\x9c'.decode('utf-8')): ord('"'),
            ord('\xe2\x80\x9d'.decode('utf-8')): ord('"'),
            ord('\xe2\x80\x9e'.decode('utf-8')): ord('"'),
            ord('\xe2\x80\x9f'.decode('utf-8')): ord('"'),
            ord('\xc3\xa9'.decode('utf-8')): ord('e'),
            ord('\xe2\x80\x9c'.decode('utf-8')): ord('"'),
            ord('\xe2\x80\x93'.decode('utf-8')): ord('-'),
            ord('\xe2\x80\x92'.decode('utf-8')): ord('-'),
            ord('\xe2\x80\x94'.decode('utf-8')): ord('-'),
            ord('\xe2\x80\x94'.decode('utf-8')): ord('-'),
            ord('\xe2\x80\x98'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\x9b'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\x90'.decode('utf-8')): ord('-'),
            ord('\xe2\x80\x91'.decode('utf-8')): ord('-'),
            ord('\xe2\x80\xb2'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\xb3'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\xb4'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\xb5'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\xb6'.decode('utf-8')): ord("'"),
            ord('\xe2\x80\xb7'.decode('utf-8')): ord("'"),
            ord('\xe2\x81\xba'.decode('utf-8')): ord("+"),
            ord('\xe2\x81\xbb'.decode('utf-8')): ord("-"),
            ord('\xe2\x81\xbc'.decode('utf-8')): ord("="),
            ord('\xe2\x81\xbd'.decode('utf-8')): ord("("),
            ord('\xe2\x81\xbe'.decode('utf-8')): ord(")"),
        }
        return text.decode('utf-8').translate(uni2ascii).encode('ascii')

    #populates a list with indices into the text file where one table's data
    #starts and stops, needed for populateTableData()
    def getTableDataStart(self):
        start = []
        for count, list in enumerate(self.data):
            for line in list:
                if '<h2' in line:
                    start.append(count)
        start.append(len(self.data))
        return start

    #the text file is very messy with a lot of characters we don't want. This
    #cleans the text and puts it in the correct data structure
    def cleanList(self, mylist):
        tempstring = ""
        templist = []
        for line in mylist:
                tempstring += (str(line))
        templist = tempstring.split("|")
        
        ret = []
        for line in templist: 
            if '][' not in line and "']" not in line and '"]' not in line and (len(line) > 2 or line == ' '):
                ret.append(line)
        return ret

    def cleanReportInfo(self, mylist):
        tempstring = ""
        templist = str(mylist).split("|")
        for line in templist:
            if "[['" not in line and '][' not in line and "']" not in line and '"]' not in line and (len(line) > 2 or line == ' '):
                tempstring += line
        return tempstring

    def checkIfReviewerIsFilled(self):
        #print self.tableData[-1][-1]
        if self.tableData[-1][-1] == ' Not Reviewed ' or self.tableData[-1][-1] == ' ':
            return False
        else:
            return True

    #adds content to the tableData list
    #+4 because we're jumping over table title, %EDITTABLE, %TABLE, and row title lines
    def populateTableData(self):
        sHighlights = []
        opHighlights = []
        shiftNotes = []
        reportInfo = []
        data = []

        sHighlights = self.cleanList(self.data[self.tableDataStart[0]+4:self.tableDataStart[1]])
        oHighlights = self.cleanList(self.data[self.tableDataStart[1]+4:self.tableDataStart[2]])
        shiftNotes = self.cleanList(self.data[self.tableDataStart[2]+4:self.tableDataStart[3]])
        reportInfo = self.cleanList(self.data[self.tableDataStart[3]+4:self.tableDataStart[4]])
        
        data.extend((sHighlights, oHighlights, shiftNotes, reportInfo))
        
        return data

    #debugging
    def printList(self):
        for line in self.tableData:
            print line

    #debugging
    def printData(self):
        for line in self.data:
            print line

'''
This class dynamically builds the email body from an HTML email template.  It is 
passed the shift log data, already nicely structured in a list of lists, and then 
dynamically creates table data rows - one per each entry in the associated list.    
'''
class HTMLBuilder:
    def __init__(self):
        self.template = self.getTemplate()
        self.prefix = '<tr>\n'
        self.postfix = '</tr>\n'

    #opens the HTML email template from a file and stores it in a list
    def getTemplate(self):
        templateList = []
        try:
            tfile = open("emailTemplate.html", 'r')
            templateList = tfile.readlines()
            tfile.close()
        except:
            print 'HTMLBuilder: error opening HTML email template'
        return templateList
    
    #We're inserting rows to the email template, so we need to know where to start 
    #inserting the rows
    def findNextIndex(self):
        for count, line in enumerate(self.template):
            if '<a index>' in line:
                del self.template[count] #for the next time this function is called, we don't want to keep inserting at the same place
                return count

    #these next 2 functions do the actual building of the email body.
    def editHTML(self, scraperText):
        iteration = 0
        for text in scraperText:
            index = self.findNextIndex()
            newRow = []
            newRow.append(self.prefix)

            for count, word in enumerate(text):
                if count % 5 == 0 and count != 0: #put each item in the right column and ignore first iteration(because it returns true)
                    newRow.append(self.postfix)
                    newRow.append(self.prefix)
                newRow.append('<td class="column' + str(count%5+1) + '">' + word + '</td>\n')
                if count % 5 == 0:
                    if 'None' in word and text[count+1] == " ": 
                        newRow.append('<td class="column' + str(count%5+1) + '">' + '</td>\n')
                        newRow.append('<td class="column' + str(count%5+1) + '">' + '</td>\n')
                        newRow.append('<td class="column' + str(count%5+1) + '">' + '</td>\n')
                        newRow.append('<td class="column' + str(count%5+1) + '">' + '</td>\n')
                        break

            newRow.append(self.postfix)
            if iteration < 2: #last table has a different format, so it uses a different function
                self.insertRow(newRow, index)
                iteration = iteration + 1
            else:# iteration < 3 :
                self.insertShiftNotes(text, index)
                self.insertReportInfo(scraperText[-1])
                return

    def insertReportInfo(self, text):
        index = self.findNextIndex()
        newRow = []
        newRow.append(self.prefix)

        for name in text:
            newRow.append('<td>' + name + '</td>\n')
        newRow.append(self.postfix)
        self.insertRow(newRow,index)

    #last category has a different layout than the rest, hence it's own function
    #combining this with editHTML() made the function too bulky
    def insertShiftNotes(self, text, index):
        newRow = []
        newRow.append(self.prefix)

        for count, word in enumerate(text):
            if count % 3 == 0 and count != 0:
                newRow.append(self.postfix)
                newRow.append(self.prefix)
            newRow.append('<td class="column' + str(count%3+1) + 'D">' + word + '</td>\n')
            if count % 3 == 0:
                if 'None' in word and text[count+1] == " ":
                    newRow.append('<td class="column' + str(count%3+1) + 'D">' + '</td>\n')
                    newRow.append('<td class="column' + str(count%3+1) + 'D">' + '</td>\n')
                    break
        
        newRow.append(self.postfix)
        self.insertRow(newRow, index)

    #TODO: I can actually do the offset count here
    def insertRow(self, newRow, count):
        tcount = count
        for item in newRow:
            self.template.insert(tcount, item)
            tcount += 1

    #debugging
    def printCount(self):
        for c in self.insertIndices:
            print c

    #debugging
    def printTemplate(self):
        for line in self.template:
            print line


'''
This class has the responsibility of building the email(to, from, subject, body),
and sending the email
'''
class Emailer:
    def __init__(self, subject):
        self.EMAIL_TO = to@email.com
        self.EMAIL_FROM = from@email.com
        self.EMAIL_SUBJECT = subject
        self.DATA = None #populated from setData()

    def send_email(self):
        message = MIMEMultipart('alternative')
        message['Subject'] = self.EMAIL_SUBJECT
        message['To'] = self.EMAIL_TO
        message['From'] = self.EMAIL_FROM
        
        
        payload = MIMEText(self.DATA, 'html')
        message.attach(payload)

        #email through sendmail linux command
        try:
            process = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin = PIPE) #-t reads message for recipients. -oi ignores single dots on lines by themselves
            process.communicate(message.as_string())
        except:
            print 'Emailer: Unable to send email'

    def setDATA(self, data):
        self.DATA = data;


'''
facade pattern to hide all the ugly function calls and simplify things a bit.
All we need to do is instantiate and call start()
'''
class Controller:
    def __init__(self):
        self.fileParser = FileParser()
        try:
            self.mailer = Emailer(self.fileParser.title)
        except:
            print "Controller: error finding title"
            self.mailer = Emailer("none") #email won't be set out if we get here, this is only for the next try/catch block
        self.hTMLBuilder = HTMLBuilder()  # I should refactor this
    
    def start(self):
        try:
            self.hTMLBuilder.editHTML(self.fileParser.tableData)
            self.mailer.setDATA(''.join(self.hTMLBuilder.template).encode('ascii')) #toString
            self.mailer.send_email()
        except:
            print "Controller: failed to create objects"

      
if __name__=='__main__':
    
    controller = Controller()
    count = 0
    while not controller.fileParser.checkIfReviewerIsFilled() and count <= 60:
        print "waiting"
        time.sleep(60)
        count += 1
        controller = Controller()
    controller.start()    
    

    '''debugging'''
#    controller = Controller()
#    controller.start()
#    controller.hTMLBuilder.printTemplate()
    #controller.fileParser.printList()
    #controller.hTMLBuilder.printCount()
    #controller.fileParser.printData()
