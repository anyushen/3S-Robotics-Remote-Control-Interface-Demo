# from pymodbus.client.sync import ModbusSerialClient as ModbusClient
# pymodbus需要安装2.5.3版本（pip install pymodbus==2.5.3）及pymodbus需要的所有依赖性（pip install pyserial==3.5 six==1.16.0 pyserial-asyncio==0.6）
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
from flask import Flask, request, jsonify, render_template
import time
import threading  # 导入 threading 模块用于多线程
import webbrowser
import redis, pickle


r = redis.Redis()

# 服务器地址和端口
server_ip = '169.254.10.100'
server_port = 502

# 初始化Modbus客户端
# client = ModbusClient(method='rtu', port='COM9', baudrate=9600, parity='O', bytesize=8, stopbits=1, timeout=1)
client = ModbusTcpClient(server_ip, port=server_port, framer=ModbusRtuFramer)
client.timeout = 1

# 定义信号地址映射
OUTPUT_ADDRESSES = {
    '外部启动': 0x0080,
    '外部停止': 0x0081,
    '远程模式': 0x2082,
    '自动模式': 0x2083,
    '程序复位': 0x2084,
    '故障/报警清除': 0x2085,
    '外部上电': 0x2086,
    '外部下电': 0x2087,
    '程序选择位B1': 0x2088,
    '程序选择位B2': 0x2089,
    '程序选择位B3': 0x208A,
    '程序选择位B4': 0x208B,
    '程序选择位B5': 0x208C,
    '程序选择位B6': 0x208D,
    '程序选择位B7': 0x208E,
    '程序选择位B8': 0x208F,
    '速度选择位B1': 0x2090,
    '速度选择位B2': 0x2091,
    '速度选择位B3': 0x2092,
    '速度选择位B4': 0x2093,
    '速度选择位B5': 0x2094,
    '速度选择位B6': 0x2095,
    '速度选择位B7': 0x2096,
    '速度选择位B8': 0x2097,
    '功能选择位B1': 0x2098,
    '功能选择位B2': 0x2099,
    '功能选择位B3': 0x209A,
    '功能选择位B4': 0x209B,
    '备用1': 0x209C,
    '备用2': 0x209D,
    '备用3': 0x209E,
    '备用4': 0x209F,
    '+X': 0X20A0,
    '-X': 0X20A1,
    '+Y': 0X20A2,
    '-Y': 0X20A3,
    '+Z': 0X20A4,
    '-Z': 0X20A5,
    '+T': 0X20A6,
    '-T': 0X20A7,
    '工位A': 0X20A8,
    '工位B': 0X20A9,
    '工位C': 0X20AA,
    '工位D': 0X20AB,
    '工件参数_L_B1': 0X20AC,
    '工件参数_L_B2': 0X20AD,
    '工件参数_L_B3': 0X20AE,
    '工件参数_L_B4': 0X20AF,
    '工件参数_L_B5': 0X20B0,
    '工件参数_L_B6': 0X20B1,
    '工件参数_L_B7': 0X20B2,
    '工件参数_L_B8': 0X20B3,
    '工件参数_L_B9': 0X20B4,
    '工件参数_L_B10': 0X20B5,
    '工件参数_L_B11': 0X20B6,
    '工件参数_L_B12': 0X20B7,
    '工件参数_L_B13': 0X20B8,
    '工件参数_L_B14': 0X20B9,
    '工件参数_L_B15': 0X20BA,
    '工件参数_L_B16': 0X20BB,
    '工件参数_W_B1': 0X20BC,
    '工件参数_W_B2': 0X20BD,
    '工件参数_W_B3': 0X20BE,
    '工件参数_W_B4': 0X20BF,
    '工件参数_W_B5': 0X20C0,
    '工件参数_W_B6': 0X20C1,
    '工件参数_W_B7': 0X20C2,
    '工件参数_W_B8': 0X20C3,
    '工件参数_W_B9': 0X20C4,
    '工件参数_W_B10': 0X20C5,
    '工件参数_W_B11': 0X20C6,
    '工件参数_W_B12': 0X20C7,
    '工件参数_W_B13': 0X20C8,
    '工件参数_W_B14': 0X20C9,
    '工件参数_W_B15': 0X20CA,
    '工件参数_W_B16': 0X20CB,
    '工件参数_H_B1': 0X20CC,
    '工件参数_H_B2': 0X20CD,
    '工件参数_H_B3': 0X20CE,
    '工件参数_H_B4': 0X20CF,
    '工件参数_H_B5': 0X20D0,
    '工件参数_H_B6': 0X20D1,
    '工件参数_H_B7': 0X20D2,
    '工件参数_H_B8': 0X20D3,
    '工件参数_H_B9': 0X20D4,
    '工件参数_H_B10': 0X20D5,
    '工件参数_H_B11': 0X20D6,
    '工件参数_H_B12': 0X20D7,
    '工件参数_H_B13': 0X20D8,
    '工件参数_H_B14': 0X20D9,
    '工件参数_H_B15': 0X20DA,
    '工件参数_H_B16': 0X20DB,
    '工件参数_T1_B1': 0X20DC,
    '工件参数_T1_B2': 0X20DD,
    '工件参数_T1_B3': 0X20DE,
    '工件参数_T1_B4': 0X20DF,
    '工件参数_T1_B5': 0X20E0,
    '工件参数_T1_B6': 0X20E1,
    '工件参数_T1_B7': 0X20E2,
    '工件参数_T1_B8': 0X20E3,
    '工件参数_T1_B9': 0X20E4,
    '工件参数_T1_B10': 0X20E5,
    '工件参数_T1_B11': 0X20E6,
    '工件参数_T1_B12': 0X20E7,
    '工件参数_T1_B13': 0X20E8,
    '工件参数_T1_B14': 0X20E9,
    '工件参数_T1_B15': 0X20EA,
    '工件参数_T1_B16': 0X20EB,
    '工件参数_T2_B1': 0X20EC,
    '工件参数_T2_B2': 0X20ED,
    '工件参数_T2_B3': 0X20EE,
    '工件参数_T2_B4': 0X20EF,
    '工件参数_T2_B5': 0X20F0,
    '工件参数_T2_B6': 0X20F1,
    '工件参数_T2_B7': 0X20F2,
    '工件参数_T2_B8': 0X20F3,
    '工件参数_T2_B9': 0X20F4,
    '工件参数_T2_B10': 0X20F5,
    '工件参数_T2_B11': 0X20F6,
    '工件参数_T2_B12': 0X20F7,
    '工件参数_T2_B13': 0X20F8,
    '工件参数_T2_B14': 0X20F9,
    '工件参数_T2_B15': 0X20FA,
    '工件参数_T2_B16': 0X20FB,
}

