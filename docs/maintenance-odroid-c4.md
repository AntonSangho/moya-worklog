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
