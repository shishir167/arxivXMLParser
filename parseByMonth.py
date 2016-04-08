import xml.etree.ElementTree as ET
import os
import collections
import codecs, sys


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
    counter = 1
    #reading all xml files(the files were downloaded as 1.xml, 2.xml, 3.xml ...)
    filename = "./xml/" + str(counter) + ".xml"
    fd = open(filename, 'r')
    xmlResult = fd.read()
    print ("[info] processing xml files...")
    parseResults(xmlResult)
    fd.close()
    counter = 0
    # while counter != 1:
    while xmlResult:
        counter += 1
        filename = "./xml/" + str(counter) + ".xml"
        try:
            fd = open(filename, 'r')
            xmlResult = fd.read()
            fd.close()
        except:
            break
        parseResults(xmlResult)
    print ("[info] writing node files...")
    writeRecordsNodes()
    print ("[info] writing edges files...")
    writeRecordsEdges()

def writeRecordsNodes():
    global minYear;
    global maxYear;
    nodesDictName = './results/NodesDict.txt';
    prefix = './results/nodes/nodes';
    suffix = '-01.txt';
    fileRef = {};
    write_template = "{},{},{}\n"
    nodes_write_template = "{},{}\n"

    #creating the node files
    for year in range(minYear, maxYear + 1):
            for x in range(1, 13):
                output = prefix + str(year) + '-' + "{0:0=2d}".format(x) + suffix;
                nodesFiles.append(output);

    #open all nodes files
    for yearFile in nodesFiles:
        try:
            os.remove(yearFile);
        except OSError:
            pass;

        ref = open(yearFile, 'a', encoding='utf-8');
        fileRef.update({yearFile : ref});

    nodesDictFile = open(nodesDictName, 'w', encoding='utf-8');

    for a,y in dictYears.items():
        idNum = dictAuthors[a];

        nodesOutput = nodes_write_template.format(str(idNum), str(a.encode('utf-8'), 'utf-8'))
        nodesDictFile.write(nodesOutput)

        for year in y:
            resultFile = prefix + str(year) + suffix;
            ref = fileRef[resultFile];
            authorid = str(dictAuthors[a])
            affiliation = ""

            if a in dictAuthorAffiliation:
                affiliation = dictAuthorAffiliation[a]

            output = write_template.format(authorid, str(a.encode('utf-8'), 'utf-8'), str(affiliation.encode('utf-8'), 'utf-8'))
            ref.write(output);

    for name, file in fileRef.items():
        file.close();

def writeRecordsEdges():
    global minYear;
    global maxYear;
    prefix = './results/edges/edges';
    suffix = '-01.txt';

    #creating the edges files
    for year in range(minYear, maxYear + 1):
        for x in range(1, 13):
                output = prefix + str(year) + '-' + "{0:0=2d}".format(x) + suffix;
                edgesFiles.append(output);
    fileRef = {};

    #open all edges files
    for yearFile in edgesFiles:
        try:
            os.remove(yearFile);
        except OSError:
            pass;

        ref = open(yearFile, 'a', encoding='utf-8');
        fileRef.update({yearFile : ref});

    for authKey,y in dictEdges.items():
        for year in y:
            resultFile = prefix + str(year) + suffix;
            ref = fileRef[resultFile];
            ref.write(authKey + "\n");

    for name, file in fileRef.items():
        file.close();

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
            else:
                author = auth[0].text;

            year = int(pubYear.text.split('-')[0])
            yearWithMonth =  pubYear.text.split('-')[0] + "-" + pubYear.text.split('-')[1]
            if(year < minYear):
                minYear = year
            elif(year > maxYear):
                maxYear = year

            if not author in dictAuthors: # check if author record already exists
                # print(str(author.encode('utf-8'), 'utf-8'))
                dictAuthors.update({author : idNo});
                dictYears.update({author : [yearWithMonth]});
                idNo += 1;
            else:
                if not yearWithMonth in dictYears[author]:
                    dictYears[author].append(yearWithMonth);

            if affiliation:
                if not author in dictAuthorAffiliation: # check if author record already exists
                    dictAuthorAffiliation.update({author : affiliation});

def processAuthorEdges(authors, pubYear, journalReference):
    if len(authors) < 2: #error checking, return if only one author for a publication
        return;
    global minYear;
    global maxYear;
    global dictAuthors;
    global dictYears;
    global dictEdges;
    index = 1;
    numAuthors = len(authors);
    auth_key_template = "{} {} {}"
    for auth in authors:
        if not ((auth is None) or (pubYear is None)):
            if len(auth) == 2:
                author = auth[1].text + " " + auth[0].text;
            elif len(auth) == 3:
                if "affiliation" in auth[2].tag:
                    author = auth[1].text + " " + auth[0].text;
                else:
                    author = auth[1].text + " " + auth[0].text + " " + auth[2].text;
            else:
                author = auth[0].text;

            year = int(pubYear.text.split('-')[0])
            yearWithMonth =  pubYear.text.split('-')[0] + "-" + pubYear.text.split('-')[1]
            firstAuth = "";
            secondAuth = "";

            if(year < minYear):
                minYear = year
            elif(year > maxYear):
                maxYear = year

            for num in range(index, numAuthors): #iterate through all co authors
                if len(authors[num]) == 2:
                    coAuthor = authors[num][1].text + " " + authors[num][0].text;
                elif len(authors[num]) == 3:
                    if "affiliation" in authors[num][2].tag:
                        coAuthor = authors[num][1].text + " " + authors[num][0].text;
                    else:
                        coAuthor = authors[num][1].text + " " + authors[num][0].text + " " + authors[num][2].text;
                else:
                    coAuthor = authors[num][0].text;

                if(author > coAuthor): #auth comes behind alphabetically
                    firstAuth = coAuthor;
                    secondAuth = author;
                else:
                    firstAuth = author;
                    secondAuth = coAuthor;

                journalRef = ''
                if (journalReference is None):
                    journalRef = ''
                else:
                    journalRef = journalReference.text

                authKey = auth_key_template.format(dictAuthors[firstAuth], dictAuthors[secondAuth], str(journalRef.encode('utf-8'), 'utf-8').replace("\n", ""))

                if not authKey in dictEdges: # check if edge record already exists
                    dictEdges.update({authKey : [yearWithMonth]});
                else:
                    if not yearWithMonth in dictEdges[authKey]: # prevent duplicate publication years
                        dictEdges[authKey].append(yearWithMonth); #append year to publication list
        index = index + 1;

def parseResults(parseString):
    root = ET.fromstring(parseString)
    records = root.iter("{http://arxiv.org/OAI/arXiv/}arXiv")

    for record in records:
        authors = record.find('{http://arxiv.org/OAI/arXiv/}authors');
        pubYear = record.find('{http://arxiv.org/OAI/arXiv/}created');
        processAuthorNodes(authors, pubYear);

    records = root.iter("{http://arxiv.org/OAI/arXiv/}arXiv")
    for record in records:
        authors = record.find('{http://arxiv.org/OAI/arXiv/}authors');
        pubYear = record.find('{http://arxiv.org/OAI/arXiv/}created');
        journalReference = record.find('{http://arxiv.org/OAI/arXiv/}journal-ref');
        processAuthorEdges(authors, pubYear, journalReference);

if __name__ == "__main__":
    main()