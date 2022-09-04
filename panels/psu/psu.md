# PSU

The original PSU I built for my Serge panels was the [MFOS wall wart PSU from Soundtronics](https://www.soundtronics.co.uk/mfos-wall-wart-power-supply/) which it turns out didn't have the grunt for two panels.

After a bit of research, it turned out that the Koma Strom PSU has a Molex connector on the back to use for connecting it to bus boards.

Alternatively, you can build a cable with the correct Molex connector that then connects it to a bunch of power connectors for Serge panels.

## Components

* Koma Strom PSU
* Power distribution
* Format Jumbler
* Synth to Line level buffer
* Headphone output

## Measurements

### Strom PCB

The Strom PCB measures 110mm by 20mm and requires 55mm of depth below the panel.

Distances from top of PCB

3.5mm (and 3.5mm from right) - m3 screw
7mm to 17mm                  - Molex PSU socket (needs cutout for catch)
36mm                         - +12v LED
51mm                         - +5v LED
66mm                         - -12v LED
82mm                         - power switch (TODO what size is the hole)
100mm                        - power socket (TODO what size is the hole)

### Sockets

MIC power sockets
https://uk.farnell.com/pro-signal/psg01593/plug-multipole-panel-4way/dp/1280759

15.875mm radius but 14.6mm flattened sides
