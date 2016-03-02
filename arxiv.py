import xml.etree.ElementTree as ET
import urllib.request
import time


def main():

    xmlResult = callArxivApi("?verb=ListRecords&set=cs&metadataPrefix=arXiv");
    token = getResumptionToken(xmlResult)
    print ("token = ", token)
    newPath = "?verb=ListRecords&resumptionToken=" + token
    print (newPath)
    callArxivApi(newPath)

def getResumptionToken(parseString):
    print ("Getting resumptionToken")
    root = ET.fromstring(parseString)
    token = next(root.iter("{http://www.openarchives.org/OAI/2.0/}resumptionToken"))
    return token.text

def callArxivApi(path):
    url = 'http://export.arxiv.org/oai2'
    url = url + path
    print (url)
    s = ""

    try:
        with urllib.request.urlopen(url) as url:
            s = url.read()
    except urllib.error.HTTPError as e:
        print("got Http error")
        print("trying after 20 seconds")
        time.sleep(20)
        callArxivApi(path)
    except urllib.error.ContentTooShortError as e:
        print("got Content too short error")
        print("trying after 2 seconds")
        time.sleep(2)
        callArxivApi(path)
    return s


if __name__ == "__main__":
    main()
