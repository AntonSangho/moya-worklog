## 프로젝트 설명
<img width="50%" src="https://user-images.githubusercontent.com/8589992/174252878-1f55046e-c069-4821-acf7-9d2b71925bf2.jpg" />

라즈베리파이로 작업일지 이미지를 영수증 프린터로 출력하는 장치.

---

## Wiring

<img src="/hardware/schematic/Wiring_v1.jpg" width="40%" alt="Raspberry Pi Wiring"></img>

## Pin Map

| Name | GPIO# |
| ----------- | ----------- |
| Reset Button GPIO | 3 |
| Reset Button Active | GND |
| Power LED Positive | 6 |
| Power LED Negative | GND |
| Print Button GPIO | 4 |
| Print Button LED | 20 |

[GPIO 핀맵 참고](https://pinout.xyz/)

---

## BOM

| 부품명 | 수량 |
| ----------- | ----------- |
| 라즈베리파이 3A+ | 1ea |
| Sam4s Giant 100 | 1ea |
| 2.5A 전원 아답터 | 1ea |
| 납작소켓 커넥터 와이어 | 2ea |
| 1K ohm 저항 | 2ea |
| 100nF 커패시터 (104) | 1ea |
| 60mm LED 아케이드 버튼 스위치 (SZH-LC043) | 1ea |

---

## 설치 방법

**지원 환경**: Raspberry Pi OS 64-bit Lite (Bookworm)  
**특징**: 스레드 방식, 이미지 캐싱, USB 자동 재연결, systemd 서비스

### 1. 라즈베리파이 이미지 굽기 (Raspberry Pi Imager)

[Raspberry Pi Imager](https://www.raspberrypi.com/software/) 다운로드 후 실행

- OS 선택: `Raspberry Pi OS (other)` → `Raspberry Pi OS Lite (64-bit)`
- Storage 선택: SD카드 선택

**OS Customisation 에서 반드시 설정 (NEXT 클릭 후 Edit Settings):**

| 항목 | 설정값 |
|------|--------|
| hostname | `raspberrypi` |
| username | `pi` |
| password | 원하는 비밀번호 |
| SSH | Enable (Use password authentication) |

> ⚠️ username을 `pi` 이외의 값으로 설정하면 서비스 파일 경로(`/home/pi/...`)와  
> 맞지 않아 실행 오류가 발생합니다. username은 반드시 `pi`로 설정하세요.

### 2. GPIO 활성화

```bash
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
echo "dtparam=gpio=on" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

### 3. 프로젝트 다운로드

```bash
git clone https://github.com/AntonSangho/moya-worklog.git
cd moya-worklog
```

### 4. 시스템 패키지 설치

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-dev python3-pip python3-venv python3-setuptools
sudo apt install -y libffi-dev libjpeg-dev zlib1g-dev libusb-1.0-0-dev
sudo apt install -y python3-rpi.gpio usbutils
```

### 5. USB 권한 설정

```bash
sudo tee /etc/udev/rules.d/99-sam4s-printer.rules << EOF
SUBSYSTEM=="usb", ATTR{idVendor}=="1c8a", ATTR{idProduct}=="3a0e", MODE="0666", GROUP="lp"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 6. Python 가상환경 및 패키지 설치

```bash
python3 -m venv venv-64bit
source venv-64bit/bin/activate
pip install --upgrade pip
pip install -r requirements-64bit.txt
```

### 7. 테스트 실행

```bash
source venv-64bit/bin/activate
python3 print_sam4s_production.py
```

### 8. systemd 서비스 등록 (부팅 자동 실행)

```bash
sudo cp moya-printer.service /etc/systemd/system/moya-printer.service
sudo systemctl daemon-reload
sudo systemctl enable moya-printer.service
sudo systemctl start moya-printer.service
```

상태 확인:
```bash
sudo systemctl status moya-printer.service
journalctl -u moya-printer.service -f
```

---

## 동작 방법

1. 라즈베리파이 전원 연결
2. LED에 불이 들어오면 준비 완료
3. 버튼을 누르면 랜덤 작업일지 출력

---

## 작업일지 이미지 만드는 법 (Illustrator 2022 기준)

1. `작업일지_원본.ai` 파일 열기
2. 내보내기 → 내보내기 형식
3. 파일명 수정
4. 대지사용 체크 후 범위 설정
5. 내보내기
6. 해상도: 고(300ppi) / 앤티앨리어싱: 아트최적화 / 배경색: 흰색

---

## 파일 구조

```
moya-worklog/
├── print_sam4s_production.py  # 메인 스크립트 (64-bit, 스레드 방식)
├── moya-printer.service       # systemd 서비스 파일
├── requirements-64bit.txt     # 패키지 목록
├── image/                     # 출력 이미지 (PNG)
├── hardware/
│   ├── schematic/             # 회로도, 배선도
│   └── drawing/               # 기구 도면
├── docs/
│   └── maintenance-odroid-c4.md  # Odroid C4 유지보수 가이드
├── legacy/                    # 구버전 코드
│   └── odroid/
└── pi-power-button/           # 전원 버튼 스크립트
```

---

## 시스템 요구사항

- **하드웨어**: Raspberry Pi 3B+ / 4B 이상
- **OS**: Raspberry Pi OS 64-bit Lite (Bookworm)
- **메모리**: 1GB 이상
- **저장공간**: 8GB 이상
- **Python**: 3.11 이상

---

## 문제 확인 프로세스

하드웨어 문제와 소프트웨어 문제를 단계적으로 분리한다.

```
[1] 전원 연결 → PWR LED(빨강) 점등?
        │ NO  → 전원 어댑터/케이블 점검 (HW)
        │ YES
        ↓
[2] ACT LED(녹색) 깜박임?
        │ NO  → SD카드 불량 또는 OS 손상 (HW)
        │ YES
        ↓
[3] SSH 접속 가능?
        │ NO  → 네트워크 설정 확인 (SW)
        │ YES
        ↓
[4] 서비스 실행 중?
        │ NO  → 서비스 재시작 (SW)
        │ YES
        ↓
[5] 프린터 USB 인식?
        │ NO  → USB 케이블/프린터 점검 (HW)
        │ YES
        ↓
[6] 버튼 LED 점등 + 버튼 동작?
        │ NO  → GPIO 배선/설정 점검 (HW/SW)
        │ YES
        ↓
    정상 동작
```

---

### 1단계 — 전원 확인 (HW)

라즈베리파이 3A+는 **Micro USB 5V 2.5A** 어댑터로 전원을 공급한다.

- 빨간 **PWR LED** 점등 확인
- 미점등 시: 어댑터 규격 확인 (5V / 2.5A 이상), 케이블 단선 확인

---

### 2단계 — 부팅 확인 (HW/SW)

| 증상 | 원인 | 조치 |
|------|------|------|
| PWR만 켜지고 ACT 없음 | SD카드 미삽입 또는 불량 | SD카드 재삽입 또는 OS 재설치 |
| ACT 깜박이다 멈춤 | OS 손상 또는 파일시스템 오류 | OS 재설치 |
| ACT 규칙적으로 깜박임 | 정상 부팅 중 | 30초 대기 후 3단계로 |

---

### 3단계 — SSH 접속 확인 (SW)

```bash
ssh pi@raspberrypi.local
# 또는 IP로 직접 접속
ssh pi@<IP주소>
```

| 증상 | 원인 | 조치 |
|------|------|------|
| `Connection refused` | SSH 미활성화 또는 부팅 미완료 | 30초 더 대기 후 재시도 |
| `Host not found` | 네트워크 미연결 | LAN 케이블 또는 WiFi 확인 |
| 비밀번호 오류 | 이미지 굽기 시 설정값 확인 | Raspberry Pi Imager로 재설치 |

---

### 4단계 — 서비스 확인 (SW)

```bash
sudo systemctl status moya-printer.service
```

| 상태 | 조치 |
|------|------|
| `active (running)` | 정상, 5단계로 |
| `failed` | 로그 확인 후 재시작 |
| `inactive` | `sudo systemctl start moya-printer.service` |

로그 확인:

```bash
journalctl -u moya-printer.service -n 50
```

서비스 재시작:

```bash
sudo systemctl restart moya-printer.service
```

---

### 5단계 — 프린터 USB 확인 (HW/SW)

```bash
lsusb | grep 1c8a
```

- 출력 있음 (`1c8a:3a0e`) → 정상, 6단계로
- 출력 없음 → 아래 순서로 점검:

1. 프린터 전원 ON 확인
2. USB 케이블 재연결
3. `dmesg | tail -20` 으로 USB 인식 오류 확인

서비스 재시작으로 프린터 재연결:

```bash
sudo systemctl restart moya-printer.service
```

---

### 6단계 — 버튼 동작 확인 (HW/SW)

서비스가 시작되면 GPIO20 LED가 켜진다. LED가 꺼져 있으면 서비스 이상이다.

**프린트 버튼 GPIO 직접 테스트:**

```bash
source ~/moya-worklog/venv-64bit/bin/activate
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print('버튼 상태:', GPIO.input(4))
GPIO.cleanup()
"
```

버튼을 누른 채로 실행하면 `1`, 떼면 `0`이 출력되어야 한다.

> **주의**: GPIO2(SDA), GPIO3(SCL)는 하드웨어 풀업이 내장되어 항상 `1`을 반환한다.  
> 프린트 버튼은 반드시 **GPIO4** 에 연결한다.

| 결과 | 원인 | 조치 |
|------|------|------|
| 항상 `0` | 정상 (미입력) | 버튼 누르면서 재테스트 |
| 항상 `1` | GPIO2/3 연결 또는 배선 쇼트 | GPIO4 핀으로 재연결 |
| 버튼 눌러도 변화 없음 | 배선 오류 | 핀맵 재확인 |

---

## 업데이트 이력

- **2026.05 (v2.1.0)**: Odroid C4 코드 개선 (로그 로테이션, 이미지 캐싱, USB 재연결, 스레드 방식), 문제 확인 프로세스 추가
- **2026.05 (v2.0.0)**: Odroid C4 → Raspberry Pi 3 이식, 성능/안정성 대폭 개선
- **2025.08 (v1.0.0)**: 64-bit Raspberry Pi OS 지원, systemd 서비스, AI 에이전트 설치 가이드

> Odroid C4 관련 문서는 [docs/maintenance-odroid-c4.md](./docs/maintenance-odroid-c4.md) 참고

---

## 연락처

sanghoemail@gmail.com
