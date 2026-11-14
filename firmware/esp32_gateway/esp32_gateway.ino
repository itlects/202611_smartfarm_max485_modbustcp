#include <WiFi.h>
// Change locally; do not commit real Wi-Fi credentials.
const char* SSID="YOUR_WIFI";
const char* PASS="YOUR_WIFI_PASSWORD";
WiFiServer server(502);
const int DIR=21;
uint16_t crc(const uint8_t* b,int n){uint16_t c=65535;while(n--){c^=*b++;for(int i=0;i<8;i++)c=c&1?(c>>1)^0xA001:c>>1;}return c;}
bool exact(WiFiClient &c,uint8_t* b,int n){unsigned long t=millis();int p=0;while(p<n&&c.connected()&&millis()-t<500){if(c.available())b[p++]=c.read();else delay(1);}return p==n;}
void setup(){Serial.begin(115200);pinMode(DIR,OUTPUT);digitalWrite(DIR,LOW);Serial2.begin(9600,SERIAL_8N1,16,17);WiFi.begin(SSID,PASS);server.begin();}
void loop(){
 WiFiClient c=server.available();if(!c){delay(1);return;}
 uint8_t h[7],p[5],r[32];
 if(!exact(c,h,7)||h[2]||h[3]||h[4]||h[5]!=6||(h[6]!=1&&h[6]!=2)||!exact(c,p,5)){c.stop();return;}
 int n=0;bool valid=p[0]==6 || (p[0]==3&&p[3]==0&&p[4]>0&&p[4]<=8);
 if(valid){
  uint8_t req[8]={h[6],p[0],p[1],p[2],p[3],p[4],0,0};uint16_t cs=crc(req,6);req[6]=cs;req[7]=cs>>8;
  while(Serial2.available())Serial2.read();delay(5);
  digitalWrite(DIR,HIGH);delayMicroseconds(100);Serial2.write(req,8);Serial2.flush();digitalWrite(DIR,LOW);
  unsigned long t=millis(),last=t;
  while(millis()-t<300){if(Serial2.available()){int v=Serial2.read();if(n<32)r[n++]=v;last=millis();}else if(n&&millis()-last>5)break;else delay(1);}
 }
 bool ok=n>=5&&r[0]==h[6]&&crc(r,n-2)==(uint16_t)(r[n-2]|r[n-1]<<8);
 if(ok)ok=(r[1]==(p[0]|0x80)&&n==5)||(r[1]==p[0]&&((p[0]==6&&n==8)||(p[0]==3&&n==5+2*p[4]&&r[2]==2*p[4])));
 if(!ok){r[0]=h[6];r[1]=p[0]|0x80;r[2]=valid?11:1;n=5;}
 h[4]=0;h[5]=n-2;c.write(h,7);c.write(r+1,n-3);c.flush();c.stop();
}
