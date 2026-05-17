# Odroid C4 유지보수 가이드

> 현재 메인 플랫폼은 Raspberry Pi 3입니다.  
> 이 문서는 기존 Odroid C4 장비 유지보수를 위해 보관됩니다.

## Wiring

<img src="/hardware/schematic/moya-worklog_OdroidC4_v1_bb.png" width="60%" alt="Odroid C4 Wiring"></img>

회로도: `/hardware/schematic/moya-worklog_sch.png`

## Pin Map

| Name | GPIO# |
| ----------- | ----------- |
| Reset Button GPIO | 11(479) |
| Reset Button Active | 9(GND) |
| LED Positive | 1(3.3V) |
| LED Negative | 6(GND) |
| Print Button GPIO | 25 |
| Print Button LED | 12 |

[BCM numbering](https://wiki.odroid.com/odroid-xu4/application_note/gpio/rpi.gpio#about_bcm_numbering)

---

## 설치 방법 (Odroid C4 + Sam4s Giant 100)

**지원 환경**: Ubuntu 22.04 Minimal  
**기본 계정**: `root` / `odroid`

### 1. OS 이미지 굽기

[Ubuntu 22.04 Minimal Images](https://wiki.odroid.com/odroid-c4/os_images/ubuntu#ubuntu_2204_minimal_images) 에서 이미지 다운로드 후 SD카드에 굽기

### 2. UART로 IP 확인 후 SSH 접속

[USB-UART 키트](https://wiki.odroid.com/accessory/development/usb_uart_kit#usb-uart_kit) 연결 후:

```bash
screen /dev/ttyUSB0 115200
```

부팅 로그에서 IP 확인 → SSH 접속:

```bash
ssh root@<IP주소>
# password: odroid
```

### 3. WiFi 연결 (선택)

```bash
nmcli device
nmcli radio wifi on
nmcli device wifi list
nmcli device wifi connect "SSID" password "PASSWORD"
```

### 4. 기본 설정

```bash
apt-get update && apt-get upgrade -y
apt-get install -y git python3-dev python3-pip python3-venv libusb-1.0-0-dev build-essential
```

### 5. 프로젝트 다운로드

```bash
git clone https://github.com/AntonSangho/moya-worklog.git /root/moya-worklog
cd /root/moya-worklog
```

### 6. RPi.GPIO-Odroid 빌드 설치

표준 RPi.GPIO는 Odroid에서 동작하지 않으므로 Odroid 전용 버전을 설치한다.

```bash
git clone https://github.com/awesometic/RPi.GPIO-Odroid /tmp/RPi.GPIO-Odroid
cd /tmp/RPi.GPIO-Odroid
CFLAGS=-fcommon python3 setup.py build install
cd /root/moya-worklog
```

> `-fcommon` 플래그는 Ubuntu 22.04의 GCC 11에서 발생하는 multiple definition 빌드 오류를 해결한다.

### 7. Python 가상환경 및 패키지 설치

```bash
python3 -m venv /root/moya-worklog/venv-odroid
source /root/moya-worklog/venv-odroid/bin/activate
pip install --upgrade pip
pip install -r legacy/odroid/requirements.txt

# 가상환경에도 RPi.GPIO-Odroid 설치
pip uninstall -y RPi.GPIO
cd /tmp/RPi.GPIO-Odroid
CFLAGS=-fcommon python setup.py build install
cd /root/moya-worklog
```

### 8. 리셋 버튼 설정

[GPIO Key Wakeup 가이드](https://wiki.odroid.com/odroid-c4/application_note/gpio/gpio_key_wakeup#sw_set-up_using_bootini) 참고

`/media/boot/boot.ini`의 `# Load kernel` 라인 앞에 추가:

```bash
sed -i '/^# Load kernel/i # Reset button (GPIO11 = pin 479)\nsetenv gpiopower "479"\nsetenv bootargs ${bootargs} gpiopower=${gpiopower}\n' /media/boot/boot.ini
```

재부팅 후 적용:

```bash
reboot
```

### 9. systemd 서비스 등록 (부팅 자동 실행)

```bash
cp /root/moya-worklog/legacy/odroid/moya-printer-odroid.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable moya-printer-odroid.service
systemctl start moya-printer-odroid.service
```

상태 확인:

```bash
systemctl status moya-printer-odroid.service
journalctl -u moya-printer-odroid.service -f
```

---

## 문제 확인 프로세스

하드웨어 문제와 소프트웨어 문제를 단계적으로 분리한다.

```
[1] 전원 연결 → LED 점등?
        │ NO  → 전원 케이블/어댑터 점검 (HW)
        │ YES
        ↓
[2] UART 부팅 로그 정상?
        │ NO  → 보드/SD카드 점검 (HW)
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
[6] 버튼 동작?
        │ NO  → GPIO 배선/설정 점검 (HW/SW)
        │ YES
        ↓
    정상 동작
```

---

### 1단계 — 전원 확인 (HW)

> **주의**: Micro USB 포트는 허브 포트입니다. 전원이 아닙니다.  
> 반드시 **DC 잭**으로 전원을 연결하세요.

- DC 잭에 전원 어댑터 연결
- 전면 LED 점등 확인
- LED 미점등 시: 어댑터 출력 전압 확인 (5V), 케이블 단선 확인

---

### 2단계 — 부팅 확인 (HW/SW)

USB-UART 키트를 연결하고 전원을 켜서 부팅 로그를 확인한다.

```bash
screen /dev/ttyUSB0 115200
```

| 증상 | 원인 | 조치 |
|------|------|------|
| 아무 출력 없음 | UART 연결 오류 | TX/RX 선 확인, baud rate 확인 |
| 부팅 로그 후 멈춤 | SD카드 불량 또는 OS 손상 | OS 재설치 |
| `kernel panic` | 커널 문제 | OS 재설치 |
| 정상 부팅 후 로그인 프롬프트 | 정상 | 3단계로 |

---

### 3단계 — 네트워크 및 SSH 확인 (SW)

UART 콘솔에서 IP 확인:

```bash
ip addr show eth0
```

SSH 접속 확인:

```bash
ssh root@<IP주소>
```

| 증상 | 원인 | 조치 |
|------|------|------|
| IP 없음 | 이더넷 미연결 | LAN 케이블 연결 확인 |
| SSH 거부 | SSH 서비스 중지 | `systemctl start ssh` |
| 비밀번호 오류 | 비밀번호 변경됨 | UART 콘솔에서 `passwd` 재설정 |

---

### 4단계 — 서비스 확인 (SW)

```bash
systemctl status moya-printer-odroid.service
```

| 상태 | 조치 |
|------|------|
| `active (running)` | 정상, 5단계로 |
| `failed` | 로그 확인 후 재시작 |
| `inactive` | `systemctl start moya-printer-odroid.service` |

로그 확인:

```bash
journalctl -u moya-printer-odroid.service -n 50
```

서비스 재시작:

```bash
systemctl restart moya-printer-odroid.service
```

---

### 5단계 — 프린터 USB 확인 (HW/SW)

```bash
lsusb | grep -i 1c8a
```

- 출력 있음 (`1c8a:3a0e`) → 정상, 6단계로
- 출력 없음 → 아래 순서로 점검:

1. 프린터 전원 ON 확인
2. USB 케이블 재연결
3. 다른 USB 포트로 교체
4. `dmesg | tail -20` 으로 USB 인식 오류 확인

서비스 재시작으로 프린터 재연결:

```bash
systemctl restart moya-printer-odroid.service
```

---

### 6단계 — 버튼 동작 확인 (HW/SW)

**프린트 버튼 GPIO 직접 테스트:**

```bash
source /root/moya-worklog/venv-odroid/bin/activate
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print('버튼 상태:', GPIO.input(25))
GPIO.cleanup()
"
```

버튼을 누른 채로 실행하면 `1`, 떼면 `0`이 출력되어야 한다.

| 결과 | 원인 | 조치 |
|------|------|------|
| 항상 `0` | 정상 (미입력) | 버튼 누르면서 재테스트 |
| 항상 `1` | 배선 쇼트 또는 하드웨어 풀업 | 배선 재확인 |
| 버튼 눌러도 변화 없음 | GPIO 핀 불량 또는 배선 오류 | 핀맵 재확인 |

**리셋 버튼 미동작 시:**

```bash
grep gpiopower /media/boot/boot.ini
```

출력 없으면 [8단계 리셋 버튼 설정](#8-리셋-버튼-설정) 재적용 후 재부팅.

---

## 실행 (수동)

```bash
source /root/moya-worklog/venv-odroid/bin/activate
python3 /root/moya-worklog/legacy/odroid/print_odroid.py
```

---

## 관련 파일

| 파일 | 설명 |
|------|------|
| `legacy/odroid/print_odroid.py` | Odroid C4용 메인 스크립트 |
| `legacy/odroid/requirements.txt` | 패키지 목록 |
| `legacy/odroid/moya-printer-odroid.service` | systemd 서비스 파일 |
| `hardware/schematic/moya-worklog_OdroidC4_v1_bb.png` | 배선도 |
| `hardware/schematic/moya-worklog_sch.png` | 회로도 |
