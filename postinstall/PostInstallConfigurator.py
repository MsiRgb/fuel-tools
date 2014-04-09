#!/usr/bin/env python

from lib.fuelConfig import FuelConfig
import argparse
import logging
from lib.fuelInterface import FuelInterface
from lib.libvirtInterface import LibvirtInterface
from time import sleep

class PostInstallConfigurator():
  def __init__(self):
    self._args = None
    self.loadArgs()
    self._fuelConfig = FuelConfig(self._args["config"])
    self._fuelInterface = FuelInterface(self._fuelConfig.getFuelServerApiUrl())
    self._libvirtInterface = LibvirtInterface(vmCreateTmplFile="lib/templates/create_vm.xml")
    logging.debug("PostInstallConfigurator starting...")
    # Place to store created VM parms
    self._vmParms = {}

  def loadArgs(self):
    parser = argparse.ArgumentParser(description='Post Install Configurator for Fuel')
    parser.add_argument('-c','--config', 
                        help='YAML config file', 
                        default="/var/tmp/postinstall/fuelConfigurator.yml")
    parser.add_argument('-l','--log-file', 
                        help='Log file', 
                        default="/var/log/postinstall.log")
    parser.add_argument('-d','--debug-level',
                        help='Log level (DEBUG,INFO,WARNING,ERROR,CRITICAL)', 
                        default=logging.INFO)
    parser.add_argument('-x','--delete-existing-envs',
                        help='Deletes existing environments to create new (DESTRUCTIVE)',
                        action='store_true',
                        default=False)
    self._args = vars(parser.parse_args())
    # Configure logging
    numeric_level = getattr(logging, self._args["debug_level"].upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % self._args["debug_level"])
    logging.basicConfig(level=self._args["debug_level"], 
                        filename=self._args["log_file"],
                        format="%(asctime)s %(process)s %(name)s %(levelname)s: %(message)s")
  
  def getNodeIdByVmName(self, vmName):
    ''' Returns a fuel node id based on a libvirt created vm name '''
    # rc['nics'][0]['mac']
    macList = []
    vmParm = self._vmParms.get(vmName, None)
    if vmParm:
      for nic in vmParm['nics']:
        macList.append(nic['mac'])
      # Get a list of fuel nodes to search out this mac
      for fuelNode in self._fuelInterface.getUnallocatedNodes():
        if fuelNode['mac'] in macList:
          return fuelNode['id']
    return None

  def run(self):
    pass
    # Load the config file
    envList = self._fuelConfig.getEnvList()
    vmList = self._fuelConfig.getVmList()
    
    # For each enviornment, add the env in Fuel
    for env in envList:
      if self._args['delete_existing_envs']:
        for currEnv in self._fuelInterface.listEnvs():
          if currEnv['name'] == env['name']:
            self._fuelInterface.deleteEnv(currEnv['id'])
      self._fuelInterface.createEnvironment(env['name'],
                                            env['release'], 
                                            env['mode'],
                                            env['net-provider'], 
                                            env['net-segment-type'])
    
    # For each VM, create the VM (note: this is only for AIO)
    # Note: If the VM is pre-configured as a node, add it to the env
    for vm in self._fuelConfig.getVmList():
      self._vmParms[vm['name']] = self._libvirtInterface.createVm(vm['name'], type=vm['type'], nics=vm['nics'])
      
    # Wait for all nodes to check in
    allNodesCheckedIn = False
    while not allNodesCheckedIn:
      sleep(5)
      checkedInNodes = 0
      for vm in vmList:
        if self.getNodeIdByVmName(vm['name']):
          checkedInNodes += 1
      logging.info("Waiting for nodes to check in (%s/%s)" % (checkedInNodes, len(vmList)))
      allNodesCheckedIn = checkedInNodes >= len(vmList)
    
    # For each VM, add primary MAC address as a new node to env
    for env in envList:
      for node in env['nodes']:
        nodeId = pic.getNodeIdByVmName(node['name'])
        roles = node['roles']
        envId = self._fuelInterface.getEnvIdByName(env['name'])
        self._fuelInterface.addNodeToEnvWithRole(nodeId, roles, envId)
    
if __name__ == "__main__":
  pic = PostInstallConfigurator()
  pic.run()
  