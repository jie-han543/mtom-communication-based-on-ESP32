# PC2 (windows)
# 作为 Websocket 客户端，接收 PC1 转发的数据
# 作为 Bluetooth 服务器，向 esp32 发送数据

#import serial
import asyncio
import websockets
import json



# 与服务器通信函数
async def hello(uri):
    async with websockets.connect(uri) as websocket:
        flag = 1
        # 向服务器问好并输出
        await websocket.send("hello")
        print("> Hello sever!")
        # 接收服务器回信/发送的数据并输出
        while True:
            recv_text = await websocket.recv()
            #print("< {}".format(recv_text))
            recv_obj = json.loads(recv_text)
            if recv_obj.get('type') == 'hello':
                print("< {}".format(recv_obj.get('response')))
            if recv_obj.get('type') == 'sending':
                await websocket.send("realtime")
                print("> waiting temperature data from esp32...")
            if recv_obj.get('type') == 'new_data':
                data_time = recv_obj.get('response').get('time')
                data_temp = recv_obj.get('response').get('temp')
                data_tempF = float(data_temp) * 9/5 + 32
                if flag != 0:
                    print("> date and time         temp(C)    temp(F)")
                    flag = 0
                print("> {}".format(data_time) + "   {}".format(data_temp) + "       {}".format(data_tempF))
                '''
                ser = serial.Serial("COM10", 115200)    # 打开COM10，将波特率配置为115200，其余参数使用默认值
                if ser.isOpen():                        # 判断串口是否成功打开
                    print("= The serial port {} is successfully opened.".format(ser.name)) # 输出串口号
                else:
                    print("= Failed to open the serial port.")
                
                if data_tempF < 77:
                    ser.write("c".encode()); # cold
                    #print("c")
                else :
                    ser.write("h".encode()) # hot
                    #print("h")
                ser.close();
                print('= The port is closed.');
                '''


# 向服务器创建 websocket 连接
asyncio.get_event_loop().run_until_complete(hello('ws://192.168.13.64:8765/'))
