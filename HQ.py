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


ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
makedirs(RESULTS_DIR, exist_ok=True)

def main():
    get_text()


    end = time.time()
    print(end - start)
    #print(ans.json()['queries']['request'])

def get_ans(question, answers):

    search_key = 'AIzaSyBqcHbDxpT8KGF1dEC7glg5dq2b2H7jn7o'
    search_id = '016671866865682481259:ivh1ljytmsm'
    q = 'what is the epipremnum aureum house plant known as?'
    ans = requests.get('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
    #print('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
    questionWord = question.strip().split(" ")[0]

    #other method is to get request with actual url and use bs4 to locate the answer google gives a
    if questionWord == 'What' or questionWord == "Of":
        googleResult = requests.get('https://www.google.com/search?q='+q)

        soup = bs.BeautifulSoup(googleResult.text,'lxml')

        if soup != None:
            headText = soup.find('div',{'class':'_sPg'})
            headText = str(headText.text).split(" ")
            freqDict = {}
            for x in answers:
                freqDict[x] = 0

            for x in headText:
                if answers[0] in x:
                    freqDict[answers[0]] += 1
                elif answers[1] in x:
                    freqDict[answers[1]] += 1
                elif answers[2] in x:
                    freqDict[answers[2]] += 1
            print(headText)
            print()
            print(freqDict)


def get_text():
    api_key = 'AIzaSyD62V5CUucbPUnx21i-cQvKS9cOngm2eeI'
    image_filename = ['imageTest.png']
    crop_image(image_filename[0])
    if not api_key or not image_filename:
        print("""
            Please supply an api key, then one or more image filenames
            $ python cloudvisreq.py api_key image1.jpg image2.png""")
    else:
        response = request_ocr(api_key, image_filename)
        if response.status_code != 200 or response.json().get('error'):
            print(response.text)
        else:
            for idx, resp in enumerate(response.json()['responses']):


                # print the plaintext to screen for convenience
                t = resp['textAnnotations'][0]
                print()
                textLst = t['description'].split("\n")
                print(textLst)
                textLst = textLst[2:]

                question = textLst[0] + " "+textLst[1]
                #print(question)

                answers = textLst[2:5]
                #print(answers)
                print()
                get_ans(question, answers)

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


def crop_image(name):
    img = Image.open(name )
    width = img.size[0]
    height = img.size[1]
    img2 = img.crop(
        (
            width - 100,
            height - 1000,
            width,
            height
        )
    )
    img2.save("img2.png")





main()
