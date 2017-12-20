from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests
import bs4 as bs

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
makedirs(RESULTS_DIR, exist_ok=True)

def main():
    get_text()



   #print('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)
    #print(ans.json()['queries']['request'])

def get_ans(question, answers):

    search_key = 'AIzaSyBqcHbDxpT8KGF1dEC7glg5dq2b2H7jn7o'
    search_id = '016671866865682481259:ivh1ljytmsm'
    q = 'What is the Epipremnum aureum house plant known as?'
    ans = requests.get('https://www.googleapis.com/customsearch/v1?key='+search_key+'&cx='+search_id+'&q='+q)

    questionWord = question.strip().split(" ")[0]

    #other method is to get request with actual url and use bs4 to locate the answer google gives a
    if questionWord == 'What' or questionWord == "Of":
        googleResult = requests.get('https://www.google.com/search?q='+q)

        soup = bs.BeautifulSoup(googleResult.text,'lxml')
        b = soup.find('div',{'class':'_sPg'})
        print(b)


def get_text():
    api_key = 'AIzaSyD62V5CUucbPUnx21i-cQvKS9cOngm2eeI'
    image_filenames = ['imageTest.png']
    if not api_key or not image_filenames:
        print("""
            Please supply an api key, then one or more image filenames
            $ python cloudvisreq.py api_key image1.jpg image2.png""")
    else:
        response = request_ocr(api_key, image_filenames)
        if response.status_code != 200 or response.json().get('error'):
            print(response.text)
        else:
            for idx, resp in enumerate(response.json()['responses']):
                # save to JSON file
                # imgname = image_filenames[idx]
                # jpath = join(RESULTS_DIR, basename(imgname) + '.json')
                # with open(jpath, 'w') as f:
                #     datatxt = json.dumps(resp, indent=2)
                #     print("Wrote", len(datatxt), "bytes to", jpath)
                #     f.write(datatxt)

                # print the plaintext to screen for convenience
                t = resp['textAnnotations'][0]
                print()
                textLst = t['description'].split("\n")
                textLst = textLst[2:]

                question = textLst[0] + " "+textLst[1]
                print(question)

                answers = textLst[2:5]
                print(answers)
                get_ans(question, answers)

def make_image_data_list(image_filenames):
    """
    image_filenames is a list of filename strings
    Returns a list of dicts formatted as the Vision API
        needs them to be
    """
    img_requests = []
    for imgname in image_filenames:
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

def make_image_data(image_filenames):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()

def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

def request_search(api_key):

 response = requests.post(ENDPOINT_URL,
                          data=make_image_data(image_filenames),
                          params={'key': api_key},
                          headers={'Content-Type': 'application/json'})
 return response












main()
