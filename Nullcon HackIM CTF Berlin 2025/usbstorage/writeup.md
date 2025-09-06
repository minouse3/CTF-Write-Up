## usbstorage - Nullcon HackIM CTF Berlin 2025 Write-up

![Banner](assets/img/banner.png)

**Challenge:** usbstorage
**Category:** Misc, Forensics
**Points:** 100
**Author:** minousE3

### Introduction
This challenge was a small forensic puzzle involving USB traffic. The story was that a private file had been copied to a USB drive and then deleted, but somehow it could still be recovered from the USB messages that were recorded. We were given a packet capture file, [`usbstorage.pcapng.gz`](assets/files/usbstorage.pcapng.gz), and our goal was to dig through it and recover the lost flag.

### Analyzing the [`usbstorage.pcapng.gz`](assets/files/usbstorage.pcapng.gz) File
The capture logs raw USB traffic between the host and a mass-storage device. Even if a file is later deleted, the transfer of its bytes is still present in the capture. I started by sanity-checking the file with strings to see if any readable hints leaked through the noise. That immediately paid off—mixed in with device chatter were mount paths and file names, including a very telling one:

```bash
┌──(minouse3㉿kali)-[~]
└─$ strings usbstorage.pcapng                  
AMD Ryzen 7 4800H with Radeon Graphics (with SSE4.2)
Linux 6.6.11-1-lts
Dumpcap (Wireshark) 4.2.2 (Git v4.2.2 packaged as 4.2.2-1)
usbmon3
Linux 6.6.11-1-lts
USBC<
->Ae
-<Ae
...
lost+found
install-logs-2023-10-14.0
flag.tar.gz
[qwritable
/media/sda4
...
```
Seeing /media/sda4 and especially flag.tar.gz told me the contents of interest were likely embedded somewhere in the bulk USB transfers. The plan, then, was to extract only the data-bearing packets, reconstruct their bytes into one contiguous blob, and carve out any embedded files.

### How to recover the flag
To rebuild the deleted file from the capture, I filtered out only packets that actually carried payload (usb.data_len > 0) and reassembled their hex bytes into a single binary stream. With that stream in hand, binwalk could identify and extract whatever files were embedded inside.

```bash
# Pull only USB packets that contain data, dump their hex payloads
tshark -r usbstorage.pcapng -Y "usb.data_len > 0" -x > usb_bytes.txt
```
```bash
# 2) Strip hex bytes into a continuous binary blob
grep -oE " [0-9a-f]{2}" usb_bytes.txt | tr -d ' ' | tr -d '\n' | xxd -r -p > usb_dump.bin
```

Now scan the usb_dump.bin file and extract what’s inside:
```bash
binwalk -e usb_dump.bin  
```

binwalk reported a gzip’d artifact; the extractor dropped a file named 13F251 that was a POSIX tar archive.
```bash
┌──(minouse3㉿kali)-[~/Downloads/CTF-Usb_Keyboard_Parser]
└─$ binwalk -e usb_dump.bin                    


DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
1307217       0x13F251        gzip compressed data, from Unix, last modified: 1970-01-01 00:00:00 (null date)

┌──(minouse3㉿kali)-[~]
└─$ cd _usb_dump.bin.extracted
                                                                                                                       
┌──(minouse3㉿kali)-[~/_usb_dump.bin.extracted]
└─$ ls
13F251
                                                                                                                       
┌──(minouse3㉿kali)-[~/_usb_dump.bin.extracted]
└─$ file 13F251
13F251: POSIX tar archive (GNU)

```

Unpacking that led to a gzip’d flag archive, which I then decompressed to reveal the final text file, which is the flag:

```bash
┌──(minouse3㉿kali)-[~/_usb_dump.bin.extracted]
└─$ tar -xvf 13F251
flag.gz
                                                                                                                       
┌──(minouse3㉿kali)-[~/_usb_dump.bin.extracted]
└─$ gzip -d flag.gz
                                                                                                                       
┌──(minouse3㉿kali)-[~/_usb_dump.bin.extracted]
└─$ ls
13F251  flag
                                                                                                                       
┌──(minouse3㉿kali)-[~/_usb_dump.bin.extracted]
└─$ cat flag                  
ENO{USB_STORAGE_SHOW_ME_THE_FLAG_PLS}
```

### Flag
```
ENO{USB_STORAGE_SHOW_ME_THE_FLAG_PLS}
```