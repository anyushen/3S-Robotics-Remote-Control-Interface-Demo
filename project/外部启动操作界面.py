import PySimpleGUI as sg
from PIL import Image
import io
import base64
import app      #导入1号机指令程序文件
import app2     #导入2号机
import threading
import queue
import time
from io import BytesIO

#所有状态栏（空闲，运行中etc.）的key为 '-ZT_A-', '-ZT_B-', '-ZT_C-', '-ZT_D-'，对应工位A~D的状态栏
#所有机器栏（无，1号机，2号机）的key为 '-RB_A-', '-RB_B-', '-RB_C-', '-RB_D-'
#所有输入框的key为：'-IN_A_L-', '-IN_A_W-', '-IN_A_H-', '-IN_A_T1-', '-IN_A_T2-'，对应第一行（工位A）的五项参数，其他工位（行）以此类推
#所有开始按钮的key为：'-KS_A-', '-KS_B-', '-KS_C-', '-KS_D-'
#所有暂停按钮的key为：'-ST_A-', '-ST_B-', '-ST_C-', '-ST_D-'
#所有结束按钮的key为：'-O_A-', '-O_B-', '-O_C-', '-O_D-'
#所有取消按钮的key为：'-QX_A-', '-QX_B-', '-QX_C-', '-QX_D-'


#***************************定义函数*****************************
def err(station, msg):   #暂时定义一个报错函数，指定station对应的工位状态显示报错
    window[f'-ZT_{station}-'].update(text='故障', button_color=('black','red'))
    my_popup(f'工位 {station} 发生错误：{msg}', '发生错误', ['OK'])

#检查名为t_name的子线程是否正在运行
def check_active_thread(machine, t_names):
    for i in t_names:
        for t in threading.enumerate():
            if i in t.name and t.tag == machine:
                return True
    return False

def send_params_and_start(input_list, station): #开机函数，接收包含所有参数的列表和工位号作为参数
    machine = machines[station]

    #用子线程暂时锁住暂停按钮，以防快速点击造成逻辑混乱
    lock_thread = threading.Thread(target=button_cooldown, args=[station])
    lock_thread.daemon = True
    lock_thread.start()

    #调用开机指令并在子线程中运行
    if machine == '1号机':
        start_thread_1 = threading.Thread(target=app.start_sequence, args = [input_list, station])
        start_thread_1.daemon = True
        start_thread_1.tag = '1号机'
        app.set_remote_auto()
        start_thread_1.start()
    elif machine == '2号机':
        start_thread_2 = threading.Thread(target=app2.start_sequence, args = [input_list, station])
        start_thread_2.daemon = True
        start_thread_2.tag = '2号机'
        app2.set_remote_auto()
        start_thread_2.start()

def pause(station):     #暂时定义一个暂停函数，接收工位号作为参数（0, 1, 2, 3)

    #用子线程暂时锁住暂停按钮，以防快速点击造成逻辑混乱
    lock_thread = threading.Thread(target=button_cooldown, args=[station])
    lock_thread.daemon = True
    lock_thread.start()

    #调用暂停指令并在子线程中运行
    if station in ['A', 'B']:
        pause_thread_1 = threading.Thread(target=app.pause_sequence)
        pause_thread_1.daemon = True
        pause_thread_1.tag = '1号机'
        pause_thread_1.start()

    elif station in ['C', 'D']:
        pause_thread_2 = threading.Thread(target=app2.pause_sequence)
        pause_thread_2.daemon = True
        pause_thread_2.tag = '2号机'
        pause_thread_2.start()

    return 0 #成功时返回值为0

def resume(input_list, station):            #再启动函数，接收工位号作为参数（0, 1, 2, 3)
    machine = machines[station]

    #用子线程暂时锁住暂停按钮，以防快速点击造成逻辑混乱
    lock_thread = threading.Thread(target=button_cooldown, args=[station])
    lock_thread.daemon = True
    lock_thread.start()

    #调用再启动指令并在子线程中运行
    if machine == '1号机':
        resume_thread_1 = threading.Thread(target=app.restart_sequence, args = [input_list, station])
        resume_thread_1.daemon = True
        resume_thread_1.tag = '1号机'
        resume_thread_1.start()
    elif machine == '2号机':
        resume_thread_2 = threading.Thread(target=app2.restart_sequence, args = [input_list, station])
        resume_thread_2.daemon = True
        resume_thread_2.tag = '2号机'
        resume_thread_2.start()