INPUT_ADDRESSES = {
    '远程模式': 0x2080,
    '自动模式': 0x2081,
    '电机开启': 0x2082,
    '准备就绪': 0x2083,
    '运行': 0x2084,
    '暂停': 0x2085,
    '急停': 0x2086,
    '外部急停': 0x2087,
    '程序终止': 0x2088,
    '综合异常E': 0x2089,
    '操作错误': 0x208A,
    '警告发生W': 0x208B,
    '碰撞传感器': 0x208C,
    '可以远程上电': 0x208D,
    '安全点信号': 0x208E,
    '备用1': 0x208F,
    '错误/警告输出B1': 0x2090,
    '错误/警告输出B2': 0x2091,
    '错误/警告输出B3': 0x2092,
    '错误/警告输出B4': 0x2093,
    '错误/警告输出B5': 0x2094,
    '错误/警告输出B6': 0x2095,
    '错误/警告输出B7': 0x2096,
    '错误/警告输出B8': 0x2097,
    '错误/警告输出B9': 0x2098,
    '错误/警告输出B10': 0x2099,
    '错误/警告输出B11': 0x209A,
    '错误/警告输出B12': 0x209B,
    '错误/警告输出B13': 0x209C,
    '错误/警告输出B14': 0x209D,
    '错误/警告输出B15': 0x209E,
    '错误/警告输出B16': 0x209F,
    '工位A': 0x20A0,
    '工位B': 0x20A1,
    '工位C': 0x20A2,
    '工位D': 0x20A3
}

