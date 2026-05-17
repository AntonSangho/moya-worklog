## 프로젝트 설명 
<img width="50%" src="https://user-images.githubusercontent.com/8589992/174252878-1f55046e-c069-4821-acf7-9d2b71925bf2.jpg" />
라즈베리파이와 같은 리눅스 소형 컴퓨터로 특정 파일을 영수증 프린트를 통해 출력하는 장치.  

## Wiring 
# Raspberry Pi
<img src="/hardware/schematic/Wiring_v1.jpg" width="40%" height="30%" title="px(픽셀) 크기 설정" alt="RubberDuck"></img>

# Odroid C4
<img src="/hardware/schematic/moya-worklog_OdroidC4_v1_bb.png" width="40%" height="30%" title="px(픽셀) 크기 설정" alt="RubberDuck"></img>

## Pin Map 
### Raspberry Pi
| Name | GPIO# |  
| ----------- | ----------- | 
| Reset Button GPIO | 3 |  
| Reset Button Active | GND |
| Power LED Positive | 6 |
| Power LED Negative | GND |
| Print Button GPIO | 4 |
| Print Button LED | 20 |

[GPIO](https://pinout.xyz/)

### Odroid C4
| Name | GPIO# |  
| ----------- | ----------- | 
| Reset Button GPIO | 11(479) |  
| Reset Button Active | 9(GND) |
| LED Positive | 1(3.3V) |
| LED Negative | 6(GND) |
| Print Button GPIO | 25 |
| Print Button LED | 12 |

[BCM numbering](https://wiki.odroid.com/odroid-xu4/application_note/gpio/rpi.gpio#about_bcm_numbering)

## BOM

| 부품명 | 수량 |  
| ----------- | ----------- | 
| 라즈베리파이 3A+ | 1ea |  
| BIXOLON_SRP-330II  | 1ea |
| 2.5A 전원 아답터 | 1ea |
| 납작소켓 커넥터 와이어 | 2ea |
| 1K ohm 저항 | 2ea |
| 100nF 커패시터 (104) | 1ea |
| 60mm LED 아케이드 버튼 스위치 (SZH-LC043) | 1ea |

## 실행방법
1. Bixolon 버전 :
	`sudo python3 print_Bixolon.py` 
2. sam4s 버전 (32-bit): 
	`sudo python3 print_sam4s.py`
3. **sam4s 버전 (64-bit 최신)**: 
	`python3 print_sam4s_production.py`

## 설치방법

### 🆕 Raspberry Pi 3/4 (64-bit) + Sam4s Giant 100 (권장)

**지원 환경**: Raspberry Pi OS 64-bit Lite (Bookworm)  
**특징**: 스레드 방식, 이미지 캐싱, USB 자동 재연결, systemd 서비스

1. **라즈베리파이 이미지 굽기 (Raspberry Pi Imager)**

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

2. **GPIO 활성화** (중요!)
   ```bash
   sudo raspi-config nonint do_spi 0
   sudo raspi-config nonint do_i2c 0
   echo "dtparam=gpio=on" | sudo tee -a /boot/firmware/config.txt
   sudo reboot
   ```

3. **프로젝트 다운로드**
   ```bash
   git clone --recurse-submodules https://github.com/AntonSangho/moya-worklog.git
   cd moya-worklog
   git checkout -b raspbian-64bit-lite
   ```

4. **시스템 패키지 설치**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y build-essential git vim curl wget
   sudo apt install -y python3-dev python3-pip python3-venv python3-setuptools python3-wheel
   sudo apt install -y libffi-dev libssl-dev libjpeg-dev zlib1g-dev libusb-1.0-0-dev
   sudo apt install -y python3-rpi.gpio python3-gpiozero usbutils
   ```

5. **CUPS 프린터 시스템 설치**
   ```bash
   sudo apt install -y cups cups-client cups-bsd cups-common libcups2-dev
   sudo apt install -y printer-driver-all printer-driver-cups-pdf
   sudo systemctl enable cups
   sudo systemctl start cups
   ```

6. **사용자 권한 설정**
   ```bash
   sudo usermod -a -G dialout,gpio,spi,i2c,lpadmin,lp anton
   newgrp lpadmin
   ```

7. **Python 가상환경 설정**
   ```bash
   python3 -m venv venv-64bit
   source venv-64bit/bin/activate
   pip install --upgrade pip wheel
   pip install -r requirements-64bit.txt
   ```

8. **프린터 설정 (Raw 모드)**
   ```bash
   # Sam4s Giant 100 USB 연결 후
   sudo lpadmin -p Sam4s_Giant100 -E -v "usb://1c8a/3a0e" -m raw
   sudo lpoptions -d Sam4s_Giant100
   ```

9. **USB 권한 설정**
   ```bash
   sudo tee /etc/udev/rules.d/99-sam4s-printer.rules << EOF
   SUBSYSTEM=="usb", ATTR{idVendor}=="1c8a", ATTR{idProduct}=="3a0e", MODE="0666", GROUP="lp"
   KERNEL=="lp[0-9]*", SUBSYSTEM=="usb", MODE="0666", GROUP="lp"
   EOF
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

10. **테스트 실행**
    ```bash
    source venv-64bit/bin/activate
    python3 print_sam4s_production.py
    ```

11. **부팅시 자동 시작 설정**
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

### Raspberry pi(cups) + Bixolon SRP-330II 
1. 라즈베리파이 imge 준비 : Raspbian 32-bit Desktop ver (2021-05-07)
2. 라즈베리파이 ssh, spi enable 
3. 원격 다운로드  
    `git clone --recurse-submodules https://github.com/AntonSangho/moya-worklog.git`
4. 드라이버 파일 압축해제  
    `unzip Software_BixolonCupsDrv_Linux_v1.3.5.1.zip .`
6. cups 설치  
    `sudo apt-get install cups`
7. pip 설치  
    `sudo apt-get install python3-pip`
8. escpos 설치  
    `sudo pip3 install escpos`
6. 프린터 드라이버 설치  
    `sh setup_v1.4.1.sh`
7. pi  권한 획득  
    `sudo usermod -a -G lpadmin pi`
8. libcups2-dev 설치  
	`sudo apt-get install libcups2-dev`
9. pycups 설치  
	`sudo pip3 install pycups`
10. cups 설정
	1. http://localhost:631 접속
	2. Add printer (USB 연결된 상태)
	3. Print 사이즈 : 75x150mm설정 
11. 기본 프린터 설정  
    `lpoptions -d BIXOLON_SRP-330II`
12. 부팅파일 설정 
	1. `sudo vi /etc/rc.local`
	2. Exit 0 전에 아래 코드 추가  
        `python3 /home/pi/moya-worklog/print.py &`

### Raspberry pi(escpos) + Sam4s Giant 100 (32-bit Legacy)

#### 설치파일 실행하는 법  
`chmod +x install.sh`  

`./install.sh`  

#### 설치하는 법  

1. 라즈베리파이 이미지 준비 : Raspbian 32-bit Lite ver (2022-04-04)
2. 라즈베리파이 ssh enable 
3. Git 설치 후 원격 다운로드  
    `git clone --recurse-submodules https://github.com/AntonSangho/moya-worklog.git`
4. pip 설치  
    `sudo apt-get install python3-pip`  
	`sudo pip3 install escpos`  
	`sudo apt-get install libopenjp2-7`
5. libcups2-dev 설치  
	`sudo apt-get install libcups2-dev`
6. pycups 설치  
	`sudo pip3 install pycups`
7. requirement로 설치  
    `pip install -r requirements.txt `
8. 부팅파일 설정 
	1. `sudo vi /etc/rc.local`
	2. Exit 0 전에 아래 코드 추가  
        `python3 /home/pi/moya-worklog/print_sam4s.py &`
9. [리셋버튼 설치](https://howchoo.com/g/mwnlytk3zmm/how-to-add-a-power-button-to-your-raspberry-pi)  
    `./pi-power-button/script/install`

10. [부팅 확인 led 설치](https://howchoo.com/g/ytzjyzy4m2e/build-a-simple-raspberry-pi-led-power-status-indicator#enable-the-gpio-serial-port)  
    `enable_uart = 1`


### Odroid C4 + Sam4s Giant 100
1. [Ubuntu Minimal 20.04 image](https://dn.odroid.com/S905X3/ODROID-C4/Ubuntu/ubuntu-20.04-4.9-mate-odroid-c4-hc4-20220228.img.xz)을 다운로드한다.
2. [uart 통신을 통해서 ip address확인 후 ssh 접속.](https://wiki.odroid.com/accessory/development/usb_uart_kit#usb-uart_kit)
   	- id: `root`
   	- password: `odroid`
4. [nmcli를 이용하여 무선 접속하기](https://wiki.odroid.com/troubleshooting/minimal_image_wifi_setup_nmcli#check_if_your_wifi_module_enabled)
   	1. `nmcli device`
   	2. `nmcli radio wifi on`
   	3. `nmcli device wifi list`
   	4. `nmcli device wifi connect "showme_2.4G" password "PASSWORD_FOR_THE_WIFI"`
5. 기본 비밀번호 변경  
	`sudo passwd`
6. 시스템 업데이이트  
	`sudo apt-get update`  
	`sudo apt-get upgrade`
7. 개발환경세팅  
	`sudo apt-get install python3-dev`  
	`sudo apt-get install python3-pip`  
	`sudo apt-get install cups`  
	`sudo apt-get install escpos`  
	`sudo apt-get install libcups2-dev`
	
8. [Odroid 용 RPi.GPIO 설치](https://wiki.odroid.com/odroid-xu4/application_note/gpio/rpi.gpio#rpigpio_for_odroid)    
	`git clone https://github.com/awesometic/RPi.GPIO-Odroid`  
	`cd RPi.GPIO-Odroid`  
	`sudo python setup.py build install`  
	
9. 원격 다운로드  
	`git clone --recurse-submodules https://github.com/AntonSangho/moya-worklog.git`
	
10. pip install  
	`cd odroid`  
	`pip install -r requirements.txt`
	

11. [리셋버튼 설치](https://wiki.odroid.com/odroid-c4/application_note/gpio/gpio_key_wakeup#sw_set-up_using_bootini)
boot.ini(/media/boot/boot.ini)에 setenv bootargs 아래 두줄 추가. 
```
### in case of GPIOX.3 (Pin 11) of 2x20 pins connector
setenv gpiopower "479"
setenv bootargs ${bootargs} gpiopower=${gpiopower}
```
5. 부팅파일 설정
	1. `sudo vi /etc/rc.local`
	2. Exit 0 전에 아래 코드 추가  
        `sudo python3 /root/moya-worklog/odroid/print_odroid.py &`

## 동작하는 법
1. 라즈베리파이 전원 연결하기. 
2. 흰색 불이 들어오면 버튼을 누른다. 

## 작업일지파일 만드는 법(illustrator2022 기준) 
1. 작업일지_원본.ai 파일 열기
2. 내보내기 -> 내보내기 형식
3. 파일명 수정
4. 대지사용 체크 후 범위설정
5. 내보내기 누르기
6. 해상도: 고(300ppi) / 앤티 앨리어싱: 아트최적화 / 배경색: 흰색 
7. 확인 

## 파일 정보 및 목록

```
moya-worklog/
├── print_sam4s_production.py  # 64-bit 최신 (스레드, 이미지 캐싱, USB 자동 재연결)
├── print_Bixolon.py           # Bixolon 프린터용
├── moya-printer.service       # systemd 서비스 파일
├── requirements-64bit.txt     # 64-bit 환경 패키지
├── requirements.txt           # 32-bit 레거시 패키지
├── image/                     # 출력 이미지 (PNG)
├── hardware/
│   ├── schematic/             # 회로도, 배선도
│   └── drawing/               # 기구 도면
├── Driver/                    # 프린터 드라이버
├── legacy/                    # 구버전 코드 (Odroid, 32-bit)
│   └── odroid/
└── pi-power-button/           # 전원 버튼 스크립트
```

## 시스템 요구사항

### 64-bit 버전 (권장)
- **하드웨어**: Raspberry Pi 3B+ / 4B 이상
- **OS**: Raspberry Pi OS 64-bit Lite (Bookworm)
- **메모리**: 1GB 이상
- **저장공간**: 8GB 이상
- **Python**: 3.11 이상
- **특징**: 스레드 방식, 이미지 캐싱, USB 자동 재연결, systemd 서비스

### 32-bit 버전 (레거시)
- **하드웨어**: Raspberry Pi 3A+ 이상
- **OS**: Raspberry Pi OS 32-bit Lite
- **메모리**: 512MB 이상
- **Python**: 3.7 이상
- **특징**: 인터럽트 방식, rc.local 실행

## 저작권 및사용권 정보 
reliquum 

## 배포자 및 개발자 연락처 
sanghoemail@gmail.com 

## 알려진 버그
- ~~불안정한 전원장치에 연결할 때 출력이 불규칙적으로 발생하는 문제~~ (64-bit 버전에서 해결)
- 32-bit 버전에서 GPIO 인터럽트 간헐적 실패 (64-bit 폴링 방식으로 해결)

## 업데이트 정보
- **2026.05**: Odroid C4 → Raspberry Pi 3 이식 완료
- **2026.05**: GPIO2(SDA) 하드웨어 풀업 문제 → GPIO4로 변경
- **2026.05**: 스레드 방식 버튼 감지, 이미지 캐싱, USB 자동 재연결 추가
- **2026.05**: systemd 서비스(`moya-printer.service`) 등록
- **2025.08**: 64-bit Raspberry Pi OS 지원 추가
- **2025.08**: systemd 서비스 지원 추가
- **2025.08**: CUPS Raw 모드 프린터 설정 간소화