def end_task(station):   #暂时定义一个停止函数，接收工位号作为参数 (0, 1, 2, 3)
    return 0    #停止成功时返回值为0

def update_stat():  #定义一个获取状态信息函数，接收工位号作为参数 (0, 1, 2, 3)
    while True:

        #1号机运行状态
        current_station = ''    #确认一号机当前工位
        if app.check_input('工位A'):
            current_station = 'A'
        elif app.check_input('工位B'):
            current_station = 'B'

        print(f'————————————————当前运行状态：{app.check_input('运行')}——————————————————')
        if current_station != '':
            #——————测试代码——————
            print(f'当前运行工位为{current_station}')

            if app.check_input('运行'):
                #————测试代码————
                print('检测到运行信号')
                window.write_event_value(f'-IN_PROGRESS_{current_station}-', None)

            if app.check_input('暂停'):
                window.write_event_value(f'-SUSPEND_{current_station}-', None)

            if app.check_input('程序终止'):
                window.write_event_value(f'-FINISH_{current_station}-', None)


        #2号机运行状态
        current_station2 = ''    #确认2号机当前工位
        if app.check_input('工位C'):
            current_station2 = 'C'
        elif app.check_input('工位D'):
            current_station2 = 'D'

        if current_station2 != '':
            #——————测试代码——————
            print(f'当前运行工位为{current_station2}')

            if app2.check_input('运行'):
                window.write_event_value(f'-IN_PROGRESS_{current_station2}-', None)

            if app2.check_input('暂停'):
                window.write_event_value(f'-SUSPEND_{current_station2}-', None)

            if app2.check_input('程序终止'):
                window.write_event_value(f'-FINISH_{current_station2}-', None)

        time.sleep(0.75)

def lock_input(station, lock):  #一键禁用/解锁station工位所有输入框和开始按钮。lock = True则禁用，lock = False则解锁
    window[f'-KS_{station}-'].update(disabled = lock)        #运行过程中锁定开始按钮
    window[f'-IN_{station}_L-'].update(disabled = lock)      #运行过程中锁定输入框
    window[f'-IN_{station}_W-'].update(disabled = lock)
    window[f'-IN_{station}_H-'].update(disabled = lock)
    window[f'-IN_{station}_T1-'].update(disabled = lock)
    window[f'-IN_{station}_T2-'].update(disabled = lock)

def button_cooldown(station):   #在窗口中锁定station工位的暂停和停止按钮
    window.write_event_value(f'-BUTTON_COOLDOWN-', station)
    
def my_popup(message, p_title, buttons):     #自定义弹窗
    layout = [
        [sg.Text(message)],
        [sg.Button(btn) for btn in buttons]  # 自定义按钮大小
    ]
    pop_up = sg.Window(p_title, layout, modal=True)
    event, _ = pop_up.read()
    pop_up.close()
    return event

def resize_image(path, max_width, max_height):      #用于等比例缩放图片
    image = Image.open(path)
    image.thumbnail((max_width, max_height))  # 等比例缩放
    bio = BytesIO()
    image.save(bio, format="PNG")
    return bio.getvalue()

#***************************窗口布局*******************************

sg.SetOptions(font = ('宋体', 15), text_justification = 'center', element_padding = (5, 10))

sg.theme('lightblue2')

machines = {'A': '1号机', 'B': '1号机', 'C': '2号机', 'D': '2号机'}
params = ['L', 'W', 'H', 'T1', 'T2']
stations = ['A', 'B', 'C', 'D']

