#!/usr/bin/env python3
"""
Sam4s Giant 100 프린터 제어 스크립트 (최종 프로덕션 버전)
64-bit Raspberry Pi OS + 폴링 방식
"""

import RPi.GPIO as GPIO
import time
import os
import random
import logging
from escpos.printer import Usb
from PIL import Image

# 로깅 설정 (force=True: escpos 임포트로 설정된 핸들러 덮어쓰기)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/moya-worklog/printer.log'),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)

# GPIO 핀 설정
# GPIO2(SDA)는 하드웨어 풀업 내장으로 사용 불가 → GPIO4(Physical 7번)로 변경
BUTTON_PIN = 4  # 출력 버튼
LED_PIN = 20     # 상태 LED

# 프린터 설정
VENDOR_ID = 0x1c8a
PRODUCT_ID = 0x3a0e
IN_EP = 0x81
OUT_EP = 0x02

# 이미지 설정
IMAGE_DIR = "/home/pi/moya-worklog/image"
IMAGE_FILES = [
    f"{IMAGE_DIR}/w1_2022.png",
    f"{IMAGE_DIR}/w2_2022.png",
    f"{IMAGE_DIR}/w3_2022.png",
    f"{IMAGE_DIR}/w4_2022.png",
    f"{IMAGE_DIR}/w5_2022.png"
]

# 전역 변수
printer_instance = None
count = 0
last_button_state = GPIO.LOW
last_print_time = 0

def setup_printer():
    """프린터 초기화"""
    global printer_instance
    
    try:
        printer_instance = Usb(VENDOR_ID, PRODUCT_ID, in_ep=IN_EP, out_ep=OUT_EP)
        logger.info("✅ Sam4s Giant 100 프린터 연결 성공")
        return True
    except Exception as e:
        logger.error(f"❌ 프린터 연결 실패: {e}")
        return False

