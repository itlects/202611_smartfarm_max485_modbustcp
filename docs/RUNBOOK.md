# Windows 노트북 실행 및 학생 접속

## 1. 소스와 Python

README의 git clone 및 가상환경 설치 명령을 실행합니다. PowerShell 실행정책 변경 없이 .venv의 python.exe를 직접 호출할 수 있습니다. `py -3.13 --version`으로 버전을 확인합니다.

## 2. MySQL 준비

요청 환경은 MySQL Community 8.0.48이지만 공식 Community 8.0 릴리스 문서는 8.0.46까지, 8.0.48은 NDB Cluster 문서에서 확인됩니다. 설치 파일의 제품명을 확인하고 아래 결과를 기준으로 실제 버전을 기록하세요. 프로그램은 MySQL 8.0 호환 SQL을 사용합니다. 이 프로젝트에서 8.0.48 서버 실접속 검증은 하지 않았습니다.

MySQL Workbench에서 root로 접속해 `SELECT VERSION();`을 실행한 뒤 schema.sql 전체를 실행합니다. 별도 쿼리 탭에서 전용 DB 사용자를 만듭니다. 웹 학생 계정과 DB 계정은 다릅니다.

```sql
CREATE USER IF NOT EXISTS 'smartfarm'@'localhost' IDENTIFIED BY '여기에별도DB암호';
GRANT SELECT, INSERT ON smartfarm.* TO 'smartfarm'@'localhost';
```

root 암호는 저장소나 학생에게 배포하지 않습니다. 기존 smartfarm DB 사용자가 있다면 암호를 확인하거나 관리자가 ALTER USER로 변경하세요.

## 3. 펌웨어 업로드

Arduino IDE에서 Arduino AVR Boards의 Arduino Uno를 선택합니다. firmware/uno_node/uno_node.ino의 NODE_ID를 1로 하여 UNO1에, 2로 하여 UNO2에 업로드합니다. 매번 D0/D1 통신 배선을 분리한 뒤 업로드하고 다시 연결합니다.

ESP32는 Espressif 공식 Arduino ESP32 보드 패키지를 설치하고 해당 DevKit 보드(일반 WROOM은 ESP32 Dev Module)를 선택합니다. firmware/esp32_gateway/esp32_gateway.ino에서 Wi-Fi SSID/PASS만 로컬에서 수정하여 업로드합니다. 같은 2.4GHz LAN에 연결하고 공유기 DHCP 목록에서 ESP32 IP를 확인해 DHCP 예약을 권장합니다. Wi-Fi 암호가 들어간 수정본은 공개 저장소에 올리지 마세요.

## 4. 실제 장치 실행

```powershell
$env:FARM_MODE='hardware'
$env:ESP32_HOST='192.168.1.50'
$env:DB_HOST='127.0.0.1'
$env:DB_USER='smartfarm'
$env:DB_PASSWORD='여기에별도DB암호'
$env:FARM_USER='smartfarm2026'
$env:FARM_PASSWORD='smartfarm1234'
$env:FARM_BIND='0.0.0.0'
.\.venv\Scripts\python.exe server.py
```

DB에 연결할 수 없으면 실제 모드 서버가 시작되지 않습니다. 시작 로그의 MySQL 버전을 확인하세요. .env.example은 설정 설명용이며 자동으로 읽지 않습니다. 환경변수는 실행할 PowerShell 창에서 설정합니다.

## 5. 학생 PC/앱 접속

노트북에서 ipconfig를 실행해 Wi-Fi의 IPv4 주소를 확인합니다. 예: 192.168.1.20이면 PC/휴대폰 브라우저에서 `http://192.168.1.20:8000`으로 접속합니다. 학생 계정 `smartfarm2026` / `smartfarm1234`.

같은 LAN에서 접속해야 하며 Windows 방화벽에서 개인 네트워크의 Python 또는 TCP 8000 수신을 허용합니다. 공용 네트워크 전체 허용은 피하세요. 게스트 Wi-Fi/AP 격리가 켜져 있으면 학생↔노트북 통신이 차단될 수 있습니다. MySQL 3306과 ESP32 502는 학생 단말에 개방할 필요가 없습니다. 휴대폰은 브라우저 즐겨찾기/홈 화면 바로가기로 사용할 수 있으며 별도 APK는 없습니다.

## 6. 단계별 실습

1. Demo로 로그인, LED 버튼, 10초 급수와 최근 기록 버튼을 확인합니다(Demo 기록은 DB에 저장하지 않음).
2. 펌프 전원을 빼고 UNO1/2 온라인, 버튼 비트와 LED를 확인합니다.
3. UNO2 센서 값을 건조/습윤 조건에서 측정해 보정합니다.
4. 펌프 외부 전원과 다이오드/풀다운을 확인한 뒤 물을 넣어 수동 급수합니다.
5. PC 서버 종료 또는 RS-485 분리 후 5초 내 펌프가 정지하는지 확인합니다.
6. 수분 회복→기준 미만 변화에서 자동급수 1회, 10초 상한을 확인합니다.
7. Workbench에서 `SELECT * FROM smartfarm.events ORDER BY id DESC LIMIT 20;`으로 기록을 확인합니다.

실제 모드는 2초마다 두 노드를 순서대로 읽습니다. 오프라인 노드는 timeout 때문에 조회 주기가 길어질 수 있습니다. UI의 연결 끊김을 정상 수분값으로 해석하지 마세요. 자동모드는 통신 복구 후 다시 켜야 합니다.

## 문제해결

| 증상 | 확인 |
|---|---|
| UNO 업로드 실패 | D0/D1 분리, 보드/COM 포트 확인 |
| 노드 연결 끊김 | ID 중복, 9600 8N1, A/B, 공통GND, DE//RE, 종단/바이어스 |
| ESP32 연결 불가 | Wi-Fi SSID, 2.4GHz, IP, UART16/17 점유 여부 |
| DB 오류 | MySQL 서비스, 실제 버전, DB_PASSWORD, localhost 권한, schema.sql |
| 펌프가 안 켜짐 | 외부 3.3V, MOSFET 방향, 공통GND, 정상 FC03 통신과 ADC 범위 |
| 자동급수 안 됨 | 자동 켜기, 수분 회복+5 후 하강 조건, 센서 보정 |
| 스마트폰 연결 실패 | 노트북 IP, 동일 LAN, 방화벽8000, AP 격리 |

공유 계정으로 접속한 학생 모두 제어할 수 있으므로 수업 중 제어 담당을 정하세요. 이 버전에는 교사/학생 권한 분리가 없습니다.
