# Moya Worklog 설치 가이드

라즈베리파이에 moya-worklog를 설치하는 AI 에이전트라면, 아래 단계를 순서대로 따라주세요.

---

## 사전 조건 (사람이 완료해야 함)

이 가이드를 실행하기 전에 아래 항목이 완료되어 있어야 합니다:

- [ ] 라즈베리파이에 Raspbian 64-bit Lite 설치 완료
- [ ] WiFi 연결 완료 (노트북과 같은 네트워크)
- [ ] SSH 활성화 완료
- [ ] 호스트명: `pi`
- [ ] Bixolon SRP-330II 프린터 USB 연결
- [ ] 정격 5V 2A 이상 파워 아답터 사용 (Adaptive Power 금지)

---

## Step 0: 사전 요구사항 확인

시스템 정보 및 네트워크 상태를 확인하세요:

```bash
# OS 버전 확인 (64-bit 확인)
uname -m
cat /etc/os-release | head -5

# 네트워크 연결 확인
ping -c 2 google.com

# USB 프린터 연결 확인 (Bixolon SRP-330II: 1504:006e)
lsusb | grep -i "1504:006e" || echo "WARNING: Bixolon 프린터가 연결되지 않음"
```

### Step 1: 시스템 업데이트 및 필수 패키지 설치

```bash
sudo apt update && sudo apt upgrade -y

# Python 및 개발 도구
sudo apt install -y python3-dev python3-pip python3-venv

# CUPS 프린팅 시스템
sudo apt install -y cups libcups2-dev

# USB 및 GPIO 라이브러리
sudo apt install -y libusb-1.0-0-dev python3-gpiozero python3-rpi.gpio

# Git 확인
if ! command -v git &> /dev/null; then
  sudo apt install -y git
fi
git --version
```

### Step 2: 저장소 Clone

```bash
cd ~
git clone https://github.com/user/moya-worklog.git
cd moya-worklog
git submodule update --init --recursive
```

이미 clone된 저장소가 있다면 최신 상태로 업데이트하세요:
```bash
cd ~/moya-worklog
git pull origin main
git submodule update --init --recursive
```

### Step 3: Python 의존성 설치

> **주의:** `requirements.txt`의 고정 버전이 Python 3.13과 호환되지 않을 수 있습니다.
> Debian 13 (trixie) 이상에서는 아래 방법으로 설치하세요.

```bash
# 핵심 패키지 설치 (버전 고정 없이)
sudo pip3 install --break-system-packages pillow python-escpos pyusb qrcode pyserial

# Debian 13 (trixie)에서 GPIO 호환성을 위해 rpi-lgpio 설치
sudo pip3 install --break-system-packages rpi-lgpio
```

기존 방식 (Python 3.11 이하):
```bash
cd ~/moya-worklog
pip3 install -r requirements.txt
```

### Step 4: Bixolon 프린터 드라이버 설치

```bash
cd ~/moya-worklog/Driver

# 드라이버 압축 해제
unzip -o Software_BixolonCupsDrv_RaspberryPI_v1.3.5.1.zip

# 압축 해제된 폴더 확인 후 설치
cd bixolon* || cd Bixolon* || cd BIXOLON*
sudo ./install.sh
```

### Step 5: USB 프린터 권한 설정

```bash
# udev 규칙 추가 (Bixolon SRP-330II: VID=1504, PID=006e)
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1504", ATTR{idProduct}=="006e", MODE="0666"' | sudo tee /etc/udev/rules.d/99-bixolon.rules

# udev 재시작
sudo udevadm control --reload-rules
sudo udevadm trigger

# pi 사용자를 필요한 그룹에 추가
sudo usermod -aG lpadmin,gpio pi
```

### Step 6: 설치 확인

```bash
cd ~/moya-worklog

# 프린터 연결 확인
lsusb | grep "1504:006e"

# Python 모듈 확인
python3 -c "from escpos import printer; print('escpos OK')"
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"
python3 -c "from PIL import Image; print('Pillow OK')"
```