#按钮 & 输入框 & 信息显示
layoutL = [
    [sg.Text('状态', size=(8,1), relief = 'ridge'), sg.Text('机器', size=(5,1), relief = 'ridge'),sg.Text('工位', size=(5,1), relief = 'ridge')]+
    [sg.Text(param, size=(7,1), justification='center') for param in params],
    
    #第一行
    [sg.B('空闲', enable_events = False, key='-ZT_A-', button_color=('black','grey'), size=(8,1)), 
     sg.T('无', size=(5,1), key = '-RB_A-'), 
     sg.T('A:', size=(5,1))]+
    [sg.In(size=(7,1), key=f'-IN_A_{param}-', font = 12, disabled_readonly_text_color = 'grey', justification = 'left') for param in params]+
    [sg.B('开始', size = 7, key='-KS_A-', button_color=('black', 'limegreen')),
     sg.B('暂停', size = 7, key='-ST_A-', button_color=('black','yellow')),
     sg.B('结束', size = 7, key='-O_A-', button_color=('black','lightcoral'))],

    #第二行
    [sg.B('空闲', enable_events = False, key='-ZT_B-', button_color=('black','grey'), size=(8,1)),
     sg.T('无', size=(5,1), key = '-RB_B-'), 
     sg.T('B:', size=(5,1))]+ 
    [sg.In(size=(7,1), key=f'-IN_B_{param}-', font = 12, disabled_readonly_text_color = 'grey', justification = 'left') for param in params]+
    [sg.B('开始', size = 7, key='-KS_B-', button_color=('black','limegreen')),
     sg.B('暂停', size = 7, key='-ST_B-', button_color=('black','yellow')),
     sg.B('结束', size = 7, key='-O_B-', button_color=('black','lightcoral'))],
    
    #第三行
    [sg.B('空闲', enable_events = False, key='-ZT_C-', button_color=('black','grey'),size=(8,1)),
     sg.T('无', size=(5,1), key = '-RB_C-'), 
     sg.T('C:', size=(5,1))]+ 
    [sg.In(size=(7,1), key=f'-IN_C_{param}-', font = 12, disabled_readonly_text_color = 'grey', justification = 'left') for param in params]+
    [sg.B('开始', size = 7, key='-KS_C-', button_color=('black','limegreen')),
     sg.B('暂停', size = 7, key='-ST_C-', button_color=('black','yellow')),
     sg.B('结束', size = 7, key='-O_C-', button_color=('black','lightcoral'))],
    
    #第四行
    [sg.B('空闲', enable_events = False, key='-ZT_D-',button_color=('black','grey'),size=(8,1)),
     sg.T('无', size=(5,1), key = '-RB_D-'), 
     sg.T('D:', size=(5,1))]+ 
    [sg.In(size=(7,1), key=f'-IN_D_{param}-', font = 12, disabled_readonly_text_color = 'grey', justification = 'left') for param in params]+
    [sg.B('开始', size = 7, key='-KS_D-', button_color=('black','limegreen')),
     sg.B('暂停', size = 7, key='-ST_D-', button_color=('black','yellow')),
     sg.B('结束', size = 7, key='-O_D-', button_color=('black','lightcoral')),
     sg.B('测试', key = '-测试-')],
]

#工件图例
layoutR = [
    [sg.Image(data = resize_image('工件图例.png', max_width=600, max_height=400))]
]

#主操作界面标签页
tab1_layout = [
    [sg.Text('外部启动运行界面', font = ('宋体', 30), justification = 'center', expand_x = True)],
    [sg.Col(layoutL, vertical_alignment = 'top'), sg.Col(layoutR, pad = ((100,50), None), vertical_alignment = 'middle')],
]

tab2_layout = [
    [sg.T('稍后添加')]

]

#整合所有layout
layout = [
    [sg.TabGroup([
        [sg.Tab('外部启动运行', tab1_layout), sg.Tab('机器参数', tab2_layout)]
        ], border_width = 5, tab_border_width = 3, selected_background_color = 'navyblue', selected_title_color = 'white')]
]

