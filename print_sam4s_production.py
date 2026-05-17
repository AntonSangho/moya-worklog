#!/usr/bin/env python3
"""
Sam4s Giant 100 프린터 제어 스크립트 (최종 프로덕션 버전)
64-bit Raspberry Pi OS + 인터럽트 방식
"""

import RPi.GPIO as GPIO
import time
import os
import random
import logging
import threading
from logging.handlers import RotatingFileHandler
from escpos.printer import Usb
from PIL import Image

# 개선 1: RotatingFileHandler - 1MB 초과 시 rotation, 최대 3개 보관
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('/home/pi/moya-worklog/printer.log', maxBytes=1*1024*1024, backupCount=3),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)

# GPIO 핀 설정
# GPIO2(SDA)는 하드웨어 풀업 내장으로 사용 불가 → GPIO4(Physical 7번)로 변경
BUTTON_PIN = 4  # 출력 버튼
LED_PIN = 20    # 상태 LED

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
last_print_time = 0
image_cache = {}  # 개선 2: 시작 시 사전 로드된 이미지 캐시
_stop_event = threading.Event()  # 개선 4: 버튼 감시 스레드 종료 신호
_print_lock = threading.Lock()   # 동시 출력 방지


def setup_printer():
    global printer_instance
    try:
        printer_instance = Usb(VENDOR_ID, PRODUCT_ID, in_ep=IN_EP, out_ep=OUT_EP)
        logger.info("✅ Sam4s Giant 100 프린터 연결 성공")
        return True
    except Exception as e:
        logger.error(f"❌ 프린터 연결 실패: {e}")
        return False


def reconnect_printer():
    """개선 3: USB 프린터 자동 재연결 (최대 3회 시도)"""
    global printer_instance
    for attempt in range(1, 4):
        logger.info(f"🔄 프린터 재연결 시도 {attempt}/3")
        try:
            if printer_instance:
                try:
                    printer_instance.close()
                except Exception:
                    pass
            time.sleep(2)
            printer_instance = Usb(VENDOR_ID, PRODUCT_ID, in_ep=IN_EP, out_ep=OUT_EP)
            logger.info("✅ 프린터 재연결 성공")
            return True
        except Exception as e:
            logger.error(f"❌ 재연결 실패 ({attempt}/3): {e}")
    logger.error("❌ 프린터 재연결 포기")
    return False


def preload_images():
    """개선 2: 시작 시 이미지 전처리 및 캐싱"""
    global image_cache
    loaded = 0
    for path in IMAGE_FILES:
        if os.path.exists(path):
            try:
                img = Image.open(path).resize((480, 1000))
                image_cache[path] = img
                logger.info(f"🖼️ 이미지 캐시 완료: {os.path.basename(path)}")
                loaded += 1
            except Exception as e:
                logger.error(f"이미지 캐시 실패 {os.path.basename(path)}: {e}")
    logger.info(f"📁 캐시 완료: {loaded}개 이미지")
    return loaded