모든 확인이 통과하면 설치 성공입니다.

### Step 7: 테스트 실행

```bash
cd ~/moya-worklog
sudo python3 print_Bixolon.py &

# 3초 대기 후 프로세스 확인
sleep 3
ps aux | grep print_Bixolon
```

GPIO 21번 핀에 연결된 버튼을 누르면 이미지가 출력됩니다.
테스트 후 프로세스 종료:
```bash
sudo pkill -f print_Bixolon.py
```

### Step 8: 자동 시작 설정 (systemd)

```bash
# systemd 서비스 파일 생성
sudo tee /etc/systemd/system/moya-worklog.service > /dev/null << 'EOF'
[Unit]
Description=Moya Worklog Printer Service
After=multi-user.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/moya-worklog
ExecStart=/usr/bin/python3 /home/pi/moya-worklog/print_Bixolon.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable moya-worklog.service
sudo systemctl start moya-worklog.service
```

### Step 9: 최종 확인

```bash
# 서비스 상태 확인
sudo systemctl status moya-worklog.service

# 실행 중인지 확인
ps aux | grep print_Bixolon
```

`Active: active (running)`이 출력되면 설치 성공입니다. 사용자에게 아래 정보를 안내하세요:

- **서비스 상태 확인**: `sudo systemctl status moya-worklog`
- **로그 확인**: `journalctl -u moya-worklog -f`
- **재부팅 후 자동 시작됨**

---

## 참고 정보

### GPIO 핀 연결

| 기능 | GPIO (BCM) | 물리 핀 |
|------|------------|---------|
| Print Button | 21 | 40 |
| Print Button LED | 20 | 38 |
| Reset Button | 3 | 5 |
| Power LED | 6 | 31 |

### 트러블슈팅

**프린터가 인식되지 않을 경우:**
```bash
# USB 장치 재확인
lsusb
# 프린터 분리 후 재연결
# udev 규칙 재적용
sudo udevadm control --reload-rules && sudo udevadm trigger
```

**GPIO 권한 오류:**
```bash
sudo usermod -aG gpio pi
# 재부팅 필요
sudo reboot
```

**서비스가 시작되지 않을 경우:**
```bash
# 로그 확인
journalctl -u moya-worklog -n 50

# 수동 실행으로 에러 확인
sudo python3 /home/pi/moya-worklog/print_Bixolon.py
```

---

### Debian 13 (trixie) / Python 3.13 관련 이슈

**1. Pillow 빌드 실패 (KeyError: '__version__')**

증상:
```
KeyError: '__version__'
Getting requirements to build wheel: finished with status 'error'
```

원인: `requirements.txt`의 `Pillow==9.1.1`이 Python 3.13과 호환되지 않음

해결:
```bash
sudo pip3 install --break-system-packages pillow
```

**2. ModuleNotFoundError: No module named 'escpos'**

증상: systemd 서비스 시작 시 모듈을 찾지 못함

원인: `pip3 install`이 사용자 경로(`~/.local`)에만 설치되어 root로 실행되는 systemd에서 접근 불가

해결:
```bash
sudo pip3 install --break-system-packages pillow python-escpos pyusb qrcode pyserial
```

**3. RuntimeError: Failed to add edge detection**

증상:
```
RuntimeError: Failed to add edge detection
```

원인: Debian 13에서 기존 RPi.GPIO의 edge detection이 작동하지 않음

해결:
```bash
sudo pip3 install --break-system-packages rpi-lgpio
```

### 유용한 명령어

```bash
# 서비스 중지
sudo systemctl stop moya-worklog

# 서비스 재시작
sudo systemctl restart moya-worklog

# 서비스 비활성화 (부팅 시 자동시작 안함)
sudo systemctl disable moya-worklog

# 실시간 로그
journalctl -u moya-worklog -f
```
