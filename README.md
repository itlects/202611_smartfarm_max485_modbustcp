# 스마트팜: ESP32 Modbus TCP ↔ RS-485 Modbus RTU / UNO × 2

학생이 GitHub에서 내려받아 Windows 노트북에서 실행하는 교육용 프로젝트입니다. PC와 스마트폰 브라우저에서 동일한 반응형 웹앱에 접속합니다. 네이티브 Android/iOS 앱이나 설치형 PWA는 포함하지 않습니다.

## 구성

노트북 Python 서버 → Wi-Fi/TCP 502 → ESP32 게이트웨이 → RS-485 9600bps 8N1 → UNO1(ID 1), UNO2(ID 2).
MAX485는 전기적 신호 변환기이며 TCP를 직접 처리하지 않습니다. ESP32가 MBAP 헤더를 RTU 프레임과 CRC로 변환합니다. FC03(읽기), FC06(단일 레지스터 쓰기)만 지원하는 수업용 구현입니다. 서버만 게이트웨이에 접속하며 학생 브라우저는 서버의 HTTP API를 사용합니다.

- UNO1: LED 2개, 버튼 2개.
- UNO2: LED 2개, 버튼 2개, 토양수분 센서 1개, 수동 부저 1개, 펌프 1개.
- 모듈 3개 필요: UNO마다 MAX485 5V 1개, ESP32에는 MAX3485 3.3V 1개 권장.
- 사진은 아날로그 센서+비교기 모듈로 보입니다. 실제 AO/DO/VCC/GND 표기를 확인하세요. AO를 사용합니다. 사진만으로 펌프 정격·릴레이 극성·센서 소비전류를 확정할 수 없습니다.

[배선·부품·레지스터](docs/HARDWARE.md) · [설치·학생 접속·문제해결](docs/RUNBOOK.md) · [검증 결과](docs/VALIDATION.md)

## 빠른 실행 (PowerShell / Python 3.13)

```powershell
git clone https://github.com/itlects/202611_smartfarm_max485_modbustcp.git
cd 202611_smartfarm_max485_modbustcp
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:FARM_MODE='demo'
.\.venv\Scripts\python.exe server.py
```

http://localhost:8000 에서 로그인합니다. ID `smartfarm2026`, 비밀번호 `smartfarm1234`.
Demo는 실제 장치/DB와 연결하지 않습니다. 실제 모드는 RUNBOOK의 DB 준비와 펌웨어 업로드를 완료한 뒤 실행하세요. 실제 모드에서 통신이 끊겨도 가상값으로 대체하지 않습니다.

## 구현 범위

센서 조회(2초 간격), 버튼 상태, LED 비트마스크 제어, 수동 10초 급수, 임계값 설정, 자동관개, 부저 제어, MySQL 측정/명령 기록, 최근 100건 조회. 공유 계정이므로 학생별 식별은 하지 않습니다. 측정기록은 계속 누적되므로 학기 종료 후 보관/삭제 정책을 정하세요.

기본 바인딩은 127.0.0.1입니다. 강의실 공유 시에만 FARM_BIND=0.0.0.0으로 바꾸고 노트북의 사설 IPv4를 사용하세요. HTTP 및 Modbus TCP는 암호화되지 않습니다. 신뢰하는 수업용 LAN에서 사용하고 인터넷 포트포워딩은 하지 마세요. 외부 서비스는 HTTPS 역방향 프록시, 개별 계정, 속도 제한과 별도 배포 구성이 필요합니다.

## 참고 원문

- [MAX485: 5V 전원](https://www.analog.com/en/products/max485.html)
- [MAX3485: 3.3V 전원](https://www.analog.com/en/products/max3485.html)
- [Modbus 공식 사양](https://www.modbus.org/specs.php)
- [Arduino UNO R3](https://docs.arduino.cc/hardware/uno-rev3/)
- [Arduino ESP32 설치](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
- [Modbus 라이브러리와 브리지 예제 학습](https://github.com/emelianov/modbus-esp8266)
- [Python Windows 설치](https://docs.python.org/3.13/using/windows.html)
- [MySQL 8.0 공식 릴리스](https://dev.mysql.com/doc/relnotes/mysql/8.0/en/)

본 저장소 Modbus 코드는 외부 Arduino Modbus 라이브러리에 의존하지 않는 최소 구현입니다.
