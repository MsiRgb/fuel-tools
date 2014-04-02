#!/bin/bash 

####################################################################################
# This script will spin up a very simple OpenStack HA environment using the Fuel CLI
#   note: The user does NOT have control over which slave nodes become 
#         which service nodes will be consumed on a first-come first-serve 
#         basis in the following order:
#           1) controllers
#           2) compute
#           3) cinder
#
#   note: The user may specify the number of each below
#
# Author: Wes Parish
# Date:   04/02/2014
####################################################################################

#### Configure Here ####
controllerNodes=3
computeNodes=2
cinderNodes=1
#### Stop Configuring! ####

# Compute required nodes
requiredNodes=$(expr $controllerNodes + $computeNodes + $cinderNodes)

check_available_nodes()
{
  availNodes=$(fuel node | egrep '^[0-99]' | grep None | cut -d '|' -f 1 | sort -n | wc -l)
  if [[ "${availNodes}" -ge "${requiredNodes}" ]]; then return 1; else return 0; fi
}

get_next_discovered_node()
{
  nextNode=$(fuel node | egrep '^[0-99]' | grep None | cut -d '|' -f 1 | sort -n | head -1)
  return $nextNode
}

# Error if we don't have enough nodes
if check_available_nodes; then echo "Not enough nodes to proceed! Check in more nodes to fuel server (${availNodes}/${requiredNodes})" && exit 1; fi

envName="scriptenv_$(date +%s)"

fuel env create --name ${envName} --rel 2 --mode ha --network-mode neutron --net-segment-type vlan

# Get env id
envId=$(fuel env | egrep '^[0-99]' | grep ${envName} | cut -d '|' -f 1)

# Add controller nodes
for (( i=0; i<${controllerNodes}; i++ )); do
  get_next_discovered_node
  fuel --env $envId node set --node $? --role controller
done

# Add compute nodes
for (( i=0; i<${computeNodes}; i++ )); do
  get_next_discovered_node
  fuel --env $envId node set --node $? --role compute
done

# Add cinder nodes
for (( i=0; i<${cinderNodes}; i++ )); do
  get_next_discovered_node
  fuel --env $envId node set --node $? --role cinder
done

echo "Finished!"

