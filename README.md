# CACHIP (Jinrui) MCU ISP-mode tool
Utility allows on-chip memory manipulation via
exposed in phase0 (ROM) and phase1 (XRAM) boot code functions.


the utility was based on a large research posted here:
[personal blog](https://blog.softdev.online/index.php?controller=post&action=view&id_post=56)


# Why?
Motivation behind the release of this tool to the public domain is to open 
this fancy very cost-effective micocontroller to be programmed by enthusiasts across 
the whole earth grobe. Patching existing firmwares and providing fresh ones fixing evil bugs. 
So E-Waste will be mimized. At least I want to believe it. Thats a first goal. The second one
is raise education level
Additional goal was to extend supported OS from MS Windows (tm) only to MacOS and Linux.
 

## How to write new firmware?
You can use official MCU Manual for SFR/etc descriptions 
and use Keil C51 or any other tool like opensource SDCC


## Currently supported operations:
* Verify MCU flash with on-disk file with user program
```
$python3 cachip-isp-serial.py COM4 verify 20A0
opening serial port COM4
trying ISP-mode activation, waiting 3seconds (feed +3.3V power to MCU !)
MCU accepted connection
sending some magic cmd
got mcu success response
switching port speed
sending next magic cmd
got mcu response, asserting values
valid
requesting verify chipID for next phases
got mcu success response
sending our bootloader
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
requesting access to flash with designated chipID
got mcu success response
requesting to do flash firmware verification with our local firmware.bin file
got mcu response
verification is success
sending session end cmd
got mcu success response
end, remove power from MCU
```

* Upload to MCU flash on-disk file with user program
```
$python3 cachip-isp-serial.py COM4 upload 20a0
opening serial port COM4
trying ISP-mode activation, waiting 3seconds (feed +3.3V power to MCU !)
MCU accepted connection
sending some magic cmd
got mcu success response
switching port speed
sending next magic cmd
got mcu response, asserting values
valid
requesting verify chipID for next phase
got mcu success response
sending bootloader
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
requesting to run code with designated chipID
got mcu success response
requesting onchip flash memory partial erase
got mcu success response
uploading from firmware.bin to onchip memory
128
got mcu success response
128
got mcu success response
128
got mcu success response
128
got mcu success response
128
got mcu success response
128
got mcu success response
128
got mcu success response
128
got mcu success response
58
got mcu success response
sending session end cmd
got mcu success response
end, remove power from MCU
```

* Download from MCU flash contents to on-disk file. Only available here. original cachip tool wont provide this.
```
$python3 cachip-isp-serial.py COM4 download 20A0 512
opening serial port COM4
trying ISP-mode activation, waiting 3seconds (feed +3.3V power to MCU !)
MCU accepted connection
sending some magic cmd
got mcu success response
switching port speed
sending next magic cmd
got mcu response, asserting values
valid
requesting verify chipID for next phase
got mcu success response
sending bootloader
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
requesting to run code with designated chipID
got mcu success response
requesting onchip flash memory read with size 512
135
frame is valid, writing to file 128 bytes
135
frame is valid, writing to file 128 bytes
135
frame is valid, writing to file 128 bytes
135
frame is valid, writing to file 128 bytes
sending session end cmd
got mcu success response
end
```

* Erase Perform chip all flash memory wipe

* Chipid Dump contents of hidden 2B area of chip memory. Only available here. Original cachip tool wont provide this.
```
$python3.exe cachip-isp-serial.py COM4 chipid
checking for a required phase1 bootloader
opening serial port COM4
trying ISP-mode activation, waiting 4 seconds (feed +3.3V power to MCU !)
MCU accepted connection
sending some magic cmd
got mcu success response
switching port speed
sending next magic cmd
got mcu response, asserting values
valid
sending our bootloader
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
got mcu success response
requesting onchip private area memory download to 2bareadump.bin
135
frame is valid, data at 0 writing to file 128 bytes
135
frame is valid, data at 128 writing to file 128 bytes
sending session end cmd
got mcu success response
end, remove power from MCU
```


### To use utility you need:
Power supply that can feed +3.3V at 50 mA atleast (for a chip)
any USB-UART bridge that handle 1200 and 115200bps speeds at 8n1 with on the fly switching between them.
USB-UART bridge SHOULD be 3.3V logic level!!!

```
Connect UART0 pins of cachip MCU crisscross (TX line of chip to RX line of USB-UART, RX line of chip to TX line of USB-UART)
There are 'golden thing' to connect via some 200-300ohms resistors of TX, RX pins
Connect GND pins between MCU, PSU, USB-UART at single point.
be-prepared to turn ON power manually when tool asks you to do so.
```

### About ChipID
to perform any valuable action you need to specify exactly matching 2 bytes ChipID.
How to obtain it? Thats require issue another cmd to read hidden not documented chip AREA "2B".
from its 2bareadump.bin look for two bytes at offset 3. Thats it! 
Currently only few are known
```
CA51F253L3 = 20A0
CA51F253L2 = 20A1
```

### The proper sequence was simple:
1. startt tool with needed params
2. next turn ON power feed to MCU (you have 4 seconds to do this)
3. see how tool is doing its job

## Disclaimer
You shall use provided tool for educational purposes and at your risk!

## Acknowledgments
to the entire friends who inspire myself
