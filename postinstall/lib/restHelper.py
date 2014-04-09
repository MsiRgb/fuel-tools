#!/usr/bin/env python

import urllib
#import urllib2
import json
import requests
from exceptions import Exception

class RestHelper():
  def __init__(self):
    pass
  
  def putRequest(self, url, data):
    encodedData = json.dumps(data)
    retVal = requests.put(url, data=encodedData)
    if retVal.status_code == 400:
      raise Exception("Error: Invalid data supplied! %s" % (data))
    elif retVal.status_code < 200 or retVal.status_code > 300:
      raise Exception("Unknown error creating environment: %s" % (data['name']))
    try:
      return retVal.json()
    except:
      return None      
  
  def postRequest(self, url, data):
    encodedData = json.dumps(data)
    retVal = requests.post(url, data=encodedData)
    if retVal.status_code == 400:
      raise Exception("Error: Invalid data supplied! %s" % (data))
    elif retVal.status_code == 409:
      raise Exception("Error: Environment %s already exists!" % (data['name']))
    elif retVal.status_code < 200 or retVal.status_code > 300:
      raise Exception("Unknown error creating environment: %s" % (data['name']))
    try:
      return retVal.json()
    except:
      return None          
  
  def deleteRequest(self, url, data={}):
    encodedData = json.dumps(data)
    retVal = requests.delete(url, data=encodedData)
    if retVal.status_code == 400:
      raise Exception("Error: Failed to execute cluster deletion process")
    elif retVal.status_code == 404:
      raise Exception("Error: Cluster not found in db")
    elif retVal.status_code < 200 or retVal.status_code > 300:
      raise Exception("Unknown error deleting environment: %s" % (data['name']))
    return retVal.json()

  
  def getRequest(self, url, data={}):
    return requests.get(url).json()
  
if __name__ == "__main__":
  import os
  print "Testing %s" % os.path.basename(__file__)
  classInstance = RestHelper()
  
  # Test connection to fuel server
  fuelUrl = "http://10.20.0.2:8000/api/v1"
  
  # Get list of environments
  # curl -i -H "Accept: application/json" -X GET http://10.20.0.2:8000/api/v1/clusters
  print "Looking for Fuel environments..."
  for env in classInstance.getRequest("%s/%s" % (fuelUrl, "clusters/")):
    print "Found environment: %s" % env 
  
  # Create a new environment
  print "Creating a new Fuel environment..."
  createEnvData = {
                    "nodes": [],
                    "tasks": [],
                    "name": "restHelper test env",
                    "release": 2
                  }
  createEnv = classInstance.postRequest("%s/%s" % (fuelUrl, "clusters/"), createEnvData)
  print "createEnv Response: %s" % (createEnv)
  
  # Delete the new environment
  print "Deleting newly created test env..."
  envToDeleteId = createEnv['id']
  deleteUrl = "%s/%s/%s/" % (fuelUrl, "clusters", envToDeleteId)
  print "Deleted environment: %s" % classInstance.deleteRequest(deleteUrl)
  
  