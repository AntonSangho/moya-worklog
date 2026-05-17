## 프로젝트 설명 
<img width="50%" src="https://user-images.githubusercontent.com/8589992/174252878-1f55046e-c069-4821-acf7-9d2b71925bf2.jpg" />
라즈베리파이와 같은 리눅스 소형 컴퓨터로 특정 파일을 영수증 프린트를 통해 출력하는 장치.  

## Wiring 
# Raspberry Pi4
<img src="/Schematic/Wiring_v1.jpg" width="40%" height="30%" title="px(픽셀) 크기 설정" alt="RubberDuck"></img>. 
# Odroid C4
<img src="/Schematic/moya-worklog_OdroidC4_v1_bb.png" width="40%" height="30%" title="px(픽셀) 크기 설정" alt="RubberDuck"></img>

## Pin Map 
### Raspberry Pi
| Name | GPIO# |  
| ----------- | ----------- | 
| Reset Button GPIO | 3 |  
| Reset Button Active | GND |
| Power LED Positive | 6 |
| Power LED Negative | GND |
| Print Button GPIO | 21 |
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
2. sam4s 버전: 
	`sudo python3 print_sam4s.py`

## 설치방법
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

### Raspberry pi(escpos) + Sam4s Giant 100

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
- 실행파일
- 출력이미지
- 프린터 드라이버 

## 저작권 및사용권 정보 
reliquum 

## 배포자 및 개발자 연락처 
sanghoemail@gmail.com 

## 알려진 버그
- 불안정한 전원장치에 연결할 때 출력이 불규칙적으로 발생하는 문제

## 업데이트 정보 
