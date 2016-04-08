The data from arxiv has been downloaded in the xml folder. The arxiv api only provided 100,000 results at a time so we had to download around 100 xml files.

To parse the data, use parseByMonths or parseByYearFiles. The program reads the xml files and outputs to the results folder. The output includes nodes, edges and the dictionary of the authors.