# 初始化输入和输出字典
input_dict = {signal_name: False for signal_name in INPUT_ADDRESSES}
output_dict = {signal_name: False for signal_name in OUTPUT_ADDRESSES}

r.set('modbus_input_dict', pickle.dumps(input_dict))
r.set('modbus_output_dict', pickle.dumps(output_dict))

# 定义指令处理函数
def polling():
    """通讯轮询函数"""
    global input_dict, output_dict
    while True:
        start_time1 = time.time()  # 记录开始时间
        # 读取所有输入寄存器
        try:
            start_address = min(INPUT_ADDRESSES.values())  # 获取最小的输入地址作为起始地址
            result = client.read_discrete_inputs(start_address, 36, unit=1)
            if not result.isError():
                bits = result.bits

                polling_input_dict = pickle.loads(r.get('modbus_input_dict'))
                # 遍历 INPUT_ADDRESSES 字典，按顺序分配读取到的值
                for index, (signal_name, address) in enumerate(sorted(INPUT_ADDRESSES.items(), key=lambda item: item[1])):
                    if index < len(bits):
                        polling_input_dict[signal_name] = bits[index]

                r.set('modbus_input_dict', pickle.dumps(polling_input_dict))

                print(f"轮询读取成功！")
            else:
                print(f"轮询读取失败！")
        except Exception as e:
            print(f"轮询读取出错: {e}")

        # 写入所有输出寄存器
        try:
            # 按照地址顺序排序 output_dict
            polling_output_dict = pickle.loads(r.get('modbus_output_dict'))
            sorted_output = sorted(polling_output_dict.items(), key=lambda item: OUTPUT_ADDRESSES[item[0]])
            # 提取值列表
            values = [value for _, value in sorted_output]
            # 获取最小的输出地址作为起始地址
            start_output_address = min(OUTPUT_ADDRESSES.values())
            # 一次性写入 40 个地址的值
            response1 = client.write_coils(start_output_address, values[:2], unit=1)
            response2 = client.write_coils(list(OUTPUT_ADDRESSES.values())[2], values[2:124], unit=1)
            if response1.isError() or response2.isError():
                print(f"轮询写入失败！")
            else:
                print(f"轮询写入成功！")

        except Exception as e:
            print(f"轮询写入出错: {e}")

        #wait(0.75 - (time.time() - start_time1))  # 每0.75秒轮询一次
        wait(0.3)  # 每0.75秒轮询一次

def keep_connection():
    """持续检查 Modbus 连接状态"""
    while True:
        if not client.is_socket_open():
            if client.connect():
                print("Modbus 客户端重新连接成功")
            else:
                print("Modbus 客户端重新连接失败")
        time.sleep(1)

def send_signal(signal_name, value):
    """更新输出字典，信号将在轮询时发送"""
    if signal_name in OUTPUT_ADDRESSES:
        signal_output_dict = pickle.loads(r.get('modbus_output_dict'))
        signal_output_dict[signal_name] = value
        r.set('modbus_output_dict', pickle.dumps(signal_output_dict))
        print(f"{signal_name} 信号已更新到输出字典: {value}")
    else:
        print(f"未知信号: {signal_name}")

def clear_fault():
    """故障/报警清除信号输出1，持续0.5秒"""
    send_signal('故障/报警清除', True)
    time.sleep(0.3)
    send_signal('故障/报警清除', False)
    time.sleep(0.2)

def set_remote_auto():
    """远程自动模式，远程和自动信号输出1"""
    send_signal('远程模式', True)
    send_signal('自动模式', True)

def set_auto_mode():
    """自动模式，远程模式和自动模式输出1后0.5秒，远程模式输出0"""
    send_signal('远程模式', True)
    send_signal('自动模式', True)
    wait(1)
    send_signal('远程模式', False)
    send_signal('外部停止', True)

