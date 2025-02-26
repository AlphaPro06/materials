import pandas as pd
import requests
import json
import os
import re
import urllib.parse
from requests.auth import HTTPBasicAuth


#filter format: filter name, lower, upper
queryString = "SELECT * FROM material_science"
filter = []
json_response = {}

class FilterCondition:

    def __init__(self, attribute):
        """A filter condition"""
        self.attribute = attribute

    def toSQL(self):
        raise NotImplementedError("")

class RangeCondition(FilterCondition):

    def __init__(self, attribute, lower, upper):
        self.attribute = attribute
        self.lower = lower
        self.upper = upper

    def toSQL(self):
        return self.attribute + " BETWEEN " + self.lower +" AND " +self.upper

def filtersToWhere(filters):
    return " AND ".join([f.toSQL() for f in filters])

def stringToRangeCondition(attribute, lower, upper):
    if not (is_number(lower) and is_number(upper) and isIdentifier(attribute)):
        #breaks the website
        #try something other than exception?
        #maybe on front end, check for input validity and bring in an alert instead of breaking on the backend
        print("yikessssssssssssssssssssssss")
        raise Exception("only numbers allowed as inputs for conditions")
    return RangeCondition(attribute, lower, upper)

def isIdentifier(s):
    if re.compile("[A-Za-z_]").match(s):
        return True
    return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getCache(cache):
    print(" from make cache ", cache)
    global filter
    filter = cache

def returnResponse():
    # print("###########################################################", filter)

    queryString = makeQuery(filter)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print(queryString)
    workflow_url = 'https://demo.vizierdb.info/vizier-db/api/v1/projects/1/branches/1/head/sql?query='
    query = queryString
    #url = 'https://demo.vizierdb.info/auth/public?workflow-url=' +
    url = workflow_url + query#urllib.parse.quote(urllib.parse.quote(query))
    print(url)
    response = requests.get(url, auth=HTTPBasicAuth('mimir', 'jormugundir'))
    print(response)
    # resp1 = requests.post(url)
    # print(resp1)
    resp = response.json()
    print("+______________________+")
    #print(resp)
    print("++++++++++++++++++++++++++++++")
    return resp


def outputTable():
    # print("~~~~~~~~~~~~~~~@@@@@@@@@@@@@@@@@@@@@@@@@@@@@~~~~~~~~~~~~~~~~~~~~~~")
    # print(filter)
    # queryString = makeQuery(filter)
    # print(queryString)
    # response = requests.post('http://localhost:8089/api/v2/query/data', data = json.dumps({ 'query' : queryString, 'includeUncertainty' : True }))
    global json_response
    # #json_response = {}
    json_response = returnResponse()
    # requests.post('https://localhost:8050/get', data = json_response)
    #print("wiat what huhhhhhhhhhhhhhhhhhhhh ")
    #print(json_response)
    cols = []
    rows = []
    #col names:
    counter = -1
    print(json_response)
    for col in json_response['schema']:
        cols.append(col['name'])
    for row in json_response['data']:
        counter+=1
        rows.append(row)
        #print(row, "\n", counter)
    dataTable = pd.DataFrame(rows, columns=cols)
    #print("bruvvvvvvvvvv why???")
    #learn to process variable sql queries
    #then query the database...
    return dataTable

def getBoolData():
    print(queryString)
    boolean= json_response['colTaint']
    boolean[0] = [False, True, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    boolean[1] = [True, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    boolData = []
    boolRow = []
    index = -1
    for i in boolean:
        for j in i:
            index +=1
            if j:
                boolRow.append(index)
        if (len(boolRow) > 0):
            boolData.append(boolRow)
        boolRow = []
        index = -1
    #print(boolData)
    if (len(boolData) < 1):
        return ["%"]
    return boolData

#

def makeQuery(filters):
    #assuming queries is a list of lists
    query = queryString
    addOn = ""
    chunks= []
    filterNum = len(filters)
    if (filterNum > 0):
        query = queryString + " WHERE "
    else:
        return query
    for filterString in filters:
        print("from makeTAble filter stuff")
        print(filterString)
        filter = filterString.strip().split(',')
        if (len(filter) > 2 and filter[0]!= "undefined" and filter[1] != "undefined" and filter[2] != "undefined"):
            addOn = stringToRangeCondition(filter[0], filter[1], filter[2])
            chunks.append(addOn)
        else:
            continue
    return query + filtersToWhere(chunks)

if __name__ == "__main__":
    main()
