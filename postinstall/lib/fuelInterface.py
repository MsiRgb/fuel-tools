#!/usr/bin/env python

from subprocess import call
from lib.restHelper import RestHelper

class FuelInterface():
  def __init__(self, fuelBaseUrl="http://10.20.0.2:8000/api/v1"):
    self._restHelper = RestHelper()
    self._fuelBaseUrl = fuelBaseUrl
  
  # mode is either ha_compact or multinode
  # netMode is either nova_network or neutron
  # netSegType is either gre or vlan
  def createEnvironment(self, envName, rel, mode, netMode, netSegType):
    createEnvData = {
                      "nodes": [],
                      "tasks": [],
                      "name": envName,
                      "release": rel,
                      "net_provider": netMode,
                      "net_segment_type": netSegType,
                      "mode": mode
                    }
    createEnv = self._restHelper.postRequest("%s/%s" % (self._fuelBaseUrl, 
                                                        "clusters/"), 
                                                        createEnvData)
    return createEnv
  
  def listEnvs(self):
    return self._restHelper.getRequest("%s/%s" % (self._fuelBaseUrl, "clusters/"))
  
  def deleteEnv(self, envId):
    deleteUrl = "%s/%s/%s/" % (self._fuelBaseUrl, "clusters", envId)
    self._restHelper.deleteRequest(deleteUrl)  
    
if __name__ == "__main__":
  import os
  print "Testing %s" % os.path.basename(__file__)
  classInstance = FuelInterface()
  print "Listing envs..."
  print classInstance.listEnvs()
  print "...done"
  print "Creating new env..."
  newEnv = classInstance.createEnvironment("fuelInterface test env 1", 2, "multinode", "nova_network", "gre")
  print newEnv
  print "...done"
  print "Deleting env..."
  classInstance.deleteEnv(newEnv['id'])
  print "...done"