def set_manual_mode():
    """手动模式，远程模式输出1，自动模式输出0"""
    send_signal('远程模式', True)
    send_signal('自动模式', False)
    wait(1)
    send_signal('远程模式', False)
    send_signal('外部停止', True)

def wait(seconds):
    """等待指定秒数"""
    time.sleep(seconds)

def check_input(signal_name):
    """从输入字典中获取信号状态"""
    if signal_name in input_dict:
        signal_input_dict = pickle.loads(r.get('modbus_input_dict'))

        print(f"接收 {signal_name}: {signal_input_dict[signal_name]}")
        return signal_input_dict[signal_name]
    else:
        print(f"未知输入信号: {signal_name}")
        return False

def send_params(input_list, station):
    signal_list = ['L_B', 'W_B', 'H_B', 'T1_B', 'T2_B']
    
    if station == 'A':
        send_signal('工位A', True)
        send_signal('工位B', False)

    if station == 'B':
        send_signal('工位B', True)
        send_signal('工位A', False)

    if station == 'C':
        send_signal('工位C', True)
        send_signal('工位D', False)

    if station == 'D':
        send_signal('工位D', True)
        send_signal('工位C', False)

    for p in range(5):
        param = input_list[p]
        signal = signal_list[p]
        for i in range(16):
            bit_value = (param >> i) & 1
            send_signal(f'工件参数_{signal}{i+1}', bit_value)

def start_sequence(input_list, station):
    """启动序列"""
    pause_sequence()
    for _ in range(2):
        clear_fault()

    start_time = time.time()  # 记录开始时间
    
    '''暂时改成15秒'''
    while time.time() - start_time < 10:  # 10 秒内持续判断

        print(f'安全点信号：{check_input('安全点信号')}')

        if check_input('安全点信号'):

            send_params(input_list, station)     #发送工件、工位参数

            if check_input('可以远程上电') :
                send_signal('外部上电', True)
                wait(2)
            else:
                if check_input('电机开启'):
                    send_signal('程序复位', True)
                    wait(2)
                    while not bool(client.read_holding_registers(0x0100, 1, unit = 1)):
                        wait(0.5)
                    send_signal('程序复位', False)
                    wait(0.5)
                    send_signal('外部停止', True)
                    wait(0.5)
                    for i in range(8):
                        bit_value = (50 >> i) & 1
                        send_signal(f'程序选择位B{i+1}', bit_value)
                    for i in range(4):
                        bit_value = (0 >> i) & 1
                        send_signal(f'功能选择位B{i+1}', bit_value)
                    wait(0.5)
                    send_signal('外部启动', True)
                    wait(0.5)
                    if check_input('运行'):
                        send_signal('外部启动', False)
                        print("启动成功！")
                        return 0
            time.sleep(1)  # 每次判断间隔 1 秒
        wait(1)
        print("机器人不在安全点，请先一键回安全点！")
    print("操作超时，退出！")  # 超时则退出并打印提示信息
    return 1

def pause_sequence():
    """暂停序列"""
    for signal_name in reversed(OUTPUT_ADDRESSES):
        if signal_name != '自动模式' and signal_name != '远程模式' :
            send_signal(signal_name, False)
    print("已暂停！")
    return 0

def restart_sequence(input_list, station):
    """再启动序列"""
    pause_sequence()
    for _ in range(2):
        clear_fault()

    start_time = time.time()  # 记录开始时间
    while time.time() - start_time < 10:  # 10 秒内持续判断
        if check_input('可以远程上电'):
            send_signal('外部上电', True)
            wait(2)
        else:
            if check_input('电机开启'):
                wait(0.5)
                send_signal('外部停止', True)
                send_params(input_list, station)     #发送工件，工位参数
                for i in range(8):
                    bit_value = (50 >> i) & 1
                    send_signal(f'程序选择位B{i+1}', bit_value)
                for i in range(4):
                    bit_value = (0 >> i) & 1
                    send_signal(f'功能选择位B{i+1}', bit_value)
                wait(0.5)
                send_signal('外部启动', True)
                wait(0.5)
                if check_input('运行'):
                    send_signal('外部启动', False)
                    print("再启动成功！")

                    return 0
        time.sleep(1)  # 每次判断间隔 1 秒
    print("操作超时，退出！")  # 超时则退出并打印提示信息

    return 1

