#!/usr/bin/env python

import libvirt
import libxml2
from libvirt import VIR_DOMAIN_RUNNING

class LibvirtInterface():
  CONN_STR = "qemu:///system"
    
  def __init__(self, connStr=CONN_STR):
    self._connStr = connStr
    self._connection = self.makeConnection(self._connStr)
  
  def makeConnection(self, connStr):
    return libvirt.open(connStr) 
  
  def getVmListById(self):
    return self._connection.listDomainsID()
  
  def getVmIdByMacAddr(self, macAddr):
    for vmId in self.getVmListById():
      ctx = libxml2.parseDoc(self._connection.lookupByID(vmId).XMLDesc(0)).xpathNewContext()
      devList = ctx.xpathEval("/domain/devices/interface[@type='network']/mac/@address")
      for dev in devList:
        if macAddr == dev.content:
          return vmId
    return None
  
  def getVmIdByIpAddr(self, ipAddr):
    for vmId in self.getVmListById():
      ctx = libxml2.parseDoc(self._connection.lookupByID(vmId).XMLDesc(0)).xpathNewContext()
      devList = ctx.xpathEval("/domain/devices/interface[@type='network']/ip/@address")
      for dev in devList:
        if ipAddr == dev.content:
          return vmId
    return None
  
  def getVmIdByName(self, name):
    for vmId in self.getVmListById():
      ctx = libxml2.parseDoc(self._connection.lookupByID(vmId).XMLDesc(0)).xpathNewContext()
      nameList = ctx.xpathEval("/domain/name")
      for nameitem in nameList:
        if name == nameitem.content:
          return vmId
    return None
  
  def getVmNameById(self, idIn):
    for vmId in self.getVmListById():
      ctx = libxml2.parseDoc(self._connection.lookupByID(vmId).XMLDesc(0)).xpathNewContext()
      idList = ctx.xpathEval("/domain/name")
      if idIn == vmId:
        return idList[0].content
    return None
  
  def getRunningStatusByVmId(self, vmId):
    state = self._connection.lookupByID(vmId).info()[0]
    return state # VIR_DOMAIN_RUNNING
  
  def getRunningStatusByVmName(self, vmName):
    vmId = self.getVmIdByName(vmName)
    if not vmId:
      return None
    return self.getRunningStatusByVmId(vmId)
  
  def getVmNameList(self):
    self.getVmListById()
  
if __name__ == "__main__":
  import os
  print "Testing %s" % os.path.basename(__file__)
  classInstance = LibvirtInterface()
  print "getVmIdByMacAddr(52:54:00:58:78:cd): %s" % classInstance.getVmIdByMacAddr("52:54:00:58:78:cd")
  print "getVmIdByIpAddr(192.168.199.1): %s" % classInstance.getVmIdByIpAddr("192.168.199.1")
  print "getVmIdByName(test1): %s" % classInstance.getVmIdByName("test1")
  print "getVmIdByName(test2): %s" % classInstance.getVmIdByName("test2")
  print "getVmNameById(2): %s" % classInstance.getVmNameById(2)
  print "getRunningStatusByVmName(test1): %s" % classInstance.getRunningStatusByVmName('test1')
  