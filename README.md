# mtom-communication-based-on-ESP32

### 项目说明
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;通过虚拟机模拟服务器，一台ESP32模拟传感器端，一台ESP32模拟执行输出端，其他功能在PC端基于Python实现。传感器端通过MQTT协议上报数据到服务器，数据类型自行定义，能够反映一种或数种传感器监测值即可。第一台PC通过Python实现的MQTT客户端订阅传感数据，实时显示传感数据，并能通过TCP套接字、UDP套接字或Websocket转发到第二台PC。可扩展实现数据库存储功能，支持历史查询或回放。第二台PC根据接收到的转发数据，定义一种规则对数据进行处理，根据处理结果，通过蓝牙连接执行输出端进行结果输出。

### 总体结构
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;项目基于Python实现，运行在Windows10和Debian11两种系统的虚拟机和PC机上；使用一台ESP32模拟传感器端，一台ESP32模拟执行输出端。系统总体结构如图所示。
![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/3cef02d0-175a-4036-854b-6b5d03442e7b)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;传感器端通过MQTT协议上传温度和时间数据到云代理服务器，PC1则通过Python实现的MQTT客户端向服务器订阅传感数据，并通过websocket转发到PC2。PC2作为websocket的客户端，能接收到转发的摄氏温度传感数据，随后将其转化为华氏温度并实时显示。执行输出端与PC2通过蓝牙连接，当温度超过阈值时，执行输出端将亮起LED灯。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;为了模块划分后开发的便利性，图中的PC1实际指的是一台安装在PC2上的虚拟机。此外，由于Websocket服务更多是为了实现能实时更新的网页，因此基于JavaScript编写了浏览器客户端。同时，在PC1上搭建了数据库，支持客户端向其查询历史数据。


#### 浏览器客户端与服务器通信工作流程
![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/8fa44721-5ceb-408a-9b1d-0f8536abe3b1)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;上图是运行在Windows系统PC机上的浏览器客户端向Debian系统的虚拟机服务器请求实时数据的websocket数据交换过程示意图。用户通过在浏览器打开html文件运行其中的JavaScript代码，向服务器申请建立websocket连接。连接成功建立后，浏览器和服务器之间均可以主动向对方发送消息。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;其中，服务器返回的message和data为JSON格式，包含以下三个属性。
```
State:服务器返回的工作代码
	OK – 服务器正常工作
	Error – 服务器存在异常
type:回信的类型，浏览器收到不同类型的回信将执行不同功能
	hello – 问好型消息，客户端收到后显示携带的回信内容 
	sending – 发送型消息，客户端收到后触发向服务器发送实时数据请求
	new_data – 实时数据型消息，客户端收到后解析数据并显示在HTML页面
response:回信携带的具体内容
```
具体定义如下：
```
hello_message1:
'state': 'OK',
'type': 'hello',
'response': 'Hello, client!'
hello_message2:
'state': 'OK',
'type': 'hello',
'response': 'connect successfully!'
hello_message3:
'state': 'OK',
'type': 'sending',
'response': 'sending temperature data from esp32...'
new_data: 
'state': 'OK',
'type': 'new_data',
'response': {
'time':传感器生成该数据的时间,
'temp':传感器传至服务器的温度 }
```
![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/02447471-6b3c-4d90-a967-db2781813c58)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;上图是浏览器客户端向虚拟机服务器请求历史数据时websocket的数据交换过程示意图。初次加载页面时，浏览器会自动获取服务器数据库中按时间升序排列的前20条数据。随后，用户可点击html页面中的按钮，向服务器申请获取更多数据。每一次点击都会触发重建一个websocket，传输后20条数据并显示在html页面中。而在每个连接中，当20条数据传输完成，服务器会发送close型的message，浏览器收到后将断开这个websocket连接。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;其中，服务器返回的message和data为JSON格式，包含以下三个属性。
```
State:服务器返回的工作代码
	OK – 服务器正常工作
	Error – 服务器存在异常
type:回信的类型，浏览器收到不同类型的回信将执行不同功能
	hello – 问好型消息，客户端收到后显示携带的回信内容 
	sending – 发送型消息，客户端收到后触发向服务器发送历史数据请求
	old_data – 历史数据型消息，客户端收到后解析数据并显示在HTML页面
empty – 空型消息，客户端收到后向用户弹窗提示已经没有更多数据可获取了
close – 关闭型消息，客户端收到后关闭这个websocket连接
response:回信携带的具体内容
```
具体定义如下：
```
old_data: 
'state': 'OK',
'type': 'old_data',
'response': {
'time':数据库中该数据的产生时间,
'temp':数据库中传感器的温度
}
empty_message:
'state': 'OK',
'type': 'empty',
'response': ''
close_message:
'state': 'OK',
'type': 'close',
'response': ''
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;项目采用MariaDB数据库，相关操作代码如下。创建并使用mtom名称的数据库，并将时间和温度数据保存至名为temp的表中。该表分别定义了日期时间类型的time和浮点数类型的温度temp。

```sql
# 创建数据库
CREATE DATABASE mtom
# 创建表
CREATE TABLE IF NOT EXISTS `temp` (
	`time` DATETIME NOT NULL,
	`temp` FLOAT NOT NULL
	)DEFAULT CHARSET=utf8;