def go_to_safety_point():
    """一键回安全点序列"""
    pause_sequence()
    for _ in range(2):
        clear_fault()
    start_time = time.time()  # 记录开始时间
    while time.time() - start_time < 10:  # 10 秒内持续判断
        if check_input('可以远程上电'):
            send_signal('外部上电', True)
            wait(2)
        else:
            if check_input('电机开启'):
                send_signal('程序复位', True)
                wait(0.5)
                send_signal('程序复位', False)
                wait(0.5)
                send_signal('外部停止', True)
                for i in range(8):
                    bit_value = (50 >> i) & 1
                    send_signal(f'程序选择位B{i+1}', bit_value)
                for i in range(4):
                    bit_value = (1 >> i) & 1
                    send_signal(f'功能选择位B{i+1}', bit_value)
                wait(0.5)
                send_signal('外部启动', True)
                wait(0.5)
                if check_input('运行'):
                    send_signal('外部启动', False)
                    start_time = time.time()  # 记录开始时间
                    while time.time() - start_time < 15:  # 15 秒内持续判断
                        if check_input('安全点信号'):
                            print("回安全点完成！")
                            return
                        time.sleep(1)
                    print("未回到安全点！")
        time.sleep(1)  # 每次判断间隔 1 秒
    print("操作超时，退出！")  # 超时则退出并打印提示信息
    return

def control_function():
    """控制功能序列"""
    # pause_sequence()
    for _ in range(2):
        clear_fault()
    start_time = time.time()  # 记录开始时间
    while time.time() - start_time < 10:  # 10 秒内持续判断
        if check_input('可以远程上电'):
            send_signal('外部上电', True)
            wait(2)
        else:
            if check_input('电机开启'):
                send_signal('程序复位', True)
                wait(0.5)
                send_signal('程序复位', False)
                wait(0.5)
                send_signal('外部停止', True)
                for i in range(8):
                    bit_value = (50 >> i) & 1
                    send_signal(f'程序选择位B{i+1}', bit_value)
                for i in range(4):
                    bit_value = (2 >> i) & 1
                    send_signal(f'功能选择位B{i+1}', bit_value)
                wait(0.5)
                send_signal('外部启动', True)
                wait(0.5)
                if check_input('运行'):
                    send_signal('外部启动', False)
                    # 这里不需要立即返回，等待按钮事件
                    break
        time.sleep(1)  # 每次判断间隔 1 秒
    else:
        print("操作超时，退出！")  # 超时则退出并打印提示信息
        return jsonify(status='error', message='操作超时，退出！')

def from_jingpai_start():
    """从精拍启动序列"""
    pause_sequence()
    for _ in range(2):
        clear_fault()
    start_time = time.time()  # 记录开始时间
    while time.time() - start_time < 10:  # 10 秒内持续判断
        if check_input('可以远程上电'):
            send_signal('外部上电', True)
            wait(2)
        else:
            if check_input('电机开启'):
                send_signal('程序复位', True)
                wait(0.5)
                send_signal('程序复位', False)
                wait(0.5)
                send_signal('外部停止', True)
                for i in range(8):
                    bit_value = (50 >> i) & 1
                    send_signal(f'程序选择位B{i+1}', bit_value)
                for i in range(4):
                    bit_value = (3 >> i) & 1
                    send_signal(f'功能选择位B{i+1}', bit_value)
                wait(0.5)
                send_signal('外部启动', True)
                wait(0.5)
                if check_input('运行'):
                    send_signal('外部启动', False)
                    print("已从精拍启动！")
                    return
        time.sleep(1)  # 每次判断间隔 1 秒
    print("操作超时，退出！")  # 超时则退出并打印提示信息
    return