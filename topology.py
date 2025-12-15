#!/usr/bin/env python
"""
Mininet Topology Script
Creates a network with 4 hosts and 3 switches
Topology:
    h1 --- s1 --- s2 --- h3
           |      |
           h2     s3
                  |
                  h4
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class CustomTopology(Topo):
    """Custom topology with 4 hosts and 3 switches"""
    
    def build(self):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        
        # Add links
        # Connect hosts to switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        
        # Connect switches together
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s3)

def run():
    """Start the network"""
    topo = CustomTopology()
    
    # Create network with remote controller (Ryu)
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6653),
        autoSetMacs=True
    )
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Network configuration:\n')
    for host in net.hosts:
        info(f'{host.name}: IP={host.IP()} MAC={host.MAC()}\n')
    
    info('*** Running CLI\n')
    info('*** Use "pingall" to test connectivity\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
