# 모야작업일지 
라즈베리파이로 특정 파일을 프린트를 통해 출력하는 장치 
## 구성 및 필수 조건 
### BOM

| 부품명 | 수량 |  
| ----------- | ----------- | 
| 라즈베리파이 3A+ | 1ea |  
| BIXOLON_SRP-330II  | 1ea |
| 2.5A 전원 아답터 | 1ea |
| 납작소켓 커넥터 와이어 | 2ea |
| 1K ohm 저항 | 2ea |
| 100nF 커패시터 (104) | 1ea |

### 회로연결 
**Button circuit**
GPIO21 - 1k Ohm - ON (button)
GPIO21 - 100nF(104) -  GND 
3.3V - 1k Ohm - COM (button) 

** LED circuit**
GPIO20 - LED anode 
GND - LED cathode 

### 실행
`python3 print.ty`

## 설치안내
1. 라즈베리파이 imge 준비 : Raspbian 32-bit Desktop ver (2021-05-07)
2. 라즈베리파이 ssh, spi enable 
3. 원격 다운로드 
https://github.com/AntonSangho/moya-worklog.git
4. 드라이버 파일 압축해제
`unzip Software_BixolonCupsDrv_Linux_v1.3.5.1.zip .`
5. cups 설치
`sudo apt-get install cups`
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
		``#Booting script for moya printer
		python3 /home/pi/moya_attendance/print.py &``
## 사용법
1.	라즈베리파이 전원 연결하기. 
2.	흰색 불이 들어오면 버튼을 누른다. 


##파일 정보 및 목록 
- 실행파일
- 출력이미지
- 프린터 드라이버 

##저작권 및사용권 정보 
reliquum 

##배포자 및 개발자 연락처 
sanghoemail@gmail.com 

##알려진 버그
- 불안정한 전원장치에 연결할 때 출력이 불규칙적으로 발생하는 문제

##문제 발생 해결첵 
- 버튼을 연결한 GPIO 의 저항값을 높힌다. 

##업데이트 정보 
