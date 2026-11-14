# GitHub 다운로드부터 실행까지

## 1. 계정과 접속 위치

| 구분 | 아이디 | 비밀번호 | 사용하는 위치 |
|---|---|---|---|
| 노트북 MySQL 서버 | root | 1234 | MySQL Workbench / Python 서버의 DB 연결 |
| 학생·사용자 웹 | smartfarm2026 | smartfarm1234 | PC·휴대폰 관제 로그인 화면 |

웹 사용자는 MySQL 계정을 입력하지 않습니다. Python 서버가 노트북의 MySQL에 접속하고, 학생은 웹 화면에 로그인합니다. 아래 절차는 기존 MySQL root 암호가 1234인 환경을 사용하며 암호를 변경하지 않습니다.

## 2. 준비 프로그램 확인

Windows 10/11에서 PowerShell을 엽니다. 명령 프롬프트(cmd)가 아닌 PowerShell 기준입니다.

```powershell
py -3.13 --version
git --version
```

Python 3.13.x와 Git 버전이 표시되면 준비된 상태입니다.

- [Python 3.13 Windows 설치 안내](https://docs.python.org/3.13/using/windows.html)
- [Git for Windows 설치](https://git-scm.com/downloads/win)
- MySQL Server와 Workbench는 설치된 것을 사용합니다. Workbench는 관리 도구이며 MySQL 서버 서비스가 실행되어야 합니다.
- Git을 설치하지 않아도 다음 ZIP 다운로드 방식으로 진행할 수 있습니다.

## 3. GitHub 프로젝트 다운로드

[프로젝트 저장소 열기](https://github.com/itlects/202611_smartfarm_max485_modbustcp)

### 방법 A: Git으로 다운로드

처음 한 번 실행합니다. 작업 폴더가 이미 있으면 다른 빈 폴더를 사용하세요.

```powershell
New-Item -ItemType Directory -Force C:\works | Out-Null
Set-Location C:\works
git clone https://github.com/itlects/202611_smartfarm_max485_modbustcp.git
Set-Location C:\works\202611_smartfarm_max485_modbustcp
Get-ChildItem
```

### 방법 B: ZIP으로 다운로드

1. 저장소의 초록색 Code 버튼을 누릅니다.
2. Download ZIP을 선택합니다.
3. 다운로드한 파일에서 마우스 오른쪽 버튼 → 모두 압축 풀기를 선택합니다.
4. 압축을 푼 폴더를 C:\works 아래로 옮깁니다.
5. server.py가 있는 폴더에서 PowerShell을 엽니다. 폴더명이 202611_smartfarm_max485_modbustcp-main이면 아래처럼 이동합니다.

```powershell
Set-Location C:\works\202611_smartfarm_max485_modbustcp-main
Get-ChildItem
```

이후 모든 명령은 server.py와 requirements.txt가 있는 프로젝트 최상위 폴더에서 실행합니다.

| 파일·폴더 | 역할 |
|---|---|
| server.py | Python 웹 서버와 MySQL 기록 |
| modbus.py | ESP32 Modbus TCP 연결 |
| requirements.txt | Python 의존성 |
| schema.sql | smartfarm DB와 events 테이블 생성 |
| web/index.html | PC·모바일 관제 화면 |
| firmware/uno_node/uno_node.ino | UNO1/UNO2 펌웨어 |
| firmware/esp32_gateway/esp32_gateway.ino | ESP32 게이트웨이 |
| docs | 배선·실행·검증 문서 |

## 4. Python 3.13 가상환경과 라이브러리 설치

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import pymysql, cryptography; print('라이브러리 설치 확인 완료')"
```

가상환경 활성화 명령 없이 python.exe를 직접 실행하므로 PowerShell 실행정책을 바꿀 필요가 없습니다.

## 5. 먼저 Demo로 웹 로그인 확인

하드웨어와 MySQL 없이 화면을 확인할 때 실행합니다.

```powershell
$env:FARM_MODE='demo'
$env:FARM_BIND='127.0.0.1'
$env:FARM_USER='smartfarm2026'
$env:FARM_PASSWORD='smartfarm1234'
.\.venv\Scripts\python.exe server.py
```

브라우저에서 http://localhost:8000 을 열고 smartfarm2026 / smartfarm1234로 로그인합니다. 화면에 시뮬레이션 표시가 나와야 합니다. Demo에서는 실제 펌프가 작동하지 않고 DB에 기록하지 않습니다.

다음 단계로 넘어갈 때 서버 PowerShell에서 Ctrl+C를 눌러 종료합니다.

## 6. MySQL root / 1234 접속 및 DB 생성

MySQL Workbench 실행 → MySQL Connections의 + → 다음 값으로 연결을 만듭니다.

| 항목 | 값 |
|---|---|
| Connection Name | Smartfarm Local |
| Connection Method | Standard (TCP/IP) |
| Hostname | 127.0.0.1 |
| Port | 3306 |
| Username | root |
| Password | Store in Vault에서 1234 입력 |

Test Connection 성공 후 접속합니다. SQL 탭에서 실행합니다.

```sql
SELECT VERSION();
```

File → Open SQL Script에서 다운로드한 프로젝트의 schema.sql을 열고 전체 실행합니다. 또는 새 SQL 탭에 다음 내용을 붙여넣고 전체 실행합니다.

```sql
CREATE DATABASE IF NOT EXISTS smartfarm CHARACTER SET utf8mb4;
USE smartfarm;
CREATE TABLE IF NOT EXISTS events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    kind VARCHAR(24) NOT NULL,
    unit TINYINT NOT NULL,
    payload JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at(created_at)
);
SHOW TABLES;
```

events가 표시되면 완료입니다. 이번 실행에서는 기존 root를 사용하므로 별도 smartfarm DB 사용자를 만들지 않습니다. root 암호를 SQL로 재설정할 필요도 없습니다.

실제 설치 버전은 SELECT VERSION() 결과를 기준으로 기록합니다. MySQL 8.0.48 설치 제품명 확인에 관한 설명은 메인 페이지를 참고하세요.

### Python에서 DB 연결만 확인

프로젝트 폴더 PowerShell에서 실행합니다.

```powershell
$env:DB_HOST='127.0.0.1'
$env:DB_USER='root'
$env:DB_PASSWORD='1234'
.\.venv\Scripts\python.exe -c "from server import database; db=database(); print('DB 연결 성공:', db.host); db.close()"
```

## 7. UNO 2개와 ESP32 준비

배선은 별도 배선 페이지를 따릅니다. Arduino IDE에서 다음 순서로 업로드합니다.

1. UNO1: uno_node.ino의 NODE_ID를 1로 설정하여 업로드합니다.
2. UNO2: 같은 파일의 NODE_ID를 2로 설정하여 업로드합니다.
3. UNO 업로드 중에는 D0/D1의 MAX485 배선을 분리하고 완료 후 다시 연결합니다.
4. ESP32: esp32_gateway.ino에서 SSID와 PASS를 실제 2.4GHz Wi-Fi 정보로 바꾸고 업로드합니다.
5. 공유기 DHCP 목록에서 ESP32 IP를 확인합니다. 아래 예시 192.168.1.50은 실제 주소로 바꿔야 합니다.
6. 처음에는 펌프 전원을 분리하고 통신·LED·센서부터 확인합니다.

[배선·부품·Modbus 레지스터 안내](https://app.notion.com/p/418b2e6bf807810ca36ac50b35c8a74b)

## 8. 실제 장치 + MySQL 모드로 실행

Demo 서버를 Ctrl+C로 종료한 뒤 같은 PowerShell에서 실행합니다.

```powershell
$env:FARM_MODE='hardware'
$env:ESP32_HOST='192.168.1.50'
$env:DB_HOST='127.0.0.1'
$env:DB_USER='root'
$env:DB_PASSWORD='1234'
$env:FARM_USER='smartfarm2026'
$env:FARM_PASSWORD='smartfarm1234'
$env:FARM_BIND='0.0.0.0'
.\.venv\Scripts\python.exe server.py
```

ESP32_HOST만 현장의 실제 ESP32 IP로 수정합니다. MySQL 버전과 hardware 모드가 로그에 표시되고 서버가 대기하면 노트북에서 http://localhost:8000 을 엽니다.

- 로그인: smartfarm2026 / smartfarm1234
- 화면: 실제 장치 모드
- UNO1: 입출력 노드 온라인
- UNO2: 수분과 펌프 상태 표시
- 노드가 오프라인이면 ESP32 IP, RS-485 배선, 노드 ID, 전원을 점검합니다.

환경변수는 설정한 PowerShell 창과 그 창에서 실행한 프로그램에 적용됩니다. 새 PowerShell을 열면 위 설정 블록을 다시 실행합니다. .env.example은 예시이며 자동으로 로드되지 않습니다.

## 9. 학생 PC와 휴대폰에서 접속

서버를 실행한 PowerShell 창은 열어 둡니다. 별도 PowerShell을 열어 실행합니다.

```powershell
ipconfig
```

노트북 Wi-Fi의 IPv4 주소를 확인합니다. 예를 들어 192.168.1.20이면 학생 브라우저 주소창에 http://192.168.1.20:8000 을 입력합니다. localhost나 0.0.0.0을 학생 접속 주소로 사용하지 않습니다.

| 접속 위치 | 주소 예시 | 로그인 |
|---|---|---|
| 서버 노트북 | http://localhost:8000 | smartfarm2026 / smartfarm1234 |
| 학생 PC | http://192.168.1.20:8000 | smartfarm2026 / smartfarm1234 |
| 학생 휴대폰 | http://192.168.1.20:8000 | smartfarm2026 / smartfarm1234 |

학생 단말과 노트북은 같은 LAN에 연결합니다. Windows 방화벽은 개인 네트워크에서 Python 또는 TCP 8000 수신을 허용합니다. 게스트 Wi-Fi의 AP 격리는 접속을 막을 수 있습니다. 학생에게 MySQL 3306을 열 필요는 없습니다.

모바일은 반응형 웹앱이며 별도 APK 설치 없이 브라우저에서 사용합니다. root / 1234는 노트북 DB 연결용이고 학생 웹 로그인에는 사용하지 않습니다. 공유 웹 계정으로 로그인한 사용자는 모두 제어할 수 있습니다.

## 10. 저장 확인과 종료·재실행

실제 모드로 센서 조회 또는 LED 제어 후 Workbench에서 실행합니다.

```sql
USE smartfarm;
SELECT id, kind, unit, payload, created_at
FROM events
ORDER BY id DESC
LIMIT 20;
```

sample은 측정, requested는 명령 요청, acknowledged는 장치 응답 확인 기록입니다.

종료 전 웹에서 펌프와 자동관개를 끄고 서버에서 Ctrl+C를 누릅니다. 재실행은 프로젝트 폴더를 열고 8단계 설정 블록을 실행합니다.

Git으로 받은 프로젝트를 업데이트할 때는 서버 종료 후 다음을 실행합니다. 로컬 수정이 있으면 먼저 보관하고 충돌을 확인하세요. ZIP 다운로드본에는 git pull을 사용하지 않습니다.

```powershell
git pull --ff-only
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 11. 자주 발생하는 오류

| 증상 | 조치 |
|---|---|
| py 명령 없음 | Python 3.13과 Windows Python 런처 설치 확인 |
| git 명령 없음 | Git 설치 후 PowerShell 재실행 또는 ZIP 방식 사용 |
| server.py 없음 | 압축파일 내부 중첩 폴더를 확인하고 server.py가 있는 폴더로 이동 |
| No module named pymysql | .venv의 python.exe로 requirements.txt 설치 후 같은 실행파일 사용 |
| Access denied for root | DB_USER=root, DB_PASSWORD=1234 설정과 Workbench 접속 확인 |
| Unknown database smartfarm | 6단계 SQL 전체 실행 |
| events 테이블 없음 | smartfarm DB에서 schema.sql 전체 실행 |
| MySQL 연결 거부 | MySQL 서버 서비스 실행, 127.0.0.1:3306 확인 |
| 8000 포트 사용 중 | 다른 서버 창을 Ctrl+C로 종료 |
| 웹 계정 오류 | FARM_USER/FARM_PASSWORD 설정 후 서버 재시작 |
| 화면이 계속 Demo | FARM_MODE=hardware 설정 후 서버 재시작 |
| 휴대폰 접속 실패 | 노트북 IP, 동일 LAN, FARM_BIND, 방화벽 8000 확인 |

이 안내는 실행 절차이며 사용자 노트북에서 MySQL 실접속이나 실물 동작을 원격으로 확인한 결과는 아닙니다.
