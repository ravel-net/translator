################################################################################
# The Pyretic Project                                                          #
# frenetic-lang.org/pyretic                                                    #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Joshua Reich  (jreich@cs.princeton.edu)                              #
################################################################################

from pox.lib.addresses import EthAddr

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import mac_learner
import threading

class firewall(DynamicPolicy):

    def __init__(self):
        # Initialize the firewall
        print "initializing firewall"      
        self.firewall = {}
        super(firewall,self).__init__(true)

    def AddRule (self, ip1, ip2):
        if (ip1, ip2) in self.firewall:
            print "Firewall rule for %s: %s already exists" % (ip1, ip2) 
            return
        self.firewall[(ip1, ip2)]=True
        print "Adding firewall rule in %s: %s" % (ip1, ip2) 
        self.update_policy()
    
    def DeleteRule (self, ip1, ip2):
        try:
            del self.firewall[(ip1, ip2)]
            print "Deleting firewall rule in %s: %s" % (ip1, ip2) 
            self.update_policy()
        except:
            pass
        try:
            del self.firewall[(ip1, ip2)]
            print "Deleting firewall rule in %s: %s" % (ip1, ip2) 
            self.update_policy()
        except:
            pass

    def update_policy (self):
        self.policy = ~union([ (match(srcip=ip1) & 
                                match(dstip=ip2)) |
                               (match(dstip=ip1) & 
                                match(srcip=ip2)) 
                               for (ip1, ip2) 
                               in self.firewall.keys()])
        print self.policy

    def ui_loop (self):
        while(True):
            nb = raw_input('(b)lock, (a)llow, or (r)return? ')
            if nb == 'b':
                try:
                    nb = raw_input('enter IP address pair ')
                    (str1,str2) = nb.split(',')
                    (ip1, ip2) = (IP(str1),IP(str2))
                    self.AddRule(ip1, ip2)
                except:
                    print "Invalid Format"
            elif nb == 'a':
                try:
                    nb = raw_input('enter IP address pair ')
                    (str1,str2) = nb.split(',')
                    (ip1, ip2) = (IP(str1),IP(str2))
                    self.DeleteRule(ip1, ip2)
                except:
                    print "Invalid Format"
            elif nb == 'r':
                return
            else:
                print "Invalid option"

def hub():
    return flood()

class simple_controller(DynamicPolicy):
    def __init__(self):
        print "Initializing controller..."
        super(simple_controller,self).__init__(true)
        self.policy = identity
        self.fwon = False
        self.fw = firewall()
        self.hubon = False
        self.ui = threading.Thread(target=self.ui_loop)
        self.ui.daemon = True
        self.ui.start()
    def ui_loop (self):
        while(True):
            nb = raw_input('(fwon)turn on firewall, (fwoff)turn off firewall, (mngfw)manage firewall, (hubon)turn on hub, (huboff)turn off hub or (q)uit? ')
            if nb == 'fwon':
                if self.fwon:
                    print "Firewall is already on."
                else:
                    self.fwon = True
                    self.update_policy()
            elif nb == 'fwoff':
                if not self.fwon:
                    print "Firewall is already off."
                else:
                    self.fwon = False
                    self.update_policy()
            elif nb == 'mngfw':
                self.fw.ui_loop()
                self.update_policy()
            elif nb == 'hubon':
                if self.hubon:
                    print "Hub is already on!"
                    return
                self.hubon = True
                self.update_policy()
            elif nb == 'huboff':
                if not self.hubon:
                    print "Hub is already off!"
                    return
                self.hubon = False
                self.update_policy()
            elif nb == 'q':
                print "Quitting"
                import os, signal
                os.kill(os.getpid(), signal.SIGINT)
                return
            else:
                print "Invalid option"

    def update_policy(self):
        if self.fwon and self.hubon:
            self.policy = self.fw.policy >> hub()
        elif self.fwon and not self.hubon:
            self.policy = self.fw.policy
        elif not self.fwon and self.hubon:
            self.policy = hub()
        else:
            self.policy = identity
        print self.policy
def main ():
    return simple_controller()
