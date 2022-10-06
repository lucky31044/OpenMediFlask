import requests
from google.api_core.exceptions import InvalidArgument
from google.cloud import vision
from google.cloud.vision import types
import httplib2,os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'google_api_account_tocken.json'
client = vision.ImageAnnotatorClient()

def google_text_extraction(pic_url):


    # h = httplib2.Http()
    # response, content = h.request(pic_url)
    # url = response["content-location"]
    # print(url)
    # image = vision.types.Image()
    # image.source.image_uri = url
    # response = client.document_text_detection(image=image)
    # print(response)
    # # Get text
    # docText = response.full_text_annotation.text
    # text = docText.rstrip("\n").replace('\n',' ')
    # print("##text"+text)


    r = requests.get(pic_url, allow_redirects=True)

    content = r.content
    image = types.Image(content=content)
    response = client.document_text_detection(image=image)

    # Get text
    docText = response.full_text_annotation.text
    text = docText.rstrip("\n").replace('\n',' ')

    return text