# 插入测试数据
INSERT INTO `temp` (`time`, `temp`) 
VALUES (CURRENT_TIMESTAMP(), 25.8);
# 读取时间按升序排列时从第0行起20行的数据表
SELECT * FROM `temp` ORDER BY `time` ASC LIMIT 0, 20;
```

#### Python客户端与服务器通信工作流程
![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/934eff66-9f80-43f9-be43-026573eae386)


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;上图是运行在Windows系统PC机上的python程序客户端向Debian系统的虚拟机服务器请求实时数据的websocket数据交换过程示意图。其数据交换格式和流程设计与浏览器客户端类似。此外，在客户端收到新的转发消息后，需要使用MySQL将其写入数据库，以供查询历史数据。


### 运行结果
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;如图6-1所示，在Arduino开发环境中编写好程序，验证无误后完成程序的在线上传，在窗口中设置波特率为115200。图6-2(a)为硬件连接图，图6-2(b)为代码运行结果。串口会先输出WiFi和PC的连接信息，随后向代理服务器发送随机温度数值。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PC端连接至服务器后，即可以同步接收到Esp32设备发出的温度数值，如图6-3所示。
  ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/4975a047-f0e4-42f5-b82d-634928e6482f)
图6-1 编译烧录Arduino程序

 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/5f2b1bb2-8de0-4c02-8f4a-a68c2e8652c6)
 
 (a)硬件连接                                 (b)窗口监视器显示输出随机温度数值                  
图6-2 Arduino运行结果图

 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/5f2b1bb2-8de0-4c02-8f4a-a68c2e8652c6)
 
图6-3 PC端同步接收温度消息

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;为了使虚拟机Debian上运行的服务器程序能同时接收MQTT信息和向客户端发送信息，如图6-4中141和142行所示建立两个新线程。第一个线程连接至MQTT代理服务器，订阅对应主题，随后循环接收推送的每条实时消息；第二个线程使用8768端口，echo2函数负责历史数据的回放与查询。而在主线程中，使用8765端口，echo函数负责响应客户端请求，实时转发订阅的数据。

![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/59dd1a02-fa4e-4194-889a-8a65095b273f)

图6-4 服务器代码主函数

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;要求虚拟机、PC和esp32要连接在同一个WiFi下。图6-5使用ip address命令查看了虚拟机的IP地址192.168.13.64。随后将客户端websocket连接的IP地址设置为对应IP。

 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/e8e9549c-c4e5-4c36-b86a-1a31e296cb5c)

图6-5 查看ip地址

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;打开mysql服务并执行相关代码创建数据库和表。

 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/7051343b-0d6b-412b-a9c5-e9b64c096cf7)

图6-6 打开mysql服务

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;运行服务器代码，图6-7(a)为服务器运行结果示意图，图6-7(b)-(d)为浏览器客户端运行结果示意图。图6-7(a)可见服务器始终在接收MQTT中主题为“Environ/Temperature”的数据。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;图6-7(a)中服务器收到客户端的两个线程发出的hello请求后，对应地往客户端返回图6-7(c)所示的问好消息，客户端收到后确认连接无误，将问好消息显示在html页面中的通讯状态部分中。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;其中一个请求是realtime请求，服务器收到后将MQTT数据转发至浏览器客户端实时数据部分展示。客户端从与服务器建立的websocket连接中每收到一条实时数据，就将其转化为华氏温度并添加到图6-7(b)所示的html页面中。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;另一个请求是database:0请求，服务器收到后从数据库查询历史消息并返回。客户端收到后添加到图6-7(d)所示的html页面中。图6-8为数据库查询结果，对比可知两者一致。

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;点击浏览器中的“获取更多历史数据”按钮，浏览器会重新建立一个websocket连接，并发送database:20请求，获取后面的20条历史数据。
  ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/99af8d3c-79dc-4290-86dd-dc8b7e47a312)

(a) 服务器运行结果示意图                  (b) 浏览器客户端实时数据运行结果示意图 

    ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/079bcc8b-db4f-40c0-98a5-8bcc3a1409de)

(c) 浏览器客户端通讯状态运行结果示意图         (d) 浏览器客户端历史数据运行结果示意图

图6-7 服务器-浏览器运行结果

 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/99fca19d-e71e-4da4-a459-d28663f3f857)

图6-8 数据库结果

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;运行服务器代码，图6-9为服务器运行结果示意图。运行python客户端时，服务器只会收到实时显示请求。客户端收到转发数据后，将其转化为华氏度，并通过蓝牙传输给esp32，运行结果如图6-10所示。温度低于25摄氏度时，客户端打开串口，向esp32传输信号，控制关闭蓝色LED灯，随后关闭串口；温度高于25摄氏度时，客户端打开串口，向esp32传输信号，控制点亮蓝色LED灯，随后关闭串口。

 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/50ff73e2-48a4-4494-89f1-b59ff6c5f243)

图6-9 服务器运行结果
 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/f69e3a35-010e-46a5-9f7e-e727cacc2956)

(a) 温度低于25摄氏度时LED灭
 ![image](https://github.com/jie-han543/mtom-communication-based-on-ESP32/assets/57163528/a8494691-387d-4d09-af8f-aa0b58bd24df)

(b) 温度高于25摄氏度时LED亮

图6-10 客户端运行结果


