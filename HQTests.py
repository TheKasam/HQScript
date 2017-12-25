import time
start = time.time()
from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests
import bs4 as bs
from PIL import Image
import pyscreenshot as ImageGrab
import urllib.request
import time

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'


oFile = open('test2.txt','w')
curretQuestionResults = []

def main():

    #grab_image() #edit values based on screen
    oFile.write('Test1: Friday, December 15, 2017'+"\n")
    ansLst = [2,2,1,2,1,2,2,2,0,1,2,1]
    totalRight = 0
    for x in range(1,13):
        #correct answer
        cAns = [ansLst[x-1]]
        oFile.write('Q'+str(x)+": ")
        question, answers = get_text("test2/test"+str(x)+".png")
        if "not" in question:
            cAns.append("not")
            question.replace("not","")
        ans1 = ans_method_one(question, answers, cAns)
                #five from 1 #ans_method_five(question, answers)
        ans2 = ans_method_four(question, answers, cAns)
        ans3 = ans_method_three(question, answers, cAns)
        ans4 = ans_method_two(question, answers, cAns)

        if sum(curretQuestionResults[-4:]) > 0:
            oFile.write(":) " + question +"\n")
            totalRight += 1
        else:
            oFile.write(":( " + question + "\n")



    end = time.time()
    print(end - start)
    #print(ans.json()['queries']['request'])


def formatAns(lst,cAns):
    print(lst)
    if len(cAns) ==2:
        maxIndex = lst.index(min(lst))
    else:
        maxIndex = lst.index(max(lst))
    indexes = [0,1,2]
    indexes.remove(maxIndex)
    if lst[maxIndex] == lst[indexes[0]] or lst[maxIndex] == lst[indexes[1]]:
         oFile.write("0 ")
         curretQuestionResults.append(0)
    elif maxIndex == cAns[0]:
        oFile.write("i ")
        curretQuestionResults.append(1)
    else:
        oFile.write("x ")
        curretQuestionResults.append(-1)

def grab_image():
    im=ImageGrab.grab(bbox=(30,150,380,500)) # X1,Y1,X2,Y2
    im.show()
    ImageGrab.grab_to_file('imageTest.png')
def ans_method_one(question, answers, cAns):

    q = 'what is the epipremnum aureum house plant known as?'
    questionWord = question.strip().split(" ")[0]

    #other method is to get request with actual url and use bs4 to locate the answer google gives a
    if True: #questionWord == 'What' or questionWord == "of":
        #googleResult = requests.get('https://www.google.com/search?q='+question)
        googleResult =  getUrlData('https://www.google.com/search?q='+question)
        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        headText = soup.find('div',{'class':'_sPg'})
        boolReturn = True
        if soup != None and headText != None:

            headText = headText.text
            textPass = headText.lower()
            headText = textPass
            #print(headText)
            headText = headText.replace(" a ","")
            headText = headText.replace(" i ","")
            headText = headText.replace("."," ")

            freqDict = {}
            print(headText, end='\n')
            for ans in answers:
                freqDict[ans] = headText.count(ans)


            print("Google",end=" ")
            print(freqDict)

            keysLst = []
            for x in freqDict:
                keysLst.append(freqDict[x])


            formatAns(keysLst, cAns)

            ans_method_five(question, answers, cAns, textPass, boolReturn)
        else:
            boolReturn = False
            oFile.write("0 ")
            curretQuestionResults.append(0)
            ans_method_five(question, answers, cAns, "", boolReturn )



#seems to be good for which of the following
def ans_method_two(question,answers, cAns):
    print()
    print("Number of results for each option:")
    queryLst = []
    for ans in answers:
        questionTemp = question + " " + '"'+ ans + '"'
        #googleResult = requests.get('https://www.google.com/search?q='+questionTemp)
        googleResult = getUrlData('https://www.google.com/search?q='+questionTemp)
        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        results_num = soup.find('div',{'id':'resultStats'})
        results = results_num.text.split(" ")
        print()

        if  "No results found for" in googleResult.text:
            queryLst.append(0)

        elif len(results) == 2:

            strToParse = results_num.text.split(" ")[0]
            if "," in strToParse:
                strToParse = strToParse.replace(",","")
            queryLst.append(float(strToParse))

        elif len(results) == 3:

            strToParse = results_num.text.split(" ")[1]
            if "," in strToParse:
                strToParse = strToParse.replace(",","")
            queryLst.append(float(strToParse))

        else:
            queryLst.append(0)

    formatAns(queryLst,cAns)

