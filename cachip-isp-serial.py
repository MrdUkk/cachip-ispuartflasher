# not so perfect and ideal but working ISP-mode via
# any USB-UART bridge firmwares uploader to any CACHIP (Jinrui) 8bit MCUs
# this work was based on long research maded by those two people
# dUkk and Mikhailow Alexander
# without theirs finding no tool would exists. So give them some shouts! :)
#
#
# to use it you must:
# 1. purchase USB-UART bridge (if you dont own it already)
# 2. drink some beer (mandatory requirement)
# 3. obtain bootloader.bin somehow
# 4. prepare your firmware.bin from compiled by some 8051 compiler code or download it from MCU :)
# 5. be very careful and do all at your risk!
#
# hand written (c) dUkk 2026 https://blog.softdev.online

import serial
import time
import math
import base64
import sys
import os

def calс_crс8xor(data: bytes) -> int:
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum

def send_to_mcu(data: bytes):
    byte_buffer = bytearray()
    # size of payload
    byte_buffer.append(len(data))
    # payload contents
    byte_buffer.extend(data)
    # checksum
    byte_buffer.append(calс_crс8xor(byte_buffer))
    # cmd to mcu
    byte_buffer.insert(0, 0x55)
    # entire frame
    ispport.write(byte_buffer)

def read_from_mcu(len: int, timeout: int):
    # increment for full protocol frame
    len += 3
    for i in range(timeout):
        if ispport.in_waiting >= len:
            data = bytearray(ispport.read(len))
            # signature of response not expected
            if data[0] != 0xAA:
               return bytearray()
            del data[0]
            crc_recv = data.pop()
            # verify crc
            crc_calc = calс_crс8xor(data)
            del data[0]
            if crc_recv == crc_calc:
               return data
            break
        time.sleep(0.01)
    return bytearray()

def read_from_mcu_data():
    byte_buffer = bytearray()
    # fill buffer with all data comes from serial until a small timeout
    for i in range(10):
        if ispport.in_waiting > 0:
           data = ispport.read(ispport.in_waiting)
           byte_buffer.extend(data)
        time.sleep(0.01)
    
    print(len(byte_buffer))
    if len(byte_buffer) < 1:
       return bytearray()

    # parse frame data
    if byte_buffer[0] != 0xAA:
       return bytearray()
    
    del byte_buffer[0]
    crc_recv = byte_buffer.pop()
    # verify crc
    crc_calc = calс_crс8xor(byte_buffer)
    if crc_recv != crc_calc:
       return bytearray()
    
    return byte_buffer            


# Check if an argument was passed
if len(sys.argv) < 3:
    print("invalid number of arguments provided! use {0} port action chipid".format(sys.argv[0]))
    print("port       - serial port name")
    print("action     - verify , upload , download, erase , chipid . filename used will be hardcoded firmware.bin")
    print("chipid     - chip identification string in HEX")
    print("size       - optional argument. specify size of data to download from mcu")
    exit(1)
    
actionToDo=0
if sys.argv[2].lower() == "verify":
   if len(sys.argv) < 4:
      print("chipid was not specified")
      exit(1)
   actionToDo=1
elif sys.argv[2].lower() == "upload":
   if len(sys.argv) < 4:
      print("chipid was not specified")
      exit(1)
   actionToDo=2
elif sys.argv[2].lower() == "download":
   if len(sys.argv) < 4:
      print("chipid was not specified")
      exit(1)
   if len(sys.argv) != 5:
      print("size in bytes of memory to read was not specified (last argument)")
      exit(1)
   memsize = int(sys.argv[4])   
   actionToDo=3
elif sys.argv[2].lower() == "erase":
   if len(sys.argv) < 4:
      print("chipid was not specified")
      exit(1)
   actionToDo=4
elif sys.argv[2].lower() == "chipid":
   actionToDo=5   
else:
   print("unknown action specified")
   exit(1)

if actionToDo != 5:
   chipid = bytearray.fromhex(sys.argv[3])
   if len(chipid) != 2:
      print("invalid chip identification string specified (two bytes, hex string)")
      exit(1)

print("checking for a required phase1 bootloader")
if not os.path.isfile("bootloader.bin"):
   print("not exist, trying")
   if not os.path.isfile("cafwboot.blob"):
      print("missing cafwboot.blob thats fatal, sorry :(")
      exit(1)
   with open("cafwboot.blob", "rb") as input_file, open("bootloader.bin", "wb") as output_file:
      base64.decode(input_file, output_file)
   
   
print(f"opening serial port {sys.argv[1]}")
ispport = serial.Serial(port=sys.argv[1], timeout=1, baudrate=1200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, xonxoff=0, rtscts=0)
okay=False

