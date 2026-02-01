# Moya Worklog 라즈베리파이 설치 가이드

이 문서는 AI agent가 자동으로 실행할 수 있도록 작성된 설치 가이드입니다.

---

## 사전 준비물

### 하드웨어
- [ ] 라즈베리파이 (Raspberry Pi 4 권장)
- [ ] MicroSD 카드 (16GB 이상)
- [ ] 프린터: Bixolon SRP-330II (USB 연결)
- [ ] 파워 아답터: **정격 5V 2A 이상** (Adaptive Power 사용 금지)
- [ ] 모니터 (HDMI 연결)
- [ ] USB 키보드

### 소프트웨어
- Raspberry Pi Imager (SD 카드 이미징용)
- Raspbian OS 64-bit Lite

---

## 1단계: SD 카드 이미지 굽기

1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/) 다운로드 및 설치
2. SD 카드를 컴퓨터에 삽입
3. Raspberry Pi Imager 실행
4. OS 선택: **Raspberry Pi OS (64-bit) Lite**
   - `Raspberry Pi OS (other)` > `Raspberry Pi OS Lite (64-bit)` 선택
5. 저장소 선택: 삽입한 SD 카드 선택
6. **설정 아이콘(톱니바퀴)** 클릭하여 사전 설정:
   - 호스트명: `pi`
   - SSH 활성화: 체크
   - 사용자 이름: `pi`
   - 비밀번호: 원하는 비밀번호 설정
   - WiFi 설정: 노트북과 동일한 네트워크 SSID 및 비밀번호 입력
   - 로캘 설정: Asia/Seoul
7. **쓰기** 버튼 클릭하여 이미징 시작
8. 완료 후 SD 카드 안전하게 제거

---

## 2단계: 하드웨어 조립

1. SD 카드를 라즈베리파이에 삽입
2. 모니터를 HDMI로 연결
3. USB 키보드 연결
4. Bixolon SRP-330II 프린터를 USB로 연결
5. **마지막에** 파워 아답터 연결 (5V 2A 정격)

---

## 3단계: 첫 부팅 및 기본 설정

### 부팅 확인
1. 전원 연결 후 부팅 대기 (약 1-2분)
2. 로그인 프롬프트가 나타나면:
   - 사용자: `pi`
   - 비밀번호: (Imager에서 설정한 비밀번호)

### 네트워크 확인
```bash
# IP 주소 확인
ip addr show wlan0

# 인터넷 연결 테스트
ping -c 3 google.com
```

### SSH 활성화 확인
```bash
sudo systemctl status ssh
# Active: active (running) 확인
```

만약 SSH가 비활성화되어 있다면:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

## 4단계: 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 5단계: 필수 패키지 설치

```bash
# Python 및 개발 도구
sudo apt install -y python3-dev python3-pip python3-venv git

# CUPS 프린팅 시스템
sudo apt install -y cups libcups2-dev

# USB 라이브러리
sudo apt install -y libusb-1.0-0-dev

# GPIO 라이브러리
sudo apt install -y python3-gpiozero python3-rpi.gpio
```

---

## 6단계: 프로젝트 클론

```bash
cd ~
git clone https://github.com/[저장소경로]/moya-worklog.git
cd moya-worklog
git submodule update --init --recursive
```

---

## 7단계: Python 의존성 설치

```bash
cd ~/moya-worklog
pip3 install -r requirements.txt
```

---

## 8단계: Bixolon 프린터 드라이버 설치

```bash
cd ~/moya-worklog/Driver

# 드라이버 압축 해제
unzip Software_BixolonCupsDrv_RaspberryPI_v1.3.5.1.zip

# 드라이버 설치 (압축 해제된 폴더로 이동 후)
cd [압축해제폴더]
sudo ./install.sh
```

### CUPS 프린터 추가
```bash
# CUPS 웹 인터페이스 활성화
sudo usermod -aG lpadmin pi
sudo cupsctl --remote-any

# 프린터 확인
lpinfo -v | grep usb
```

웹브라우저에서 `http://[라즈베리파이IP]:631` 접속하여 프린터 추가

---

## 9단계: USB 프린터 권한 설정

```bash
# udev 규칙 추가 (Bixolon SRP-330II)
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1504", ATTR{idProduct}=="006e", MODE="0666"' | sudo tee /etc/udev/rules.d/99-bixolon.rules

# udev 재시작
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 10단계: 테스트 실행

```bash
cd ~/moya-worklog

# 프린터 테스트
sudo python3 print_Bixolon.py
```

GPIO 21번 핀에 연결된 버튼을 누르면 이미지가 출력됩니다.

---

## 11단계: 자동 시작 설정

### 방법 1: rc.local 사용
```bash
sudo nano /etc/rc.local
```

`exit 0` 전에 다음 줄 추가:
```bash
python3 /home/pi/moya-worklog/print_Bixolon.py &
```

### 방법 2: systemd 서비스 생성 (권장)
```bash
sudo nano /etc/systemd/system/moya-worklog.service
```

내용:
```ini
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
```

서비스 활성화:
```bash
sudo systemctl daemon-reload
sudo systemctl enable moya-worklog.service
sudo systemctl start moya-worklog.service
```

---

## 12단계: GPIO 연결 (하드웨어)

| 기능 | GPIO (BCM) | 물리 핀 |
|------|------------|---------|
| Print Button | 21 | 40 |
| Print Button LED | 20 | 38 |
| Reset Button | 3 | 5 |
| Power LED | 6 | 31 |

버튼은 **Pull-Down** 저항 설정으로 동작합니다.

---

## 문제 해결

### 프린터가 인식되지 않음
```bash
# USB 장치 확인
lsusb | grep -i bixolon

# 예상 출력: Bus 001 Device 00X: ID 1504:006e
```

### GPIO 권한 오류
```bash
sudo usermod -aG gpio pi
# 재부팅 후 적용
```

### 전원 불안정으로 인한 오작동
- 정격 5V 2A 이상의 파워 아답터 사용
- Adaptive Power (USB PD) 사용 금지
- USB 허브를 통한 연결 지양

---

## 요약 체크리스트

- [ ] SD 카드 이미징 완료 (Raspbian 64-bit Lite)
- [ ] 첫 부팅 및 로그인 성공
- [ ] WiFi 연결 확인
- [ ] SSH 활성화 확인
- [ ] 시스템 업데이트 완료
- [ ] 필수 패키지 설치 완료
- [ ] 프로젝트 클론 완료
- [ ] Python 의존성 설치 완료
- [ ] Bixolon 드라이버 설치 완료
- [ ] USB 권한 설정 완료
- [ ] 테스트 출력 성공
- [ ] 자동 시작 설정 완료
