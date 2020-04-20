FROM justifiably/python3

RUN pip install pyserial paho-mqtt

ADD currentcost.py /usr/local/bin
ADD currentcostlib.py /usr/local/bin
RUN chmod u+x /usr/local/bin/currentcost.py
RUN ln -s /usr/bin/python3 /usr/bin/python

ENTRYPOINT ["/usr/local/bin/currentcost.py"]
CMD ["-o"]
