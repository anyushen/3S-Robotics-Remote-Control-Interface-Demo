# from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from flask import Flask, request, jsonify, render_template
import time
import threading  # 导入 threading 模块用于多线程

# client = ModbusClient(method='rtu', port='COM9', baudrate=19200, parity='O', bytesize=8, stopbits=1, timeout=1)
client = ModbusClient(host='192.168.1.254', port=502)
if client.connect():
     print('ok')
else:
     print('err')

response = client.write_coil(0x2080, 0, unit=1)
if response.isError():
     print('发送失败')
else:
     print('发送成功')
while True:
     input = client.read_coils(0x009D, 1, unit=1).bits[0]
     print(input)
     time.sleep(1.5)