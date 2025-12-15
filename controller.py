#!/usr/bin/env python3
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
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, icmp, tcp, arp

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

        # Install table-miss flow entry (send unknown packets to controller)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        # Install ICMP drop rule for h1 immediately
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
        eth = pkt.get_protocol(ethernet.ethernet)

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

        # Parse packet for special rules
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        arp_pkt = pkt.get_protocol(arp.arp)
        
        # Always allow ARP (for address resolution)
        if arp_pkt:
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                       in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
            return
        
        # Rule 1: Drop ICMP from h1 (should be caught by flow rule, but double-check)
        if ip_pkt and icmp_pkt and ip_pkt.src == self.h1_ip:
            self.logger.info(f"Blocking ICMP from h1 on switch {dpid}")
            return  # Drop packet
        
        # Rule 2: Handle TCP traffic from h2 to h3
        if ip_pkt and tcp_pkt and ip_pkt.src == self.h2_ip and ip_pkt.dst == self.h3_ip:
            self.logger.info(f"TCP h2->h3 on switch {dpid}, installing flow")
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ip_proto=6,  # TCP
                    ipv4_src=self.h2_ip,
                    ipv4_dst=self.h3_ip
                )
                self.add_flow(datapath, 50, match, actions, idle_timeout=120)

        # Rule 3: Handle packets from h4 - modify MAC header
        if src == self.h4_mac and out_port != ofproto.OFPP_FLOOD:
            self.logger.info(f"Modifying h4 packet on switch {dpid}")
            new_mac = '00:00:00:00:00:44'
            actions = [
                parser.OFPActionSetField(eth_src=new_mac),
                parser.OFPActionOutput(out_port)
            ]
            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=self.h4_mac,
                eth_dst=dst
            )
            self.add_flow(datapath, 60, match, actions, idle_timeout=120)

        # Install flow for regular forwarding (learning switch behavior)
        if out_port != ofproto.OFPP_FLOOD and src != self.h4_mac:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 10, match, actions, msg.buffer_id, idle_timeout=120)
                return
            else:
                self.add_flow(datapath, 10, match, actions, idle_timeout=120)

        # Send packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                   in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
