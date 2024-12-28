#!/bin/python
import os
import sys
import time

file_spec = """/**
  ******************************************************************************
  * @file    ota_file_data.c
  * @author  wyz
  * @date    2020/01/14
  * @brief   This file is generated by ota.bin via script.
  Array ota_bin_info and ota_bin_data are get from the bin file.

  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 wyz. All rights reserved.
  *
  ******************************************************************************
**/\n\n#include "can-fd-host.h"\nuint32_t upgradeCaseGetFileSize(void);\n\n"""

localtime = time.asctime( time.localtime(time.time()))
file_size_define_spec = """\r\n\nuint32_t upgradeCaseGetFileSize(void)
{
    return sizeof(ota_bin_data);
}\r\n"""

list_data = []
list_bytes = []

from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter
import crcmod.predefined
import array
import hashlib

fw_data = array.array('B')

crc16func = crcmod.predefined.mkCrcFun('crc-16')


def aes_xcrypt(data):
        bmkey = bytes([0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c])
        aes = AES.new(bmkey, AES.MODE_CTR, counter=Counter.new(128, initial_value=0))
        return aes.encrypt(data)

# CRC16 XMODEM
def crc16(x, invert):
    wCRCin = 0x0000
    wCPoly = 0x1021
    for byte in x:
        if type(byte) is str:
            wCRCin ^= (ord(byte) << 8)
        else:
            wCRCin ^= ((byte) << 8)
        for i in range(8):
            if wCRCin & 0x8000:
                wCRCin = (wCRCin << 1) ^ wCPoly
            else:
                wCRCin = (wCRCin << 1)

    wCRCin = wCRCin & 0xffff
    return wCRCin

def read_data_from_binary_file(filename, list_data):
    with open(filename, 'rb') as rf:
        rf.seek(0, 0)
        while True:
            t_byte = rf.read(1)
            if len(t_byte) == 0:
                break
            else:
                fw_data.append(ord(t_byte))

    with open(filename, 'rb') as f:
        f.seek(0, 0)
        en_fw = bytes([])
        while True:
            en_fw = f.read(256)
            if len(en_fw) == 0:
                break
            else:
                buffer = aes_xcrypt(en_fw)
                for byte in buffer:
                    list_data.append("0x%.2X" % byte)
                    list_bytes.append(byte)

def read_u32(list_data):
    return int(list_data[3], 16) << 24 | int(list_data[2], 16) << 16 | int(list_data[1], 16) << 8 | int(list_data[0],
                                                                                                        16)
def read_u32_from_bytes(list_data, i):
    return int(list_data[6+i*8], 16) << 28 | int(list_data[7+i*8], 16) << 24 | int(list_data[4+i*8], 16) << 20 | int(list_data[5+i*8], 16) << 16 | \
    int(list_data[2+i*8], 16) << 12 | int(list_data[3+i*8], 16) << 8 | int(list_data[0+i*8], 16) << 4 | int(list_data[1+i*8], 16)

def write_data_to_text_file(filename, list_data, data_num_per_line):
    data_num_per_line_int = int(data_num_per_line)
    with open(filename, 'w+') as wf:
        lll = len(list_data)
        app_version = 0
        boot_version = 0
        crc = 0
        crc = crc16func(fw_data)
        md5 = hashlib.md5()
        md5.update(fw_data)
        uid = b'langgo137526'
        print('md5=', md5.hexdigest())
        md5_digest = bytes.fromhex(md5.hexdigest())
        md5_value = read_u32_from_bytes(md5.hexdigest(),0)
        md5_value1 = read_u32_from_bytes(md5.hexdigest(),1)
        md5_value2 = read_u32_from_bytes(md5.hexdigest(),2)
        md5_value3 = read_u32_from_bytes(md5.hexdigest(),3)
        sha256 = hashlib.sha256()
        sha256.update(md5_digest)
        sha256.update(uid)
        print('sha256 of md5 & uid=', sha256.hexdigest())
        sha256_digest = bytes.fromhex(sha256.hexdigest())
        sha256_value = read_u32_from_bytes(sha256.hexdigest(),0)
        sha256_value1 = read_u32_from_bytes(sha256.hexdigest(),1)
        sha256_value2 = read_u32_from_bytes(sha256.hexdigest(),2)
        sha256_value3 = read_u32_from_bytes(sha256.hexdigest(),3)
        sha256_value4 = read_u32_from_bytes(sha256.hexdigest(),4)
        sha256_value5 = read_u32_from_bytes(sha256.hexdigest(),5)
        sha256_value6 = read_u32_from_bytes(sha256.hexdigest(),6)
        sha256_value7 = read_u32_from_bytes(sha256.hexdigest(),7)
        info = '''const uint32_t ota_bin_info[] =
{{
    0x{:08X},  //App version({})
    0x{:08X},  //File Size({})
    0x{:08X},  //CRC
    0x{:08X},  //MD5
    0x{:08X},  //MD5
    0x{:08X},  //MD5
    0x{:08X},  //MD5
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
    0x{:08X},  //SHA256
}};
'''
        print(info.format(app_version,app_version,lll,lll, crc, md5_value,md5_value1,md5_value2,md5_value3, \
        sha256_value,sha256_value1,sha256_value2,sha256_value3,sha256_value4,sha256_value5,sha256_value6,sha256_value7))
        wf.write(file_spec)
        wf.write(info.format(app_version,app_version,lll,lll, crc, md5_value,md5_value1,md5_value2,md5_value3, \
        sha256_value,sha256_value1,sha256_value2,sha256_value3,sha256_value4,sha256_value5,sha256_value6,sha256_value7))
        wf.write('\n\nconst uint8_t ota_bin_data[] =\n{\n    ')
        if ((data_num_per_line_int <= 0) or data_num_per_line_int > len(list_data)):
            data_num_per_line_int = 16
            print('data_num_per_line out of range,use default value\n')
        for i in range(0, len(list_data)):
            if ((i != 0) and (i % data_num_per_line_int == 0)):
                wf.write('\n    ')
                wf.write(list_data[i] + ', ')
            elif (i + 1) == len(list_data):
                wf.write(list_data[i])
            else:
                wf.write(list_data[i] + ', ')
        wf.write('\n};')
        wf.write(file_size_define_spec)
        wf.write("/** "+localtime+" V1.1**/\n\n")

def main():
    input_f = 'OTA.bin'
    output_f = 'ota_file_data.c'

    data_num_per_line = 32
    read_data_from_binary_file(input_f, list_data)
    write_data_to_text_file(output_f, list_data, data_num_per_line)


if __name__ == "__main__":
    sys.exit(main())
