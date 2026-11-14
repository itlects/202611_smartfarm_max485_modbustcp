// UNO1: NODE_ID=1; UNO2: NODE_ID=2. UART D0/D1 reserved for RS485.
#define NODE_ID 1
const byte DIR=2, LED1=3, LED2=4, BTN1=5, BTN2=6, PUMP=7, BUZZ=8, POWER=9;
uint16_t regs[8]={0,0,0,0,0,0,30,0};
byte rx[8]; byte used=0;
unsigned long lastByte=0,lastRead=0,pumpStart=0,sampleAt=0,changed[2]={0,0};
bool stable[2]={true,true},prev[2]={true,true},armed=false;
uint16_t crc(const byte* b, int n){uint16_t c=65535;while(n--){c^=*b++;for(byte i=0;i<8;i++)c=c&1?(c>>1)^0xA001:c>>1;}return c;}
void stopPump(){regs[4]=0;digitalWrite(PUMP,LOW);}
void startPump(){if(NODE_ID==2 && !regs[4]){regs[4]=1;pumpStart=millis();}}
void respond(byte* b, byte n){uint16_t c=crc(b,n);b[n++]=c;b[n++]=c>>8;digitalWrite(DIR,HIGH);delayMicroseconds(100);Serial.write(b,n);Serial.flush();digitalWrite(DIR,LOW);}
void process(){
 if(rx[0]!=NODE_ID || crc(rx,6)!=(uint16_t)(rx[6]|rx[7]<<8))return;
 byte f=rx[1],out[32]={NODE_ID,f};uint16_t a=word(rx[2],rx[3]),v=word(rx[4],rx[5]);byte err=0;
 if(f==3){if(v==0||v>8||a+v>8)err=2;else{out[2]=v*2;for(byte i=0;i<v;i++){out[3+2*i]=regs[a+i]>>8;out[4+2*i]=regs[a+i];}lastRead=millis();respond(out,3+v*2);return;}}
 else if(f==6){
  if(a<3||a>7||(NODE_ID==1&&(a==4||a==5||a==7)))err=2;
  else if((a==3&&v>3)||((a==4||a==5||a==7)&&v>1)||(a==6&&v>100))err=3;
  else{if(a==4){if(v)startPump();else stopPump();}else regs[a]=v;for(byte i=0;i<6;i++)out[i]=rx[i];respond(out,6);return;}
 }else err=1;
 out[1]=f|0x80;out[2]=err;respond(out,3);
}
void setup(){
 const byte pins[]={DIR,LED1,LED2,PUMP,BUZZ,POWER};
 for(byte i=0;i<6;i++)pinMode(pins[i],OUTPUT);
 pinMode(BTN1,INPUT_PULLUP);pinMode(BTN2,INPUT_PULLUP);
 digitalWrite(DIR,LOW);stopPump();Serial.begin(9600);
}
void loop(){
 unsigned long now=millis();
 if(used && now-lastByte>10)used=0;
 while(Serial.available()){rx[used++]=Serial.read();lastByte=now;if(used==8){process();used=0;}}
 // Power sensor for 20ms once per second to reduce probe corrosion.
 if(NODE_ID==2&&now-sampleAt>=1000){sampleAt=now;digitalWrite(POWER,HIGH);}
 if(digitalRead(POWER)&&now-sampleAt>=20){regs[0]=analogRead(A0);regs[1]=constrain(map(regs[0],850,350,0,100),0,100);digitalWrite(POWER,LOW);}
 bool link=lastRead && now-lastRead<5000;
 if(NODE_ID==2&&(regs[0]<10||regs[0]>1013)){stopPump();regs[7]=0;}
 if(!link){stopPump();regs[7]=0;armed=false;}
 if(regs[4]&&now-pumpStart>=10000){stopPump();armed=false;}
 if(regs[1]>=regs[6]+5)armed=true;
 if(NODE_ID==2&&link&&regs[7]&&armed&&regs[1]<regs[6]){startPump();armed=false;}
 for(byte i=0;i<2;i++){
  bool b=digitalRead(i?BTN2:BTN1);
  if(b!=prev[i]){prev[i]=b;changed[i]=now;}
  if(now-changed[i]>=40&&b!=stable[i]){stable[i]=b;if(!b){if(NODE_ID==1)regs[3]^=(1<<i);else if(i==0&&link)startPump();else{stopPump();regs[7]=0;}}}
 }
 regs[2]=(!stable[0])|((!stable[1])<<1);
 digitalWrite(LED1,regs[3]&1);digitalWrite(LED2,regs[3]&2);
 if(NODE_ID==2&&regs[5]&&link)tone(BUZZ,2000);else noTone(BUZZ);
}