# phase1
# try ISP activation magic sequence for 4seconds (Vcc should be ON)
print("trying ISP-mode activation, waiting 4 seconds (feed +3.3V power to MCU !)")
for i in range(400):
    ispport.write(b"\xC1\x83\x07")
    #try read ACK
    if ispport.in_waiting >= 4:
        data = bytearray(ispport.read(4))
        idx = data.find(b"\xAA\x4F\x4B\x00")
        if idx != -1:
            print("MCU accepted connection")
            okay=True
        else:
            print("got mcu unknown response {0}".format(data.hex()))
        break
    time.sleep(0.01)

if not okay:
   print("no connection, try again")

# phase2
if okay:
   print("sending some magic cmd")
   okay=False
   send_to_mcu(b"\x01\x00")
   data = read_from_mcu(6, 100)
   idx = data.find(b"\x81\x00\x08\x46\x32\x53")
   if idx != -1:
      print("got mcu success response")
      okay=True
   else:
      print("got mcu unknown response {0}".format(data.hex()))


# phase3
if okay:
   print("switching port speed")
   okay=False
   time.sleep(0.1)
   ispport.baudrate=115200
   ispport.flush()
   print("sending next magic cmd")
   send_to_mcu(b"\x02")
   # try readback from MCU 00 to FE bytes
   byte_buffer = bytearray()
   for i in range(100):
     if ispport.in_waiting > 0:
         data = ispport.read(ispport.in_waiting)
         byte_buffer.extend(data)
         if len(byte_buffer) >= 254:
             print("got mcu response, asserting values")
             is_incremental = all(byte_buffer[i + 1] - byte_buffer[i] == 1 for i in range(len(byte_buffer) - 1))
             if is_incremental:
                  print("valid")
                  okay=True
             break
     time.sleep(0.01)


# phase4
# something like checking chipid before uploading
if okay and actionToDo != 5:
   print("requesting verify chipID for next phases")
   okay=False
   send_to_mcu(b"\x04" + chipid + b"\x01")
   data = read_from_mcu(3, 100)
   idx = data.find(b"\x80\x00\x00")
   if idx != -1:
      print("got mcu success response")
      okay=True
   else:
      idx = data.find(b"\x80\x01\x00")
      if idx != -1:
         print("got mcu error response")

# phase5
# send bootloader to MCU
if okay:
   print("sending our bootloader")
   okay=False
   blfile = open("bootloader.bin", "rb")
   addrofwrite = 0
   while True:
       chunk = blfile.read(128)
       if not chunk:
          break
       byte_buffer = bytearray()
       # cmd write received to xram location
       byte_buffer.extend(b"\x06\x04\x00")
       # address of write target (2bytes)
       byte_buffer.extend(addrofwrite.to_bytes(2, byteorder='big', signed=False))
       addrofwrite += len(chunk)
       # trailing
       byte_buffer.extend(b"\x80")
       # body
       byte_buffer.extend(chunk)
       # send to mcu
       send_to_mcu(byte_buffer)
       # try read status
       data = read_from_mcu(3, 100)
       idx = data.find(b"\x80\x00\x00")
       if idx != -1:
          print("got mcu success response")
          okay=True
       else:
          idx = data.find(b"\x80\x01\x00")
          if idx != -1:
             print("got mcu error response")
             break
   blfile.close()


# phase6
# verify chipid (authorization?)
if okay and actionToDo != 5:
   print("requesting access to flash with designated chipID")
   okay=False
   send_to_mcu(b"\x18" + chipid + b"\x01")
   data = read_from_mcu(3, 100)
   idx = data.find(b"\x80\x00\x00")
   if idx != -1:
      print("got mcu success response")
      okay=True
   else:
      idx = data.find(b"x80\x01\x00")
      if idx != -1:
         print("got mcu error response")


