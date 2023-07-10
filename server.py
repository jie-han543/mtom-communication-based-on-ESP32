# PC1 (debian 11)
# 作为 MQTT 订阅者订阅消息，接收esp32发表的数据
# 作为 Websocket 服务器，收到数据后转发给 PC2

import random
import asyncio
import websockets
import time
import json
import pymysql
from paho.mqtt import client as mqtt_client # 导入 Paho MQTT客户端
import _thread

# ============================ MQTT部分 ============================
# 设置 MQTT Broker 连接参数
BROKER = 'broker.emqx.io'
PORT = 1883
TOPIC = "Environ/Temperature"
CLIENT_ID = f'python-mqtt-{random.randint(0, 100)}' # 随机生成带有前缀的客户端ID

# MQTT 回调函数，该函数将在客户端连接后被调用
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect MQTT Broker, return code %d\n", rc)
    client = mqtt_client.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client

temp = 0
flag = 0
# MQTT 订阅消息，打印出订阅的topic名称以及接收到的消息内容
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global temp
        global flag
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        temp = msg.payload.decode()
        temp = temp.split()[0]
        flag = flag + 1
        conn = pymysql.connect(host = '127.0.0.1' # 连接名称，本机默认127.0.0.1
        ,user = 'root' # 用户名
        ,passwd='350129' # 密码
        ,port= 3306 # 端口，默认为3306
        ,db='mtom' # 数据库名称
        ,charset='utf8' # 字符编码
        ,autocommit=True
        )
        cur = conn.cursor() # 生成游标对象
        sql="INSERT INTO `temp` (`time`, `temp`) VALUES (CURRENT_TIMESTAMP(), " + temp + ");" # SQL语句
        print(sql)
        print(cur.execute(sql)) # 执行SQL语句
        cur.close() # 关闭游标
        conn.close() # 关闭连接
    client.subscribe(TOPIC)
    client.on_message = on_message

# ========================= Websocket部分 =========================

# 与客户端实时通信函数
async def echo(websocket, path):
    global temp
    global flag
    async for message in websocket:
        # 收到客户端问好，回信
        #hello_message1 = "state:Hello, client! I got your message: {}".format(message)
        print(message)
        if message == "hello":
            hello_message1 = json.dumps({'state':'OK','type':'hello','response':'Hello, client!'})
            await websocket.send(hello_message1)
            hello_message2 = json.dumps({'state':'OK','type':'hello','response':'connect successfully!'})
            await websocket.send(hello_message2)
            hello_message3 = json.dumps({'state':'OK','type':'sending','response':'sending temperature data from esp32...'})
            await websocket.send(hello_message3)
        # 把mqtt收到的数据主动向客户端发送，并写入数据库
        if message == "realtime":
            while True:
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #test
                if flag != 0:
                   new_data = json.dumps({'state':'OK','type':'new_data','response':{'time':t,'temp':temp}})
                   await websocket.send(new_data)
                   flag = 0

# 与客户端通信历史数据函数
async def echo2(websocket, path):
    global temp
    global flag
    async for message in websocket:
        # 收到客户端问好，回信
        #hello_message1 = "state:Hello, client! I got your message: {}".format(message)
        print(message)
        if message == "hello":
            hello_message1 = json.dumps({'state':'OK','type':'hello','response':'Hello, client!'})
            await websocket.send(hello_message1)
            hello_message2 = json.dumps({'state':'OK','type':'hello','response':'connect successfully!'})
            await websocket.send(hello_message2)
            hello_message3 = json.dumps({'state':'OK','type':'sending','response':'sending temperature data from esp32...'})
            await websocket.send(hello_message3)
        # 连接本地数据库
        if message.find("database") != -1:
            conn = pymysql.connect(host = '127.0.0.1' # 连接名称，本机默认127.0.0.1
            ,user = 'root' # 用户名
            ,passwd='350129' # 密码
            ,port= 3306 # 端口，默认为3306
            ,db='mtom' # 数据库名称
            ,charset='utf8' # 字符编码
            )
            cur = conn.cursor() # 生成游标对象
            page = message.split(':')[1]
            sql="select * from `temp` ORDER BY `time` ASC LIMIT " + page + ", 20;" # SQL语句
            #print(sql)
            cur.execute(sql) # 执行SQL语句
            data = cur.fetchall() # 通过fetchall方法获得数据
            if not data:
                empty_message = json.dumps({'state':'OK','type':'empty','response':''})
                await websocket.send(empty_message)
            for i in data: # 打印输出该20条数据
                old_data = json.dumps({'state':'OK','type':'old_data','response':{'time':i[0],'temp':i[1]}}, default=str)
                await websocket.send(old_data)
            close_message = json.dumps({'state':'OK','type':'close','response':''})
            await websocket.send(close_message)
            cur.close() # 关闭游标
            conn.close() # 关闭连接

def mqqt_l():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def websocket2():
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)
    loop2.run_until_complete(websockets.serve(echo2, '0.0.0.0', 8768))
    loop2.run_forever();

if __name__ == '__main__':
    try:
       _thread.start_new_thread( mqqt_l, () )
       _thread.start_new_thread( websocket2,() )
    except:
       print("Error: unable to start thread")
    loop1 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop1)
    loop1.run_until_complete(websockets.serve(echo, '0.0.0.0', 8765))
    loop1.run_forever();

