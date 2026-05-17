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

## 설치 방법 (Odroid C4 + Sam4s Giant 100)

1. [Ubuntu Minimal 20.04 image](https://dn.odroid.com/S905X3/ODROID-C4/Ubuntu/ubuntu-20.04-4.9-mate-odroid-c4-hc4-20220228.img.xz) 다운로드

2. [UART 통신으로 IP 확인 후 SSH 접속](https://wiki.odroid.com/accessory/development/usb_uart_kit#usb-uart_kit)
   - id: `root`
   - password: `odroid`

3. [nmcli로 WiFi 연결](https://wiki.odroid.com/troubleshooting/minimal_image_wifi_setup_nmcli#check_if_your_wifi_module_enabled)
   ```bash
   nmcli device
   nmcli radio wifi on
   nmcli device wifi list
   nmcli device wifi connect "SSID" password "PASSWORD"
   ```

4. 기본 설정
   ```bash
   sudo passwd
   sudo apt-get update && sudo apt-get upgrade
   ```

5. 개발환경 설치
   ```bash
   sudo apt-get install python3-dev python3-pip cups escpos libcups2-dev
   ```

6. [Odroid용 RPi.GPIO 설치](https://wiki.odroid.com/odroid-xu4/application_note/gpio/rpi.gpio#rpigpio_for_odroid)
   ```bash
   git clone https://github.com/awesometic/RPi.GPIO-Odroid
   cd RPi.GPIO-Odroid
   sudo python setup.py build install
   ```

7. 프로젝트 다운로드
   ```bash
   git clone --recurse-submodules https://github.com/AntonSangho/moya-worklog.git
   cd moya-worklog/legacy/odroid
   pip install -r requirements.txt
   ```

8. [리셋 버튼 설치](https://wiki.odroid.com/odroid-c4/application_note/gpio/gpio_key_wakeup#sw_set-up_using_bootini)

   `/media/boot/boot.ini`에 추가:
   ```
   ### in case of GPIOX.3 (Pin 11) of 2x20 pins connector
   setenv gpiopower "479"
   setenv bootargs ${bootargs} gpiopower=${gpiopower}
   ```

9. 부팅 자동 실행
   ```bash
   sudo vi /etc/rc.local
   # exit 0 전에 추가:
   sudo python3 /root/moya-worklog/legacy/odroid/print_odroid.py &
   ```

## 실행

```bash
python3 legacy/odroid/print_odroid.py
```

## 관련 파일

| 파일 | 설명 |
|------|------|
| `legacy/odroid/print_odroid.py` | Odroid C4용 메인 스크립트 |
| `legacy/odroid/requirements.txt` | 패키지 목록 |
| `hardware/schematic/moya-worklog_OdroidC4_v1_bb.png` | 배선도 |
| `hardware/schematic/moya-worklog_sch.png` | 회로도 |
