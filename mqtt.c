#include<WiFi.h>
#include<cmath>
#include<PubSubClient.h>

//WiFi
const char* ssid ="Hs-1";                     //ESP32连接的WiFi账号
const char* password =  "01070910";           //WiFi密码

//MQTT Broker
const char* mqttServer = "broker.emqx.io";    //要连接到的服务器IP
const int mqttPort = 1883;                    //要连接到的服务器端口号

WiFiClient espClient;                         //定义wifiClient实例
PubSubClient client(espClient);               //定义PubSubClient的实例

int led_port = 2;
long lastMsg = 0;                             //上次收到消息的时间戳
long randNum;                                 //随机整数
long randNum2;                                //随机小数
char topic[20];                               //主题
char msg[20];                                 //消息


/**
* WiFi
*/
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  //Serial.println();
  //Serial.print("Connecting to ");
  //Serial.println(ssid);
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
  // 循环直到重新连接
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // 随机生成一个客户机 ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {             // 尝试连接成功
      Serial.println("connected");
      // 连接成功后发布消息
      client.publish("outTopic", "hello world");
      // 订阅
      //client.subscribe("inTopic");
    } else {                                            // 连接失败
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println("try again in 5 seconds");
      // 等待5秒再重试
      delay(5000);
    }
  }
}

void setup() {
    Serial.begin(115200);                   
    delay(10);
    setup_wifi();                                       // 连接wifi    
    client.setServer(mqttServer,mqttPort);              // MQTT服务器连接函数（服务器IP，端口号）  
}
 
void loop() {
  // 失败重连
  if (!client.connected()) {
    reconnect();
  }
  //不断监听信息
  //client.loop();
  long now = millis();                                  // 返回自程序启动以来经过的毫秒数
  if (now - lastMsg > 2000) {                           // 每2s发布一次信息
    lastMsg = now;
    snprintf(topic, 20, "Environ/Temperature");         // 将格式化的字符串复制到 topic 中，字符的最大数目20
    randNum = random(15,35);
    randNum2 = random(0,9);
    snprintf(msg, 20, "%d.%d °C", randNum, randNum2);   // 将格式化的字符串复制到 msg 中，字符的最大数目20

    Serial.println(msg);
    client.publish(topic, msg);
  }
}
