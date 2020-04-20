FROM justifiably/python3

COPY currentcost.py currentcostlib.py /usr/local/bin/

RUN pip install pyserial paho-mqtt && \
    chmod u+x /usr/local/bin/currentcost.py && \
    ln -s /usr/bin/python3 /usr/bin/python

ENTRYPOINT ["/usr/local/bin/currentcost.py"]
CMD ["--help"]