def ans_method_three(question,answers, cAns):

    print()
    print("Google Number of times each option appears on page")
    #googleResult = requests.get('https://www.google.com/search?q='+question)
    googleResult = getUrlData('https://www.google.com/search?q='+question)
    queryLst =[ ]
    soup = bs.BeautifulSoup(googleResult.text,'lxml')
    results_num = soup.find('div',{'id':'search'})
    for ans in answers:

        print(ans + ": " + str(results_num.text.replace(",","").lower().count(ans)))
        queryLst.append(results_num.text.replace(",","").lower().count(ans))
    formatAns(queryLst,cAns)

#count in api
def ans_method_four(question, answers, cAns):
    print("API Count")
    search_key = 'AIzaSyBqcHbDxpT8KGF1dEC7glg5dq2b2H7jn7o'
    search_id = '016671866865682481259:ivh1ljytmsm'
    #test question 1: 'what is the epipremnum aureum house plant known as?'
    queryLst = []
    for ans in answers:
        q = question + " " + ans

        #queryAnswer = requests.get('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
        queryAnswer = getUrlData('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
        #print('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
        #print(ans + ":  ")
        #print(queryAnswer.json()['queries']['request'][0]['totalResults'])
        queryLst.append(queryAnswer.text.lower().count(ans))
        print(ans + ": " + str(queryAnswer.text.lower().count(ans)))
    formatAns(queryLst,cAns)

#same sentace
def ans_method_five(question, answers, cAns, soupTxt, boolReturn):
    if boolReturn:
        question = question.replace("-","")
        soupSentence = soupTxt.split(".")
        ansLst = [0,0,0]
        for sentace in soupSentence:
            for ansInx in range(len(answers)):
                if answers[ansInx] in sentace:
                    ansLst[ansInx] += 1

        formatAns(ansLst,cAns)



    else:
        formatAns([0,0,0],cAns)
def get_text(imageName):
    api_key = 'AIzaSyD62V5CUucbPUnx21i-cQvKS9cOngm2eeI'
    image_filename = [imageName]
    #crop_image(image_filename[0])
    if not api_key or not image_filename:
        print("missing key or file name")
    else:
        print("a")
        response = request_ocr(api_key, image_filename)
        print("b")
        if response.status_code != 200 or response.json().get('error'):
            print('error no internet connection?')#response.text to see errro
        else:
            for idx, resp in enumerate(response.json()['responses']):

                # print the plaintext to screen for convenience
                text = resp['textAnnotations'][0]['description']
                print(text)
                textLst = text.lower().split("\n")

                qEnd = 0
                question = ""
                for x in range(len(textLst)):
                    question += textLst[x] + " "
                    if textLst[x][-1] == "?":
                        qEnd = x
                        break

                answers = []
                for x in range(qEnd+1, qEnd+4):
                    answers.append(textLst[x])

                if not question or not answers:
                    print("error couldn't find questions")
                    sys.exit(0)
                print()
                print(question)
                print()

                print(answers)
                print()
                return(question, answers)

def getUrlData(url):
    page = ''
    while page == '':
        try:
            page = requests.get(url)
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    return page

def make_image_data_list(image_filename):
    """
    image_filename is a list of filename strings
    Returns a list of dicts formatted as the Vision API
        needs them to be
    """
    img_requests = []
    for imgname in image_filename:
        with open(imgname, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }]
            })
    return img_requests

def make_image_data(image_filename):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filename)
    return json.dumps({"requests": imgdict }).encode()

def request_ocr(api_key, image_filename):
    response = ""
    while not response:
        try:
            response = requests.post(ENDPOINT_URL,
                                 data=make_image_data(image_filename),
                                 params={'key': api_key},
                                 headers={'Content-Type': 'application/json'})
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue

    return response





main()
