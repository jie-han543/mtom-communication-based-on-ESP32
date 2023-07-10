#include<WiFi.h>
#include <cmath>
#include<PubSubClient.h>

//WiFi
const char* ssid ="HONOR";               //ESP32连接的WiFi账号
const char* password =  "fengxindan007";        //WiFi密码

//MQTT Broker
const char* mqttServer = "broker.emqx.io";  //要连接到的服务器IP
const int mqttPort = 1883;                 //要连接到的服务器端口号
 
WiFiClient espClient;                     // 定义wifiClient实例
PubSubClient client(espClient);          // 定义PubSubClient的实例

int led_port = 2;
long lastMsg = 0;
int value = 0;
long randNum;
char msg[20];
char topic[20];
/**
* 消息回调
*/
void callback(char* topic, byte* payload, unsigned int length) 
{
    Serial.print("Message arrived [");              //串口打印：来自订阅的主题:
    Serial.print(topic);                //串口打印订阅的主题
    Serial.print("] ");              //串口打印：信息：
    for (int i = 0; i< length; i++)        //使用循环打印接收到的信息
    {
        Serial.print((char)payload[i]);
    }
    Serial.println(); 

    // Switch on the LED if an 1 was received as first character
    if ((char)payload[0] == '1') {
      digitalWrite(led_port, LOW);   // Turn the LED on (Note that LOW is the voltage level
      // but actually the LED is on; this is because
      // it is active low on the ESP-01)
    } else {
      digitalWrite(led_port, HIGH);  // Turn the LED off by making the voltage HIGH
    }
}

/**
* WiFi
*/
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
 
/**
 * 断开重连
 */
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void setup() 
{
    Serial.begin(115200);                   
    delay(10);
    //连接wifi
    setup_wifi();         
    //MQTT服务器连接函数（服务器IP，端口号）
    client.setServer(mqttServer,mqttPort);  
    //设定回调方式，当ESP32收到订阅消息时会调用此方法
    client.setCallback(callback);           
    
}
 
void loop()   
{
  //重连机制
  if (!client.connected()) {
    reconnect();
  }
  //不断监听信息
  //client.loop();

  long now = millis();
  if (now - lastMsg > 10000) {
    //每2s发布一次信息
    lastMsg = now;
    ++value;
    if (value >=10) {
      value = 0;
    }
    switch (value % 5){
      //温度
      case 0:
        snprintf(topic, 20, "Environ/Temperature");
        randNum = random(15,35);
        snprintf(msg, 20, "%d°C", randNum);
        break;
      default:
        break;
    }
    
    //Serial.print("Publish message: ");
    Serial.println(value);
    client.publish(topic, msg);
  }
}
