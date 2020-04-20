# XML lib
import xml.dom.minidom as minidom
from time import time,strftime,localtime

# MQTT lib
import paho.mqtt.publish as publish


class Packet:
    """
    XML packet
    """
    def __init__(self, source):
        """Gets an XML packet from the serial connection and parses it"""

        # This just waits until the XML comes through
        self.xml = {}
        self.xml['text'] = source.readline()
        self.xml['dom'] = minidom.parseString(self.xml['text'])

        # Parse into packet data - element names are unique in child nodes
        self.parse_data()

    def parse_data(self):
        """Parse XML data into a set of dicts, and pull out relevant data"""

        msg = self.xml['dom'].childNodes[0]
        self.data = xml_to_dicts(msg, False)

        # Get some metadata together
#        self.id = "%s:%s" % (self.data['src']['name']['#cdata'], self.data['src']['id']['#cdata'])
        # ID is meter firmware version and serial number identifier.
        self.id = "%s:%s" % (self.data['src']['#cdata'],
                             self.data['id']['#cdata'])
        self.temp = self.data['tmpr']['#cdata']
        self.watts = int(self.data['ch1']['watts']['#cdata'])
        # Time - CurrentCost DSB="days since birth" reset time 
        self.cctime = '%dDSB-%s' % (int(self.data['dsb']['#cdata']),
                                  self.data['time']['#cdata'])
        self.time = time()


    def logstring(self):
        # Write: local time | CurrentCost "time" | id | temp/C | power/W 
        timeformat="%d %b %Y %H:%M:%S"
        time=strftime(timeformat,localtime(self.time))
        return '{0}\t{1}\t{2}\t{3}\t{4}'.format(
            time, self.id, self.cctime, self.temp, self.watts)
              
    def log(self,logdir):
        """Write single-line plain-text logfile"""
        f = open(logdir + 'parsed.log', 'a')
        try:
            f.write(self.logstring() + "\n")
        finally:
            f.close()

    def log_stdout(self):
        print (self.logstring())

    def log_raw(self,logdir):
        """Log raw data"""
        f = open(logdir + 'raw.txt', 'a')
        try:
            f.write(self.xml['text'])
        finally:
            f.close()

    def log_influx(self,logdir):
        """Write influxdb points"""
        f = open(logdir + 'influx.log', 'a')
        try:
            # Write: local time | CurrentCost "time" | id | temp/C | power/W 
            f.write("current_cost_watts,device=%s,cctime=%s temp=%s watts=%s %d000000000\n"
                    % (self.id, self.cctime, self.temp, self.watts, self.time))
        finally:
            f.close()

    def mqtt_publish(self,topic,hostname,port,auth,tls):
        msgs=[(topic + "/ccmonitortime", self.cctime, 0, True),
              (topic + "/temperature", self.temp, 0, True),
              (topic + "/watts", self.watts, 0, True)]
        # with multiple currentcosts/devices would be better to include id in topic
        publish.multiple(msgs, hostname=hostname,port=port,
                         client_id="CurrentCost "+self.id,
                         keepalive=60,
                         auth=auth,tls=tls)
            
def xml_to_dicts(xml, cope_with_duplicates=True):
    d = {}
    for n in xml.childNodes:
        try:
            # Tag - parse its child nodes
            k = n.tagName
            dd = xml_to_dicts(n, cope_with_duplicates)
        except AttributeError:
            # Not tag - return text
            k = '#cdata'
            dd = n.wholeText
        if cope_with_duplicates:
            # Use an array to cope with duplicate values
            if not d.has_key(k):
                d[k] = []
            d[k].append(dd)
        else:
            # Just set a direct value
            d[k] = dd
    return d
