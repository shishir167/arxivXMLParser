
import os
import urllib.request
import time
import xml.etree.ElementTree as ET


def main():
    counter = 59

    token = "1122234|59001"
    while token:
        token = getResumptionToken(xmlResult)
        newPath = "?verb=ListRecords&resumptionToken=" + token
        xmlResult = callArxivApi(newPath)
        counter += 1
        print ("[info] counter = ", counter)
        print ("[info] token = ", token)
        filename = "./xml/" + str(counter) + ".xml"
        print ('[info] filename = ' + filename)
        try:
            fd = open(filename, 'w')
            fd.write(xmlResult.decode("utf-8"))
            fd.close()
        except:
            print('[info] write error')



def getResumptionToken(parseString):
    print ("Getting resumptionToken")
    root = ET.fromstring(parseString)
    token = next(root.iter("{http://www.openarchives.org/OAI/2.0/}resumptionToken"))
    return token.text

def callArxivApi(path):
    url = 'http://export.arxiv.org/oai2'
    url = url + path
    print ("[info] calling url", url)
    s = ""
    while not s:
        try:
            with urllib.request.urlopen(url) as url:
                s = url.read()
                print ("[info] got xml from api")
        except urllib.error.HTTPError as e:
            print("got Http error")
            print("trying after 20 seconds")
            time.sleep(20)
        except urllib.error.URLError as e:
            print("got URL error", str(e))
            print("trying after 20 seconds")
            time.sleep(2)
        except urllib.error.ContentTooShortError as e:
            print("got Content too short error")
            print("trying after 2 seconds")
            time.sleep(20)
    return s



if __name__ == "__main__":
    main()


