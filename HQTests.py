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
import wikipedia
import spacy


ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'


# oFile = open('test1.4.txt','w')
curretQuestionResults = []

def main():
    grab_image()
    #grab_image() #edit values based on screen
    #oFile.write('Test1: Friday, December 15, 2017'+"\n")
    ansLst = [2,2,1,2,1,2,2,2,0,1,2,1]
    totalRight = 0
    for x in range(1,2):
        #correct answer
        cAns = [ansLst[x-1]]
       # oFile.write('Q'+str(x)+": ")
        question, answers = get_text("test3/test"+str(x)+".png")
        if "not" in question:
            cAns.append("not")
            question.replace("not","")
        question = question.replace(",","")
        #google head
        ans1 = ans_method_one(question, answers, cAns)
                #five from 1 #ans_method_five(question, answers)
        #count in api
        ans2 = ans_method_four(question, answers, cAns)
        #count in google
        ans3 = ans_method_three(question, answers, cAns) #3 calls method6
        #count in first url  #######geet all url######?????
        #method 6
        #countnum of results
        ans4 = ans_method_two(question, answers, cAns)
        #ans7 = ans_method_seven(question, answers, cAns)

        # if sum(curretQuestionResults[-6:]) > 0:
        #     oFile.write(":) " + question +"\n")
        #     totalRight += 1
        # else:
        #     oFile.write(":( " + question + "\n")


    print(formatDef)
    end = time.time()
    print(end - start)
    #print(ans.json()['queries']['request'])

formatDef = []
def formatAns(lst,cAns):
    print(lst)
    if len(cAns) ==2:
        maxIndex = lst.index(min(lst))
    else:
        maxIndex = lst.index(max(lst))
    formatDef.append(maxIndex)
    # indexes = [0,1,2]
    # indexes.remove(maxIndex)
    # print(indexes)
    # print(maxIndex)
    # print(lst)
    # if lst[maxIndex] == lst[indexes[0]] or lst[maxIndex] == lst[indexes[1]]:
    #      oFile.write("0 ")
    #      curretQuestionResults.append(0)
    # elif maxIndex == cAns[0]:
    #     oFile.write("i ")
    #     curretQuestionResults.append(1)
    # else:
    #     oFile.write("x ")
    #     curretQuestionResults.append(-1)
    print(maxIndex+1)

def grab_image():
    im=ImageGrab.grab(bbox=(0,150,380,500)) # X1,Y1,X2,Y2
    im.show()
    im.save("test3/test1.png", "PNG")

#Google counts options in headText
def ans_method_one(question, answers, cAns):



    #other method is to get request with actual url and use bs4 to locate the answer google gives a
    if True: #questionWord == 'What' or questionWord == "of":
        #googleResult = requests.get('https://www.google.com/search?q='+question)
        googleResult =  getUrlData('https://www.google.com/search?q='+question)
        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        headText = soup.find('div',{'class':'_oDd'})

        print(headText)
        boolReturn = True
        if soup != None and headText != None:

            headText = headText.span.text.lower()
            freqDict = {}
            print(headText, end='\n')
            for ans in answers:
                freqDict[ans] = headText.count(ans)


            print("Google",end=" ")
            keysLst = []
            for x in freqDict:
                keysLst.append(freqDict[x])

            formatAns(keysLst, cAns)

            #ans_method_five(question, answers, cAns, textPass, boolReturn)
        else:
            boolReturn = False
            #oFile.write("0 ")
            curretQuestionResults.append(0)
            #ans_method_five(question, answers, cAns, "", boolReturn )

#counts number of results
#seems to be good for which of the following
def ans_method_two(question,answers, cAns):
    print()
    print("Number of results for each option:")
    queryLst = []
    for ans in answers:
        questionTemp = question + " " + '"'+ ans + '"'
        googleResult = getUrlData('https://www.google.com/search?q='+questionTemp)
        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        results_num = soup.find('div',{'id':'resultStats'})

        print()
        if not results_num:
            queryLst.append(0)
            continue

        results = results_num.text.split(" ")
        if  "No results found for" in googleResult.text:
            queryLst.append(0)

        elif len(results) == 4:

            strToParse = results[0]
            if "," in strToParse:
                strToParse = strToParse.replace(",","")
            queryLst.append(float(strToParse))

        elif len(results) == 5:

            strToParse = results[1]
            if "," in strToParse:
                strToParse = strToParse.replace(",","")
            queryLst.append(float(strToParse))

        else:
            queryLst.append(0)

    formatAns(queryLst,cAns)

#Google number of times option appears on page
def ans_method_three(question,answers, cAns):

    print()
    print("Google Number of times each option appears on page")
    googleResult = getUrlData('https://www.google.com/search?q='+question)
    queryLst =[ ]
    soup = bs.BeautifulSoup(googleResult.text,'lxml')
    results_num = soup.find('div',{'id':'search'})
    for ans in answers:
        #do i neeed replace?
        print(ans + ": " + str(results_num.text.replace(",","").lower().count(ans)))
        queryLst.append(results_num.text.replace(",","").lower().count(ans))
    formatAns(queryLst,cAns)

    ans_method_six( question, answers, cAns, soup)

#count in api
def ans_method_four(question, answers, cAns):
    print("API Count")
    search_key = 'AIzaSyBqcHbDxpT8KGF1dEC7glg5dq2b2H7jn7o'
    search_id = '016671866865682481259:ivh1ljytmsm'
    #test question 1: 'what is the epipremnum aureum house plant known as?'
    queryLst = []
    for ans in answers:
        q = question

        #queryAnswer = requests.get('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
        queryAnswer = getUrlData('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)

        #print(queryAnswer)
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


#getting first link
def ans_method_six(question, answers, cAns, soup):
    links = soup.find_all('h3', {'class':'r'})
    url = links[0].a['href']
    print(url)

    firstUrl = getUrlData(url)
    ansCount = []
    textUrl = firstUrl.text.lower()
    for ans in answers:
        print(textUrl.count(ans))
        ansCount.append(textUrl.count(ans))
    print("first link")
    formatAns(ansCount,cAns)

def ans_method_seven(question, answers, cAns):
    print("method 7")
    nlp = spacy.load('en')

    question_lst = []
    question_lst_nlp = nlp(question[:-2])
    for word in question_lst_nlp:
        print(type(word))
        print(word)
        if not word.is_stop:
            question_lst.append(word.text)

    question_lst = filter(lambda a: a != '"', question_lst)
    question_lst = set(question_lst)


    wiki_results_lst = []
    ansCount = []

    for answer in answers:
        sites = wikipedia.search(answer)
        print(answer)
        site = sites[0] if len(sites) else ""

        if site != "":
            try:
                site = wikipedia.page(site)
            except wikipedia.exceptions.DisambiguationError as e:
                print(type(format(e)))
                e = format(e).split("\n")
                e = e[1:]
                for line in e:
                    line = line.lower()
                    print(line)
                    if line.count(answer) > 0:
                        site = wikipedia.page(line)
                        break

            wiki_results_lst.append(site.content)
        else:
            wiki_results_lst.append("")
    count = 0
    for site_txt in wiki_results_lst:
        count += 1
        question_word_count = 0

        for word in question_lst:

            question_word_count += site_txt.count(word)

        word_count_percent = question_word_count / len(site_txt.split(" "))
        print(count)
        # if count == 2:
        #     print(site_txt)
        ansCount.append(word_count_percent)


    formatAns(ansCount,cAns)
    print(question)
    print(question_lst)

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
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    page = ''
    while page == '':
        try:
            page = requests.get(url, headers=headers)
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
