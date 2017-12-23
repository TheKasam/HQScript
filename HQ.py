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


ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'

def main():

    #grab_image() #edit values based on screen

    question, answers = get_text()
    # ans_method_one(question, answers)
    # ans_method_four(question, answers)
    # ans_method_three(question, answers)
    # ans_method_two(question, answers)
    ans_method_five(question, answers)


    end = time.time()
    print(end - start)
    #print(ans.json()['queries']['request'])

def grab_image():
    im=ImageGrab.grab(bbox=(30,150,380,500)) # X1,Y1,X2,Y2
    im.show()
    ImageGrab.grab_to_file('imageTest.png')
def ans_method_one(question, answers):

    q = 'what is the epipremnum aureum house plant known as?'
    questionWord = question.strip().split(" ")[0]

    #other method is to get request with actual url and use bs4 to locate the answer google gives a
    if True: #questionWord == 'What' or questionWord == "of":
        googleResult = requests.get('https://www.google.com/search?q='+question)

        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        headText = soup.find('div',{'class':'_sPg'})
        if soup != None and headText != None:

            headText = headText.text
            headText = headText.lower()
            #print(headText)
            headText = headText.replace(" a ","")
            headText = headText.replace(" i ","")
            headText = headText.replace("."," ")
            headText = headText.split(" ")
            freqDict = {}

            for x in answers:
                freqDict[x] = 0

            for x in headText:
                x = x.strip(',')
                print(x,end=" ")
                if x == answers[0]:
                    freqDict[answers[0]] += 1
                elif x == answers[1] :
                    freqDict[answers[1]] += 1
                elif  x == answers[2]:
                    freqDict[answers[2]] += 1
            print()
            print()
            print("Google",end=" ")
            print(freqDict)

#count in api
def ans_method_four(question, answers):
    print("API Count")
    search_key = 'AIzaSyBqcHbDxpT8KGF1dEC7glg5dq2b2H7jn7o'
    search_id = '016671866865682481259:ivh1ljytmsm'
    #test question 1: 'what is the epipremnum aureum house plant known as?'

    for ans in answers:
        q = question + " " + ans

        queryAnswer = requests.get('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
        #print('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
        #print(ans + ":  ")
        #print(queryAnswer.json()['queries']['request'][0]['totalResults'])
        print(ans + ": " + str(queryAnswer.text.lower().count(ans)))

def ans_method_five(question, answers):
    googleResult = requests.get('https://www.bing.com/search?q='+question)

    soup = bs.BeautifulSoup(googleResult.text,'lxml')
    headText = soup.find('li',{'class':"b_ans b_top b_topborder"})
    print(soup)
    print(headText)
#seems to be good for which of the following
def ans_method_two(question,answers):
    print()
    print("Number of results for each option:")
    for ans in answers:
        questionTemp = question + " " + '"'+ ans + '"'
        googleResult = requests.get('https://www.google.com/search?q='+questionTemp)

        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        results_num = soup.find('div',{'id':'resultStats'})
        print(ans + ": " +results_num.text.split(" ")[1])



def ans_method_three(question,answers):

    print()
    print("Google Number of times each option appears on page")
    googleResult = requests.get('https://www.google.com/search?q='+question)

    soup = bs.BeautifulSoup(googleResult.text,'lxml')
    results_num = soup.find('div',{'id':'search'})
    for ans in answers:

        print(ans + ": " + str(results_num.text.replace(",","").lower().count(ans)))



def get_text():
    api_key = 'AIzaSyD62V5CUucbPUnx21i-cQvKS9cOngm2eeI'
    image_filename = ['imageTest2.png']
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
                textLst = text.lower().split("\n")
                textStart = 0

                #lines of question
                #1 line
                if textLst[textStart][-1] == "?":
                    question = textLst[textStart]
                    answers = textLst[textStart+1:textStart+4]

                #2lines
                elif textLst[textStart+1][-1] == "?":
                    question = textLst[textStart] + " "+textLst[textStart+1]
                    answers = textLst[textStart+2:textStart+5]
                #3lines
                elif textLst[textStart+2][-1] == "?":
                    question = textLst[textStart] + " "+textLst[textStart+1] +" "+textLst[textStart+2]
                    answers = textLst[textStart+3:textStart+6]
                else:
                    print("error couldn't find questions")
                    sys.exit(0)
                print()
                print(question)
                print()

                print(answers)
                print()
                return(question, answers)

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
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filename),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response





main()
