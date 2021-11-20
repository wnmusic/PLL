#!/usr/bin/env python3
from pyftdi import spi
from optparse import OptionParser
import sys
import struct



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--pdf", dest="pdf", default=25000,
                      help="Phase detector freqency");

    (options, args) = parser.parse_args()
    if (len(args) < 1):
        print(" should provide RF frequency")
        sys.exit(1)

    f_rf = float(args[0])
    print(f_rf, options.pdf)

    N = int(12e6/options.pdf/2)
    A = int(f_rf/options.pdf/2)
    
    print(N, A)
    ctrl = spi.SpiController()
    ctrl.configure('ftdi://ftdi:2232h/2')
    slave = ctrl.get_port(cs=0, freq=3E6, mode=0)

    val = (N<<16) | (A)
    buf = val.to_bytes(4, byteorder='big')
    print(buf)

    slave.write(buf)
