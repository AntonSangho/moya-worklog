# Moya Worklog ESP32 포트

Raspberry Pi/Odroid용 Moya Worklog를 ESP32-P4-Nano로 포팅한 버전입니다.

## 하드웨어 요구사항

- **ESP32-P4-Nano** 개발보드
- **ESC/POS 호환 열화상 프린터**
  - Sam4s Giant 100 (USB ID: 0x1c8a:0x3a0e)
  - Bixolon SRP-330II (USB ID: 0x1504:0x006e)
- **버튼 및 LED**
  - 프린트 버튼 (GPIO 21)
  - 상태 LED (GPIO 2)
  - 리셋 버튼 (GPIO 3)

## 핀 맵핑

```
ESP32-P4-Nano 핀 구성:
- GPIO 21: 프린트 버튼 (Pull-down 저항)
- GPIO 2:  상태 LED
- GPIO 3:  리셋 버튼 (Pull-up 저항)
- USB:     프린터 통신 (Serial)
```

## 설치 및 설정

### 1. 개발 환경 설정

```bash
# PlatformIO 설치 (VS Code Extension 또는 CLI)
pip install platformio

# 프로젝트 디렉토리로 이동
cd esp32
```

### 2. 이미지 변환 및 준비

```bash
# Python 이미지 변환 스크립트 실행
python3 setup_images.py
```

이 스크립트는:
- `../image/` 디렉토리의 PNG 파일들을 열화상 프린터용 바이너리로 변환
- SPIFFS 파일시스템용 `data/` 디렉토리 생성
- 변환된 이미지 파일들을 `data/` 디렉토리에 저장

### 3. 펌웨어 빌드 및 업로드

```bash
# 메인 프로그램 빌드 및 업로드
pio run --target upload

# SPIFFS 파일시스템 업로드 (이미지 데이터)
pio run --target uploadfs
# 또는
./upload_spiffs.sh
```

### 4. 시리얼 모니터

```bash
# 시리얼 모니터로 디버그 정보 확인
pio device monitor
```

## 주요 기능

### 기본 동작
1. **버튼 프레스**: GPIO 21번 핀의 버튼을 누르면 랜덤 worklog 이미지 출력
2. **디바운싱**: 2초 간격으로 중복 프린트 방지
3. **상태 LED**: GPIO 2번 핀으로 시스템 상태 표시
4. **리셋 기능**: GPIO 3번 핀으로 시스템 재시작

### 프린터 지원
- **ESC/POS 명령어** 완전 지원
- **이미지 출력**: 480x1000px 열화상 프린터 최적화
- **자동 용지 커팅**: 출력 후 자동 커팅
- **프린터 감지**: USB 연결된 프린터 자동 감지

### 이미지 처리
- **PNG → 바이너리 변환**: PIL을 사용한 고품질 변환
- **Floyd-Steinberg 디더링**: 모노크롬 변환 시 화질 최적화
- **SPIFFS 저장**: 플래시 메모리에 이미지 저장
- **랜덤 선택**: 5개 이미지 중 랜덤 선택

## 파일 구조

```
esp32/
├── moya_worklog_esp32.ino          # 메인 ESP32 코드
├── libraries/ThermalPrinter/       # 열화상 프린터 라이브러리
│   ├── ThermalPrinter.h
│   └── ThermalPrinter.cpp
├── image_converter.py              # PNG → 바이너리 변환기
├── setup_images.py                 # 이미지 설정 스크립트
├── platformio.ini                  # PlatformIO 설정
├── custom_partitions.csv           # 파티션 테이블
├── upload_spiffs.sh               # SPIFFS 업로드 스크립트
├── data/                          # SPIFFS 데이터 (생성됨)
│   ├── w1_2022.bin
│   ├── w2_2022.bin
│   ├── w3_2022.bin
│   ├── w4_2022.bin
│   ├── w5_2022.bin
│   └── filelist.txt
└── README.md
```

## 개발자 정보

### 원본 Python 버전에서 변경된 사항

1. **GPIO 라이브러리**: `RPi.GPIO` → ESP32 내장 GPIO
2. **이미지 처리**: `PIL` → 사전 변환된 바이너리
3. **프린터 통신**: `python-escpos` → 커스텀 ThermalPrinter 클래스
4. **파일 시스템**: 로컬 파일 → SPIFFS
5. **메모리 관리**: Python GC → ESP32 힙 관리

### 성능 특성

- **부팅 시간**: ~3초
- **프린트 시간**: ~10-15초 (이미지 크기에 따라)
- **메모리 사용량**: ~150KB RAM, ~1.4MB Flash
- **이미지 저장**: 최대 5개 이미지 (각 ~60KB)

## 문제 해결

### 일반적인 문제들

1. **프린터가 감지되지 않음**
   - USB 케이블 연결 확인
   - 프린터 전원 확인
   - 시리얼 모니터에서 에러 메시지 확인

2. **이미지가 출력되지 않음**
   - SPIFFS 업로드 확인: `pio run --target uploadfs`
   - 이미지 변환 오류 확인: `python3 setup_images.py`

3. **버튼이 반응하지 않음**
   - 버튼 배선 확인 (GPIO 21, Pull-down)
   - 디바운스 시간 확인 (2초 대기)

4. **시스템 재시작**
   - 메모리 부족: 이미지 크기 확인
   - 전원 공급 확인

### 디버깅

```bash
# 상세 로그 확인
pio device monitor --filter esp32_exception_decoder

# SPIFFS 파일 시스템 확인
# ESP32 코드에서 SPIFFS.begin(true) 후 파일 목록 출력
```

## 라이센스

원본 Moya Worklog 프로젝트와 동일한 라이센스를 따릅니다.