def setup_gpio():
    """GPIO 초기화 + 개선 4: 백그라운드 스레드로 버튼 감시"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.HIGH)

        logger.info(f"✅ GPIO 설정 완료 - 스레드 방식 (BUTTON=GPIO{BUTTON_PIN}, LED=GPIO{LED_PIN})")
        return True
    except Exception as e:
        logger.error(f"❌ GPIO 설정 실패: {e}")
        return False


def button_watcher():
    """개선 4: 백그라운드 스레드에서 버튼 감시 (50ms 간격)
    메인 루프 대신 별도 스레드가 담당 → 메인은 sleep만 하여 CPU 점유 최소화
    """
    last_state = GPIO.LOW
    while not _stop_event.is_set():
        try:
            state = GPIO.input(BUTTON_PIN)
            if state == GPIO.HIGH and last_state == GPIO.LOW:
                logger.info("🔘 버튼 눌림 감지! (스레드)")
                print_output()
            last_state = state
        except Exception as e:
            logger.error(f"버튼 읽기 오류: {e}")
        time.sleep(0.05)  # 50ms


def print_output():
    global count, last_print_time

    # Lock으로 동시 출력 방지 (스레드 안전)
    if not _print_lock.acquire(blocking=False):
        logger.debug("출력 중: 요청 무시")
        return

    try:
        current_time = time.time()
        if current_time - last_print_time < 2.0:
            logger.debug("디바운싱: 출력 요청 무시")
            return
        last_print_time = current_time
        count += 1
    except Exception:
        _print_lock.release()
        return

    try:
        logger.info(f"🖨️ 출력 시작 #{count}")

        for i in range(3):
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.1)

        if image_cache and printer_instance:
            # 개선 2: 캐시에서 이미지 선택 (디스크 I/O 없음)
            selected_file = random.choice(list(image_cache.keys()))
            logger.info(f"📸 캐시에서 이미지 선택: {os.path.basename(selected_file)}")
            printer_instance.image(image_cache[selected_file])
            printer_instance.cut()
            logger.info(f"✅ 이미지 출력 완료 #{count}")

        elif printer_instance:
            logger.info("📝 텍스트 출력 모드 (캐시된 이미지 없음)")
            text_content = [
                f"=== Test Print #{count} ===\n",
                "Sam4s Giant 100\n",
                "64-bit Raspberry Pi OS\n",
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

        GPIO.output(LED_PIN, GPIO.HIGH)

    except Exception as e:
        logger.error(f"❌ 출력 오류 #{count}: {e} ({type(e).__name__})")
        GPIO.output(LED_PIN, GPIO.HIGH)
        # 개선 3: USB 에러 시 자동 재연결
        if "usb" in str(e).lower() or "pipe" in str(e).lower() or "errno" in str(e).lower():
            reconnect_printer()

    finally:
        _print_lock.release()


def cleanup():
    try:
        _stop_event.set()  # 버튼 감시 스레드 종료
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        logger.info("🧹 GPIO 정리 완료")
    except Exception as e:
        logger.error(f"정리 오류: {e}")


def main():
    logger.info("🚀 Sam4s Giant 100 프린터 서비스 시작 (인터럽트 방식)")
    logger.info("=" * 60)
    logger.info(f"작업 디렉토리: {os.getcwd()}")
    logger.info(f"사용자: {os.getenv('USER', 'unknown')}")
    logger.info(f"Python: {os.sys.version.split()[0]}")

    logger.info("1/3: 프린터 초기화")
    if not setup_printer():
        logger.error("❌ 프린터 초기화 실패 - 서비스 종료")
        return

    logger.info("2/3: 이미지 사전 캐싱")
    preload_images()

    logger.info("3/3: GPIO 초기화")
    if not setup_gpio():
        logger.error("❌ GPIO 초기화 실패 - 서비스 종료")
        cleanup()
        return

    logger.info("=" * 60)
    logger.info("✅ 모든 초기화 완료!")
    logger.info(f"🔘 버튼(GPIO {BUTTON_PIN})을 누르면 출력됩니다")
    logger.info("📊 60초마다 상태 정보 출력")
    logger.info("⏹️ 종료하려면 Ctrl+C를 누르세요")
    logger.info("=" * 60)

    # 개선 4: 버튼 감시를 백그라운드 스레드로 분리
    watcher = threading.Thread(target=button_watcher, daemon=True)
    watcher.start()
    logger.info("🧵 버튼 감시 스레드 시작")

    heartbeat = 0
    try:
        # 메인 루프는 heartbeat만 담당 - CPU 점유 없음
        while True:
            time.sleep(60)
            heartbeat += 1
            logger.info(f"💓 서비스 실행 중... (heartbeat #{heartbeat}, 총 출력: {count}회)")

    except KeyboardInterrupt:
        logger.info("⏹️ 사용자에 의해 종료")
    except Exception as e:
        logger.error(f"❌ 런타임 오류: {e} ({type(e).__name__})")
    finally:
        cleanup()
        logger.info("🏁 Sam4s 프린터 서비스 종료")


if __name__ == "__main__":
    main()