def setup_gpio():
    """GPIO 초기화 (폴링 방식)"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # 핀 설정
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(LED_PIN, GPIO.OUT)
        
        # LED 켜기 (준비 상태)
        GPIO.output(LED_PIN, GPIO.HIGH)
        
        # 초기 버튼 상태
        initial_state = GPIO.input(BUTTON_PIN)
        logger.info(f"✅ GPIO 설정 완료 - LED 켜짐, 초기 버튼 상태: {initial_state}")
        return True
        
    except Exception as e:
        logger.error(f"❌ GPIO 설정 실패: {e}")
        return False

def get_available_images():
    """사용 가능한 이미지 파일 목록"""
    available = []
    for image_file in IMAGE_FILES:
        if os.path.exists(image_file):
            file_size = os.path.getsize(image_file)
            available.append(image_file)
            logger.debug(f"이미지 발견: {os.path.basename(image_file)} ({file_size} bytes)")
        else:
            logger.debug(f"이미지 없음: {os.path.basename(image_file)}")
    
    logger.info(f"📁 사용 가능한 이미지: {len(available)}개")
    return available

def print_output():
    """프린터 출력 실행"""
    global count, last_print_time
    
    current_time = time.time()
    
    # 2초 디바운싱
    if current_time - last_print_time < 2.0:
        logger.debug("디바운싱: 출력 요청 무시")
        return
    
    last_print_time = current_time
    count += 1
    
    try:
        logger.info(f"🖨️ 출력 시작 #{count}")
        
        # LED 진행 상태 표시
        for i in range(3):
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.1)
        
        # 이미지 파일 확인
        available_images = get_available_images()
        
        if available_images and printer_instance:
            # 이미지 출력 모드
            selected_file = random.choice(available_images)
            logger.info(f"📸 선택된 이미지: {os.path.basename(selected_file)}")
            
            # 이미지 로드 및 처리
            im = Image.open(selected_file)
            logger.info(f"원본 크기: {im.size}")
            
            # Sam4s Giant 100 최적 크기로 리사이즈
            resized = im.resize((480, 1000))
            logger.info(f"리사이즈: {resized.size}")
            
            # 프린터 출력
            printer_instance.image(resized)
            printer_instance.cut()
            
            logger.info(f"✅ 이미지 출력 완료 #{count}")
            
        elif printer_instance:
            # 텍스트 출력 모드 (이미지 없을 때)
            logger.info("📝 텍스트 출력 모드")
            
            text_content = [
                f"=== Test Print #{count} ===\n",
                "Sam4s Giant 100\n",
                "64-bit Raspberry Pi OS\n",
                "폴링 방식 정상 작동!\n",
                f"시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                f"총 출력 횟수: {count}\n",
                "=" * 30 + "\n"
            ]
            
            for line in text_content:
                printer_instance.text(line)
            
            printer_instance.cut()
            logger.info(f"✅ 텍스트 출력 완료 #{count}")
        
        else:
            logger.error("❌ 프린터가 연결되지 않음")
        
        # LED 준비 상태로 복귀
        GPIO.output(LED_PIN, GPIO.HIGH)
        
    except Exception as e:
        logger.error(f"❌ 출력 오류 #{count}: {e}")
        logger.error(f"오류 타입: {type(e).__name__}")
        GPIO.output(LED_PIN, GPIO.HIGH)

def check_button():
    """폴링 방식 버튼 상태 확인"""
    global last_button_state
    
    try:
        current_state = GPIO.input(BUTTON_PIN)
        
        # Rising Edge 감지 (버튼 눌림)
        if current_state == GPIO.HIGH and last_button_state == GPIO.LOW:
            logger.info("🔘 버튼 눌림 감지!")
            last_button_state = current_state
            return True
        
        last_button_state = current_state
        return False
        
    except Exception as e:
        logger.error(f"버튼 읽기 오류: {e}")
        return False

def cleanup():
    """리소스 정리"""
    try:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        logger.info("🧹 GPIO 정리 완료")
    except Exception as e:
        logger.error(f"정리 오류: {e}")

def main():
    """메인 실행 함수"""
    logger.info("🚀 Sam4s Giant 100 프린터 서비스 시작 (폴링 방식)")
    logger.info("=" * 60)
    
    # 시스템 정보
    logger.info(f"작업 디렉토리: {os.getcwd()}")
    logger.info(f"사용자: {os.getenv('USER', 'unknown')}")
    logger.info(f"Python: {os.sys.version.split()[0]}")
    
    # 초기화
    logger.info("1/2: 프린터 초기화")
    if not setup_printer():
        logger.error("❌ 프린터 초기화 실패 - 서비스 종료")
        return
    
    logger.info("2/2: GPIO 초기화")
    if not setup_gpio():
        logger.error("❌ GPIO 초기화 실패 - 서비스 종료")
        cleanup()
        return
    
    # 이미지 파일 확인
    available_images = get_available_images()
    
    logger.info("=" * 60)
    logger.info("✅ 모든 초기화 완료!")
    logger.info(f"🔘 버튼(GPIO {BUTTON_PIN})을 누르면 출력됩니다")
    logger.info("📊 10초마다 상태 정보 출력")
    logger.info("⏹️ 종료하려면 Ctrl+C를 누르세요")
    logger.info("=" * 60)
    
    loop_count = 0
    
    try:
        # 메인 폴링 루프
        while True:
            loop_count += 1
            
            # 버튼 상태 확인
            if check_button():
                print_output()
                time.sleep(0.5)  # 출력 후 추가 대기
            
            # 10초마다 상태 출력
            if loop_count % 50 == 0:  # 50 * 0.2초 = 10초
                logger.info(f"💓 서비스 실행 중... (루프 #{loop_count}, 총 출력: {count}회)")
            
            # 폴링 간격 (200ms)
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        logger.info("⏹️ 사용자에 의해 종료")
        
    except Exception as e:
        logger.error(f"❌ 런타임 오류: {e}")
        logger.error(f"오류 타입: {type(e).__name__}")
        
    finally:
        cleanup()
        logger.info("🏁 Sam4s 프린터 서비스 종료")

if __name__ == "__main__":
    main()