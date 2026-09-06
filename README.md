# CACHIP (Jinrui) MCU ISP-mode tool
Utility allows on-chip memory manipulation via
exposed in phase0 (ROM) and phase1 (XRAM) boot code functions.


the utility was based on a large research posted here:
[personal blog](https://blog.softdev.online/index.php?controller=post&action=view&id_post=56)


Motivation behind the release of this tool to the public domain is to open 
this fancy very cost-effective micocontroller to be programmed by enthusiasts across 
the whole earth grobe. Patching existing firmwares and providing fresh ones fixing evil bugs. 
So E-Waste will be mimized. at least I want to believe it. Thats a goal.

## To write new firmware
You can use official MCU Manual for SFR/etc descriptions 
and use Keil C51 or any other tool like opensource SDCC


## Currently supported operations:
* Verify MCU flash with on-disk file with user program
* Upload to MCU flash on-disk file with user program
* Download from MCU flash contents to on-disk file

### to use utility you need:
Power supply that can feed +3.3V at 50 mA atleast (for a chip)
any USB-UART bridge that handle 1200 and 115200bps speeds at 8n1 with the fly switching between them.
USB-UART bridge SHOULD be 3.3V logic level!!!

```
Connect UART0 pins of cachip MCU crisscross (TX line of chip to RX line of USB-UART, RX line of chip to TX line of USB-UART)
There are 'golden thing' to connect via some 200-300ohms resistors of TX, RX pins
Connect GND pins between MCU, PSU, USB-UART at single point.
be-prepared to turn ON power manually when tool asks you to do so.
```

### The proper sequence was simple:
1. startt tool with needed params
2. next turn ON power feed to MCU (you have 4 seconds to do this)
3. see how tool is doing its job


## Acknowledgments
to the entire friends who inspire myself
