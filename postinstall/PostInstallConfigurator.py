#!/usr/bin/env python

from lib.fuelConfig import FuelConfig

class PostInstallConfigurator():
  def __init__(self):
    self._yamlConfigFile = "/var/tmp/postinstall/fuelConfigurator.yml"
    self._fuelConfig = FuelConfig(self._yamlConfigFile)
    
  def run(self):
    pass
    
if __name__ == "__main__":
  pic = PostInstallConfigurator()
  pic.run()