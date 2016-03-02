import xml.etree.ElementTree as ET
import urllib.request
import time


def main():
    xmlResult = callArxivApi("?verb=ListRecords&set=cs&metadataPrefix=arXiv")
    print(len(xmlResult))
    token = getResumptionToken(xmlResult)
    for x in range(0, 9):
        print ("x =", x)
        print ("token = ", token)
        newPath = "?verb=ListRecords&resumptionToken=" + token
        xmlResult = callArxivApi(newPath)
        token = getResumptionToken(xmlResult)

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
            print ("returning xml")
            return s
    except urllib.error.HTTPError as e:
        print("got Http error")
        print("trying after 20 seconds")
        time.sleep(20)
        return callArxivApi(path)
    except urllib.error.URLError as e:
        print("got URL error", str(e))
        print("trying after 20 seconds")
        time.sleep(2)
        return callArxivApi(path)
    except urllib.error.ContentTooShortError as e:
        print("got Content too short error")
        print("trying after 2 seconds")
        time.sleep(20)
        return callArxivApi(path)


if __name__ == "__main__":
    main()
