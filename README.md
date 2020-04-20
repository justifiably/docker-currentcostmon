# A simple CurrentCost monitor running in Docker with MQTT output

This is a Python interface to the CurrentCost energy monitoring
devices connected on a serial port.  Code borrowed/inspired from
other similar ancient hacks.

Can log to several different kinds of file, as well as an MQTT broker.

Default is to print readings on stdout:

   docker run -ti --device /dev/ttyUSB0:/dev/ttyUSB0 justifiably/currentcostmon

See full usage with:
 
	docker run justifiably/currentcostmon -h

## Pointers

* [Current Cost Envi](http://www.currentcost.com/product-envi.html)
* [Current Cost EnviR](http://www.currentcost.com/product-envir.html)

Other projects:

* <https://github.com/waveform80/currentcost> much better than mine,
  without XML parsing overkill
* <https://github.com/robrighter/node-currentcost> if JS is your thing
  (has useful documentation of format)
