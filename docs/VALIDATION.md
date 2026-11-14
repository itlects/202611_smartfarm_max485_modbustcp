# 검증 기록

검증일: 2026-11-15 (한국시간).

| 항목 | 결과 |
|---|---|
| Python 3.13 런타임 | 실제 실행 |
| PyMySQL 1.1.2, cryptography 46.0.3 | Python 3.13 Linux 환경 설치·import 및 RSA 키 생성 성공 |
| 테스트 3개 | TCP 분할 수신, 잘못된 Transaction ID 거부, 웹 인증/제어/타이머 통합 시험 통과 |
| 로그인/제어 통합 세부 | 미인증401, 틀린 암호401, 정상 로그인200, UNO1 펌프쓰기400, 임계값101 거부, Demo 펌프10초 후OFF |
| 웹 JavaScript | node --check 구문검사 통과 |
| UNO 제어 로직 | g++ C++11 + Arduino 함수 대역으로 부팅OFF, ON 재전송시 타이머 미연장, 10초OFF, 통신5초 후 펌프/자동OFF 확인 |
| Arduino AVR / ESP32 실제 보드 컴파일 | 미실행: Arduino CLI/보드 코어 미설치 |
| RS-485 실물·펌프·센서 | 장비 미연결; RUNBOOK 실물 인수시험 필요 |
| Windows 3.13 / MySQL 실접속 | 미실행; 설치와 스키마/버전 확인 절차 제공 |
| 스마트폰 브라우저 실기기 | 미실행; 반응형 웹 제공, 네이티브 앱 없음 |

이 결과는 실물 시험 완료나 Windows/MySQL 8.0.48 호환성 인증을 의미하지 않습니다. Python 의존성의 Linux 3.13 실행 확인과 하드웨어 실접속은 구분합니다.

재현:

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

테스트 중 8000 포트는 비워 두세요. Demo 자동관개는 하드웨어 자동관개 로직을 모사하지 않고 API/UI 제어와 펌프 시간제한만 시험하는 용도입니다.
