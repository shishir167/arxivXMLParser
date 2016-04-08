import xml.etree.ElementTree as ET
import urllib.request
import time
import os
import collections

dictAuthors = collections.OrderedDict();
dictYears = {};
idNo = 1;
nodesFiles = [];
minYear = 2050;
maxYear = -1;
dictAuthorAffiliation = {};
dictEdges = collections.OrderedDict(); #stores all authors alongside publication dates
edgesFiles = [];

def main():
    xmlResult = callArxivApi("?verb=ListRecords&set=cs&metadataPrefix=arXiv")
    parseResults(xmlResult)
    # print("dict length: ", len(dictAuthors))
    token = getResumptionToken(xmlResult)
    counter = 0
    while token:
        counter += 1
        print ("counter =", counter)
        print ("token = ", token)
        newPath = "?verb=ListRecords&resumptionToken=" + token
        xmlResult = callArxivApi(newPath)
        parseResults(xmlResult)
        print("dict length: ", len(dictAuthors))
        token = getResumptionToken(xmlResult)
    writeRecordsNodes()


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

def processAuthorNodes(authors, pubYear):
    global dictAuthors;
    global dictYears;
    global idNo;
    global minYear;
    global maxYear;

    for auth in authors:
        if not ((auth is None) or (pubYear is None)):
            affiliation = ''
            if len(auth) == 2:
                author = auth[1].text + " " + auth[0].text;
            elif len(auth) == 3:
                if "affiliation" in auth[2].tag:
                    affiliation = auth[2].text
                    author = auth[1].text + " " + auth[0].text;
                else:
                    author = auth[1].text + " " + auth[0].text + " " + auth[2].text;
                    print (author)
            else:
                author = auth[0].text;

            year = int(pubYear.text.split('-')[0]);
            # print("author: ", author.encode('utf-8'), "year: ", year.encode('utf-8'))
            if(year < minYear):
                minYear = year
            elif(year > maxYear):
                maxYear = year

            if not author in dictAuthors: # check if author record already exists
                dictAuthors.update({author : idNo});
                dictYears.update({author : [year]});
                idNo += 1;
            else:
                # print("duplicate record", author.encode('utf-8'))
                if not year in dictYears[author]:
                    dictYears[author].append(year);

            if affiliation:
                # print(affiliation)
                if not author in dictAuthorAffiliation: # check if author record already exists
                    dictAuthorAffiliation.update({author : affiliation});

def processAuthorEdges(authors, pubYear, journalReference):
    if len(authors) < 2: #error checking, return if only one author for a publication
        return;

    index = 1;
    numAuthors = len(authors);
    auth_key_template = "{} {} {} {}"
    for a in authors:
        if not ((a is None) or (pubYear is None)):
            auth = a.text;
            year = int(pubYear.text.split('-')[0]);
            firstAuth = "";
            secondAuth = "";

            if(year < minYear):
                minYear = year
            elif(year > maxYear):
                maxYear = year

            for num in range(index, numAuthors): #iterate through all co authors
                coAuthor = authors[num].text;

                if(auth > coAuthor): #auth comes behind alphabetically
                    firstAuth = coAuthor.encode('utf-8');
                    secondAuth = auth.encode('utf-8');
                else:
                    firstAuth = auth.encode('utf-8');
                    secondAuth = coAuthor.encode('utf-8');

                #authKey = dictAuthors[firstAuth] + " " + dictAuthors[secondAuth];
                authKey = auth_key_template.format(dictAuthors[firstAuth], dictAuthors[secondAuth], journalReference)

                if not authKey in dictEdges: # check if edge record already exists
                    dictEdges.update({authKey : [year]});
                else:
                    if not year in dictEdges[authKey]: # prevent duplicate publication years
                        dictEdges[authKey].append(year); #append year to publication list
        index = index + 1;

def writeRecordsNodes():
    nodesDictName = './results/NodesDict.txt';
    prefix = './results/nodes/nodes';
    suffix = '-01-01.txt';
    fileRef = {};
    write_template = "{},{},{}\n"
    nodes_write_template = "{},{}\n"


    for year in range(minYear, maxYear + 1):
        output = prefix + str(year) + suffix;
        nodesFiles.append(output);


    #open all nodes files
    for yearFile in nodesFiles:
        try:
            os.remove(yearFile);
        except OSError:
            pass;

        ref = open(yearFile, 'a');
        fileRef.update({yearFile : ref});

    nodesDictFile = open(nodesDictName, 'w');

    for a,y in dictYears.items():
        idNum = dictAuthors[a];
        nodesOutput = nodes_write_template.format(str(idNum), a.encode('utf-8'))
        nodesDictFile.write(nodesOutput)

        for year in y:
            resultFile = prefix + str(year) + suffix;
            ref = fileRef[resultFile];
            authorid = str(dictAuthors[a])
            affiliation = ""

            if a in dictAuthorAffiliation:
                affiliation = dictAuthorAffiliation[a]

            output = write_template.format(authorid, a.encode('utf-8'), affiliation)
            ref.write(output);

    for name, file in fileRef.items():
        file.close();

def writeRecordsEdges():
    prefix = './results/edges/edges';
    suffix = '-01-01.txt';
    for year in range(minYear, maxYear + 1):
        output = prefix + str(year) + suffix;
        edgesFiles.append(output);
    fileRef = {};

    #open all edges files
    for yearFile in edgesFiles:
        try:
            os.remove(yearFile);
        except OSError:
            pass;

        ref = open(yearFile, 'a');
        fileRef.update({yearFile : ref});

    for authKey,y in dictEdges.items():
        for year in y:
            resultFile = prefix + str(year) + suffix;
            ref = fileRef[resultFile];
            ref.write(authKey + "\n");

    for name, file in fileRef.items():
        file.close();


def parseResults(parseString):
    global dictAuthors
    #
    # tree = ET.parse(parseString)
    # root = tree.getroot()

    root = ET.fromstring(parseString)
    records = root.iter("{http://arxiv.org/OAI/arXiv/}arXiv")

    print ("[info] processing author records...")

    for record in records:
        authors = record.find('{http://arxiv.org/OAI/arXiv/}authors');
        pubYear = record.find('{http://arxiv.org/OAI/arXiv/}created');
        processAuthorNodes(authors, pubYear);



if __name__ == "__main__":
    main()