#创建窗口
window = sg.Window('任务执行控制系统', layout, margins=(20, 15), 
                   enable_close_attempted_event = True,
                   resizable=True,                    # 允许窗口缩放
                   finalize=True,
                   enable_window_config_events=True)  # 启用窗口配置事件

#用于记录每个工位运行情况的参数
in_pause = {}       #工位是否暂停中
in_progress = {}    #工位是否运行中
in_error = {}       #工位是否故障中
in_queue = {}       #工位是否等待中

for i in stations:
    in_progress[i] = False
    in_pause[i] = False
    in_error[i] = False
    in_queue[i] = False

#*****************************程序开始运行*****************************
if __name__ == "__main__":
    try:
        # 启动需要持续运行的线程
        #1号机连接状态
        connection_thread = threading.Thread(target=app.keep_connection)
        connection_thread.daemon = True  # 设置为守护线程，程序退出时自动结束
        connection_thread.start()  # 启动线程

        #2号机连接状态
        #connection_thread2 = threading.Thread(target=app2.keep_connection)
        #connection_thread2.daemon = True
        #connection_thread2.start()

        #1号机信号轮询
        polling_thread = threading.Thread(target=app.polling)
        polling_thread.daemon = True
        polling_thread.start()

        #2号机信号轮询
        #polling_thread2 = threading.Thread(target=app2.polling)
        #polling_thread2.daemon = True
        #polling_thread2.start()

        #1，2号机状态更新
        update_thread = threading.Thread(target=update_stat)
        update_thread.daemon = True
        update_thread.start()

        #*****************************事件循环********************************
        while True:
            event, values = window.read()

            #退出程序之前跳出弹窗确认
            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                logout = my_popup('确定退出程序？', '退出程序', ['确认退出', '取消'])
                if logout == '确认退出':
                    break
                else:
                    continue
            
            #——————测试代码——————
            if event == '-测试-':
                app.send_signal('工位A', True)
            #**************************按下开机键******************************
            if event.startswith('-KS_'):
                try:

                    #识别工位 & 机器
                    station = event.strip('-KS_')   #获取工位号：A, B, C, D
                    machine = machines[station]

                    #获取并将输入参数转换为浮点数，若报错说明参数为空/不为数字
                    results = [int(v) for k, v in values.items() if isinstance(k, str) and k.startswith(f'-IN_{station}')]
                    
                    sg.Popup(results)

                    valid_param = True
                    for i in results:   #检查参数是否包含0或负数
                        if i <= 0:
                            valid_param = False
                            sg.Popup('无效参数，请重新输入！')

                #出现报错说明输入参数不为数字
                except ValueError:
                    valid_param = False
                    sg.Popup('无效参数，请重新输入！')

                #当确认参数全部合规后，开始发送并启动机器
                if valid_param:

                    send_params_and_start(results, station)

                    #*****测试代码*****
                    in_progress[station] = True

                    lock_input(station, True)      #机器开始运行后锁定输入框和开始按钮

                    #某个工位开机后，将该机器负责的其他工位设置为等待中并锁定开始键
                    for k, v in machines.items():
                        if v == machine and k != station:
                            window[f'-KS_{k}-'].update(text = '等待中', button_color = ('black', 'light grey'), disabled = True)


            #**************************按下暂停键*****************************
            if event.startswith('-ST_'):
                #识别工位
                station = event.strip('-ST_')

                #只有在运行过程当中才能暂停
                if in_progress[station] or in_pause[station]:
                    
                    results = [int(v) for k, v in values.items() if isinstance(k, str) and k.startswith(f'-IN_{station}')]

                    if in_pause[station]:              #如果当前正在暂停中，则尝试再启动

                        #——————测试代码——————
                        print('检测到当前已经暂停')

                        resume(results, station)
                        window[f'-ST_{station}-'].update(text='暂停')
                        in_pause[station] = False  #将暂停状态改为False

                        #——————测试代码——————
                        in_progress[station] = True
                            
                    else:      #如果当前正在运行中，则尝试暂停
                        #——————测试代码——————
                        print('检测到当前还未暂停')

                        pause(station)
                        window[f'-ST_{station}-'].update(text='继续')
                        in_pause[station] = True   #将暂停状态改为True

            #**************************按下停止键****************************
            if event.startswith('-O_'):

                #识别工位
                station = event.strip('-O_')

                #只有在运行过程中才能停止
                if in_progress[station] or in_pause[station]:

                    #弹窗请求确认或取消停止
                    answer = my_popup(f'是否要结束工位 {station} 的作业？', '结束作业', ['确定', '取消'])

                    if answer == '确定':

                        #停止函数返回0说明停止成功
                        if end_task(station) == 0:

                            in_progress[station] = False     #将运行状态改为False
                            in_pause[station] = False     # 将暂停状态改为False
                            window[f'-ST_{station}-'].update(text='暂停')    #重置暂停按钮
                            
                            #——————测试代码——————
                            print('设置状态为空闲中++++++++++++++++++++++++')
                            window[f'-ZT_{station}-'].update(text = '空闲', button_color = ('black','grey'))
                            window[f'-RB_{station}-'].update(value = '无')       #实时更新当前工位运行的机器
                            window.refresh()
                            
                            lock_input(station, False)  #解锁当前工位输入框和开始按钮

                            my_popup(f'已结束工位 {station} 的作业', '结束成功', [' OK '])

                        #返回值不为0则出现报错
                        else:
                            err(station, '结束作业')

            #**************************代替子线程处理的元素更新*************************

            #———————————————————update_stat() 实时更新状态—————————————————————
            if event.startswith('-IN_PROGRESS_'):    #运行中状态
                station = event.strip('-IN_PROGRESS_')

                #当机器开始运行但状态显示还未更新时，更新状态为运行中
                if in_progress[station] and not (window[f'-ZT_{station}-'].get_text() == '运行中'):

                    #——————测试代码——————
                    print('设置状态为运行中++++++++++++++++++++++++++++++')

                    window[f'-ZT_{station}-'].update(text = '运行中', button_color = ('black','green'))     #实时更新当前工位运行状态
                    window[f'-RB_{station}-'].update(value = f'{machines[station]}')       #实时更新当前工位运行的机器

            if event.startswith('-SUSPEND_'):       #暂停中状态
                station = event.strip('-SUSPEND_')

                if in_pause[station] and not (window[f'-ZT_{station}-'].get_text() == '暂停中'):
                    #——————测试代码——————
                    print('设置状态为暂停中++++++++++++++++++++++++++++++++++++')

                    window[f'-ZT_{station}-'].update(text = '暂停中', button_color = ('black','yellow'))
                    window.refresh()

            if event.startswith('-FINISH_'):          #程序终止状态
                station = event.strip('-FINISH_')
                machine = machines[station]

                window[f'-ZT_{station}-'].update(text = '空闲', button_color = ('black','grey'))
                window[f'-RB_{station}-'].update(value = '无')       #实时更新当前工位运行的机器
                
                #结束后将其他显示等待中的工位解锁
                for i in stations:
                    if i != station and machines[i] == machine:
                        window[f'-KS_{i}-'].update(text = '开始', button_color = ('black', 'green'), disabled = False)
                window.refresh()

                in_progress[station] = False
                in_pause[station] = False
                
            if event == '-BUTTON_COOLDOWN-':        #启动、暂停、再启动过程中锁定按钮
                station = values['-BUTTON_COOLDOWN-']
                machine = machines[station]

                window[f'-ST_{station}-'].update(disabled = True)
                window[f'-O_{station}-'].update(disabled = True)
                window.refresh()

                #以0.5秒间隔持续检查启动，暂停，或再启动子线程是否在运行中
                while check_active_thread(machine, ['start_sequence', 'pause_sequence', 'restart_sequence']):
                    time.sleep(0.5)
                
                #当上述所有线程都结束运行后，解锁按钮
                window[f'-ST_{station}-'].update(disabled = False)
                window[f'-O_{station}-'].update(disabled = False)
                window.refresh()

            time.sleep(1)
        window.close()
    except KeyboardInterrupt:
        print("\n程序已退出")
    finally:
        app.client.close