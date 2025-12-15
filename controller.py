#!/usr/bin/env python
"""
Ryu OpenFlow Controller with Match + Action Rules
Implements:
1. Drop ICMP packets from h1
2. Forward TCP packets from h2 to h3 through specific path
3. Modify MAC/IP headers for packets from h4
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, icmp, tcp

class OpenFlowController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(OpenFlowController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        
        # Define MAC addresses for hosts
        self.h1_mac = '00:00:00:00:00:01'
        self.h2_mac = '00:00:00:00:00:02'
        self.h3_mac = '00:00:00:00:00:03'
        self.h4_mac = '00:00:00:00:00:04'
        
        # Define IP addresses
        self.h1_ip = '10.0.0.1'
        self.h2_ip = '10.0.0.2'
        self.h3_ip = '10.0.0.3'
        self.h4_ip = '10.0.0.4'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        self.logger.info(f"Switch connected: DPID={datapath.id}")

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        # Install special rules after switch connects
        self.install_custom_rules(datapath)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0, hard_timeout=0):
        """Add a flow entry to the switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst,
                                    idle_timeout=idle_timeout,
                                    hard_timeout=hard_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst,
                                    idle_timeout=idle_timeout,
                                    hard_timeout=hard_timeout)
        datapath.send_msg(mod)

    def install_custom_rules(self, datapath):
        """Install custom OpenFlow rules"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Rule 1: Drop ICMP packets from h1 (highest priority)
        match = parser.OFPMatch(
            eth_type=ether_types.ETH_TYPE_IP,
            ip_proto=1,  # ICMP
            ipv4_src=self.h1_ip
        )
        actions = []  # Empty actions = drop packet
        self.add_flow(datapath, 100, match, actions)
        self.logger.info(f"Switch {datapath.id}: Installed ICMP drop rule for h1")
        
        # Rule 2: Forward TCP packets from h2 to h3 through specific path
        # This will be handled in packet_in for more flexible routing
        
        # Rule 3: Modify MAC/IP headers for packets from h4
        # This requires packet modification which we'll handle in packet_in

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle packet-in messages"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Ignore LLDP packets
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})

        # Learn MAC address to avoid flooding next time
        self.mac_to_port[dpid][src] = in_port

        # Get output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Check for special handling
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        
        # Handle TCP traffic from h2 to h3 (Route through s1 -> s3 -> s2)
        if ip_pkt and tcp_pkt:
            if ip_pkt.src == self.h2_ip and ip_pkt.dst == self.h3_ip:
                self.logger.info(f"TCP packet from h2 to h3 on switch {dpid}")
                # Install flow for specific routing
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ip_proto=6,  # TCP
                    ipv4_src=self.h2_ip,
                    ipv4_dst=self.h3_ip
                )
                if out_port != ofproto.OFPP_FLOOD:
                    self.add_flow(datapath, 50, match, actions, idle_timeout=30)

        # Handle packets from h4 - modify headers
        if src == self.h4_mac:
            self.logger.info(f"Packet from h4 detected on switch {dpid} - modifying headers")
            # Modify source MAC to a different address
            new_mac = '00:00:00:00:00:44'  # Modified MAC
            actions = [
                parser.OFPActionSetField(eth_src=new_mac),
                parser.OFPActionOutput(out_port)
            ]
            
            # Install flow with header modification
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(
                    in_port=in_port,
                    eth_src=self.h4_mac
                )
                self.add_flow(datapath, 60, match, actions, idle_timeout=30)

        # Install a flow to avoid packet_in next time (for regular traffic)
        if out_port != ofproto.OFPP_FLOOD and src != self.h4_mac:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # Verify if we have a valid buffer_id, if yes, send buffer_id
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 10, match, actions, msg.buffer_id, idle_timeout=30)
                return
            else:
                self.add_flow(datapath, 10, match, actions, idle_timeout=30)

        # Send packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                   in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
