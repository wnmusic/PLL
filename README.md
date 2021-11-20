# PLL
Experiments on PLL 

## Experiment One
Using CD4046. The VCO range is 48.5~50MHz. I use iCEStick as the divider, also because the board has a 12MHz crystal, which could be used as a rough reference.  Suppose the channel frequency is 25kHz, where the crystal freqency need to be divided into. 

Also the RF frequency is amplified by a wideband differential amplifer to provide enough swing to be accept by the FPGA. 
After close the loop, the tuning range drop to 48.5 ~ 49.5MHz. 

The loop is designed to be very narrow, And the final spur is about -55-60dBc. 