# phase7 is select between 3 allowed actions
if okay:
   okay=False
   if actionToDo == 1:
      print("requesting to do flash firmware verification with our local firmware.bin file")
      chksum = int.from_bytes(b"\x00\x00\xAD\x75", byteorder="big", signed=False)
      file = open("firmware.bin", "rb")
      while True:
        chunk = file.read(128)
        if not chunk:
           break
        for i in range(len(chunk)):
           chksum += chunk[i]
      filesize = file.tell()
      file.close()
      if filesize <= 32000:
         okay=True
      byte_buffer = bytearray()
      byte_buffer.extend(b"\x13")
      # size to calc hash (2bytes)
      byte_buffer.extend(filesize.to_bytes(2, byteorder='big', signed=False))
      # initial seed
      byte_buffer.extend(b"\x00\x00\xAD\x75")
      if okay:
         okay=False
         send_to_mcu(byte_buffer)
         data = read_from_mcu(8, 100)
         if len(data) > 0:
            print("got mcu response")
            # discard nonsense
            del data[:4]
            # search for our checksum
            idx = data.find(chksum.to_bytes(4, byteorder='big', signed=False))
            if idx != -1:
               print("verification is success {0}".format(chksum.to_bytes(4, byteorder='big', signed=False).hex()))
               okay=True
            else:
               print("checksum verification was failed! value {0} not expected".format(data.hex()))
   elif actionToDo == 2:
      filesize = os.path.getsize("firmware.bin")
      if filesize <= 32000:
         okay=True
      else:
         print("too large firmware size to upload")
      
      if okay:
         okay=False
         # determine how much sectors will be occupied by firmware?
         sectorscount = math.ceil(filesize / 128)
         print(f"requesting onchip flash memory partial {sectorscount} sectors erase")
         send_to_mcu(b"\x05\x28\x45\x00" + sectorscount.to_bytes(1, byteorder='big', signed=False))
         # give MCU bunch of time to perform this long operation
         time.sleep(0.400)
         data = read_from_mcu(3, 900)
         idx = data.find(b"\x80\x00\x00")
         if idx != -1:
            print("got mcu success response")
            okay=True
         else:
            idx = data.find(b"x80\x01\x00")
            if idx != -1:
               print("got mcu error response")
      
      if okay:
         okay=False
         print("uploading from firmware.bin to onchip memory")
         file = open("firmware.bin", "rb")
         addrofwrite = 0
         byte_buffer = bytearray()
         while True:
             chunk = file.read(128)
             if not chunk:
                break
             # cmd write received to flash location
             byte_buffer.extend(b"\x06\x28\x00")
             # address of write target (2bytes)
             byte_buffer.extend(addrofwrite.to_bytes(2, byteorder='big', signed=False))
             # trailing
             byte_buffer.extend(b"\x80")
             # body
             byte_buffer.extend(chunk)
             # send to mcu
             send_to_mcu(byte_buffer)
             # try read status
             data = read_from_mcu(3, 100)
             idx = data.find(b"\x80\x00\x00")
             if idx != -1:
                print("got mcu success response write at {0}".format(addrofwrite))
                okay=True
             else:
                idx = data.find(b"\x80\x01\x00")
                if idx != -1:
                   print("got mcu error response")
                break
             byte_buffer.clear()
             addrofwrite += len(chunk)
         file.close()
   elif actionToDo == 3:
      print("requesting onchip flash memory read with size {0} to firmware.bin".format(memsize))
      file = open("firmware.bin", "wb")
      addrofread = 0
      byte_buffer = bytearray()
      while addrofread < memsize:
          # cmd read onchip memory
          byte_buffer.extend(b"\x08\x28\x00")
          # address where to read from (2bytes)
          byte_buffer.extend(addrofread.to_bytes(2, byteorder='big', signed=False))
          # read size is 128bytes
          byte_buffer.extend(b"\x80")
          # send to mcu
          send_to_mcu(byte_buffer)
          # readback data
          byte_buffer = read_from_mcu_data()
          if len(byte_buffer) > 5:
             print("frame is valid, data at {0} writing to file {1} bytes".format(addrofread, len(byte_buffer)-5))
             # remove header
             del byte_buffer[:5]
             file.write(byte_buffer)
          else:
             print(f"frame invalid and discarded. read break at {addrofread}")
             break
          byte_buffer.clear()
          addrofread += 128
      file.close()
   elif actionToDo == 4:
      print(f"requesting onchip flash memory FULL erase")
      send_to_mcu(b"\x05\x28\x45\x01\x00")
      # give MCU bunch of time to perform this long operation
      time.sleep(0.400)
      data = read_from_mcu(3, 900)
      idx = data.find(b"\x80\x00\x00")
      if idx != -1:
         print("got mcu success response")
         okay=True
      else:
         idx = data.find(b"x80\x01\x00")
         if idx != -1:
            print("got mcu error response")
   elif actionToDo == 5:
      print("requesting onchip private area memory download to 2bareadump.bin")
      file = open("2bareadump.bin", "wb")
      addrofread = 0
      memsize = 256
      byte_buffer = bytearray()
      while addrofread < memsize:
          # cmd read onchip memory
          byte_buffer.extend(b"\x08\x2B\x00")
          # address where to read from (2bytes)
          byte_buffer.extend(addrofread.to_bytes(2, byteorder='big', signed=False))
          # read size is 128bytes
          byte_buffer.extend(b"\x80")
          # send to mcu
          send_to_mcu(byte_buffer)
          # readback data
          byte_buffer = read_from_mcu_data()
          if len(byte_buffer) > 5:
             print("frame is valid, data at {0} writing to file {1} bytes".format(addrofread, len(byte_buffer)-5))
             # remove header
             del byte_buffer[:5]
             file.write(byte_buffer)
          else:
             print(f"frame invalid and discarded. read break at {addrofread}")
             break
          byte_buffer.clear()
          addrofread += 128
      file.close()
      
      
# something like a finish session
print("sending session end cmd")
send_to_mcu(b"\x07")
data = read_from_mcu(3, 100)
idx = data.find(b"\x80\x00\x00")
if idx != -1:
   print("got mcu success response")
else:
   print("got mcu error response")
     
ispport.close()
print("end, remove power from MCU")
