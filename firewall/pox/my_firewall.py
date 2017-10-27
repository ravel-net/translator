# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Gives a GUI for blocking individual IP addresses.

Meant to work with reactive components like l2_learning or l2_pairs.

Start with --no-clear-tables if you don't want to clear tables on changes.
"""

from pox.core import core
from pox.lib.revent import EventHalt
from pox.lib.addresses import IPAddr
import pox.lib.packet as pkt
import pox.openflow.libopenflow_01 as of
import threading


class MyFirewall(object):
    def __init__(self):
        # Initialize the firewall
        print "initializing firewall"
        # a set of blocked IP pairs
        self.firewall = {}

        # If True, clear tables on every block/unblock
        self.clear_tables_on_change = True

        self.eventID = None

    def AddRule(self, ip1, ip2):
        if (ip1, ip2) in self.firewall:
            print "Firewall rule for %s: %s already exists" % (ip1, ip2)
            return
        self.firewall[(ip1, ip2)] = True
        print "Adding firewall rule in %s: %s" % (ip1, ip2)

    def DeleteRule(self, ip1, ip2):
        try:
            del self.firewall[(ip1, ip2)]
            print "Deleting firewall rule in %s: %s" % (ip1, ip2)
        except:
            pass

    def _handle_PacketIn(self, event):
        # Note the two IPs
        packet = event.parsed
        ip = packet.find('ipv4')
        if ip is None:
            print "received non-ip packet!"
            return
        # Check for blocked IPs
        if (str(ip.srcip), str(ip.dstip)) in self.firewall:
            return EventHalt

    def ui_loop(self):
        while(True):
            nb = raw_input('(b)lock, (a)llow, or (r)return? ')
            if nb == 'b':
                try:
                    nb = raw_input('enter IP address pair ')
                    (str1, str2) = nb.split(',')
                    (ip1, ip2) = (IPAddr(str1), IPAddr(str2))
                    self.AddRule(str(ip1), str(ip2))
                except:
                    print "Invalid Format"
            elif nb == 'a':
                try:
                    nb = raw_input('enter IP address pair ')
                    (str1, str2) = nb.split(',')
                    (ip1, ip2) = (IPAddr(str1), IPAddr(str2))
                    self.DeleteRule(str(ip1), str(ip2))
                except:
                    print "Invalid Format"
            elif nb == 'r':
                return
            else:
                print "Invalid option"

    def on(self):
        if self.eventID is not None:
            print "Firewall is already on!"
            return
        self.eventID = core.openflow.addListeners(self, priority=1)
        self.eventID = self.eventID[0][1]

    def off(self):
        if self.eventID is None:
            print "Firewall is already off!"
            return
        core.openflow.removeListener(self.eventID)
        self.eventID = None

class MyHub (object):
    def __init__(self):
        print "initializing hub..."
        self.eventID = None
    
    def _handle_PacketIn(self, event):
        """
        Handle packet in messages from the switch, ask the switch to flood the packet.
        """
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.in_port = event.port
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)

    def on(self):
        if self.eventID is not None:
            print "Hub is already on!"
            return
        self.eventID = core.openflow.addListeners(self)
        self.eventID = self.eventID[0][1]

    def off(self):
        if self.eventID is None:
            print "FiHubrewall is already off!"
            return
        core.openflow.removeListener(self.eventID)
        self.eventID = None

class SimpleController(object):
    def __init__(self):
        print "Initializing controller..."
        self.fwon = False
        self.ui = threading.Thread(target=self.ui_loop)
        self.ui.daemon = True
        self.ui.start()

    def ui_loop (self):
        while(True):
            nb = raw_input('(fwon)turn on firewall, (fwoff)turn off firewall, (mngfw)manage firewall, (hubon)turn on hub, (huboff)turn off hub or (q)uit? ')
            if nb == 'fwon':
                core.MyFirewall.on()
            elif nb == 'fwoff':
                core.MyFirewall.off()
            elif nb == 'mngfw':
                core.MyFirewall.ui_loop()
            elif nb == 'hubon':
                core.MyHub.on()
            elif nb == 'huboff':
                core.MyHub.off()
            elif nb == 'q':
                print "Quitting"
                import os, signal
                os.kill(os.getpid(), signal.SIGINT)
                return
            else:
                print "Invalid option"

def launch():
    core.registerNew(MyFirewall)
    core.registerNew(MyHub)
    core.registerNew(SimpleController)

