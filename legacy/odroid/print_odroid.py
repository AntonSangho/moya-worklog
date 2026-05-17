#!/usr/bin/env python3
"""
Odroid C4 + Sam4s Giant 100 프린터 제어 스크립트
스레드 방식, 이미지 캐싱, USB 자동 재연결
"""

import logging
import os
import random
import threading
import time
from logging.handlers import RotatingFileHandler
from typing import Optional

import RPi.GPIO as GPIO
from escpos.printer import Usb
from PIL import Image

# ── 로깅 ──────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            "/home/odroid/moya-worklog/printer.log",
            maxBytes=1 * 1024 * 1024,
            backupCount=3,
        ),
        logging.StreamHandler(),
    ],
    force=True,
)
logger = logging.getLogger(__name__)

# ── 설정 ──────────────────────────────────────────────────────────────────────
BUTTON_PIN: int = 25
LED_PIN: int = 12

VENDOR_ID: int = 0x1C8A
PRODUCT_ID: int = 0x3A0E
IN_EP: int = 0x81
OUT_EP: int = 0x02

IMAGE_DIR: str = "/home/odroid/moya-worklog/image"
IMAGE_FILES: list[str] = [
    f"{IMAGE_DIR}/w{i}_2022.png" for i in range(1, 6)
]

DEBOUNCE_SEC: float = 2.0
BUTTON_POLL_SEC: float = 0.05
RECONNECT_WAIT_SEC: float = 2.0
MAX_RECONNECT: int = 3

# ── 전역 상태 ─────────────────────────────────────────────────────────────────
printer: Optional[Usb] = None
image_cache: dict[str, Image.Image] = {}
print_count: int = 0
last_print_time: float = 0.0
_print_lock = threading.Lock()
_stop_event = threading.Event()


# ── 프린터 ────────────────────────────────────────────────────────────────────

def connect_printer() -> bool:
    global printer
    try:
        printer = Usb(VENDOR_ID, PRODUCT_ID, in_ep=IN_EP, out_ep=OUT_EP)
        logger.info("프린터 연결 성공")
        return True
    except Exception as e:
        logger.error(f"프린터 연결 실패: {e}")
        return False


def reconnect_printer() -> bool:
    """출력 오류 후 최대 MAX_RECONNECT회 재연결 시도"""
    global printer
    for attempt in range(1, MAX_RECONNECT + 1):
        logger.info(f"프린터 재연결 시도 {attempt}/{MAX_RECONNECT}")
        try:
            if printer:
                try:
                    printer.close()
                except Exception:
                    pass
            time.sleep(RECONNECT_WAIT_SEC)
            printer = Usb(VENDOR_ID, PRODUCT_ID, in_ep=IN_EP, out_ep=OUT_EP)
            logger.info("프린터 재연결 성공")
            return True
        except Exception as e:
            logger.error(f"재연결 실패 ({attempt}/{MAX_RECONNECT}): {e}")
    logger.error("프린터 재연결 포기")
    return False


# ── 이미지 ────────────────────────────────────────────────────────────────────

def preload_images() -> int:
    """시작 시 이미지 전처리 및 메모리 캐싱 — 버튼 응답 속도 향상"""
    loaded = 0
    for path in IMAGE_FILES:
        if os.path.exists(path):
            try:
                image_cache[path] = Image.open(path).resize((480, 1000))
                logger.info(f"캐시: {os.path.basename(path)}")
                loaded += 1
            except Exception as e:
                logger.error(f"이미지 캐시 실패 {os.path.basename(path)}: {e}")
    logger.info(f"캐시 완료: {loaded}개 이미지")
    return loaded


# ── 출력 ──────────────────────────────────────────────────────────────────────

def print_output() -> None:
    global print_count, last_print_time

    if not _print_lock.acquire(blocking=False):
        return

    try:
        now = time.time()
        if now - last_print_time < DEBOUNCE_SEC:
            return
        last_print_time = now
        print_count += 1

        logger.info(f"출력 시작 #{print_count}")
        _blink_led(times=3)

        if image_cache and printer:
            path = random.choice(list(image_cache.keys()))
            logger.info(f"선택: {os.path.basename(path)}")
            printer.image(image_cache[path])
            printer.cut()
            logger.info(f"출력 완료 #{print_count}")
        elif printer:
            _print_text()
        else:
            logger.error("프린터 미연결")

        GPIO.output(LED_PIN, GPIO.HIGH)

    except Exception as e:
        logger.error(f"출력 오류 #{print_count}: {e} ({type(e).__name__})")
        GPIO.output(LED_PIN, GPIO.HIGH)
        if any(kw in str(e).lower() for kw in ("usb", "pipe", "errno")):
            reconnect_printer()
    finally:
        _print_lock.release()


def _blink_led(times: int) -> None:
    for _ in range(times):
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.1)


def _print_text() -> None:
    logger.info("텍스트 출력 모드")
    lines = [
        f"=== Print #{print_count} ===\n",
        "Sam4s Giant 100 / Odroid C4\n",
        f"시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"총 출력: {print_count}회\n",
        "=" * 30 + "\n",
    ]
    for line in lines:
        printer.text(line)
    printer.cut()
    logger.info(f"텍스트 출력 완료 #{print_count}")


# ── GPIO ──────────────────────────────────────────────────────────────────────

def setup_gpio() -> bool:
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.HIGH)
        logger.info(f"GPIO 설정 완료 (BUTTON=GPIO{BUTTON_PIN}, LED=GPIO{LED_PIN})")
        return True
    except Exception as e:
        logger.error(f"GPIO 설정 실패: {e}")
        return False


def button_watcher() -> None:
    """버튼 감시 데몬 스레드 — 50ms 간격 폴링, Rising Edge 감지"""
    last_state = GPIO.LOW
    while not _stop_event.is_set():
        try:
            state = GPIO.input(BUTTON_PIN)
            if state == GPIO.HIGH and last_state == GPIO.LOW:
                logger.info("버튼 눌림")
                print_output()
            last_state = state
        except Exception as e:
            logger.error(f"버튼 읽기 오류: {e}")
        time.sleep(BUTTON_POLL_SEC)


def cleanup() -> None:
    _stop_event.set()
    try:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        logger.info("GPIO 정리 완료")
    except Exception as e:
        logger.error(f"정리 오류: {e}")


# ── 진입점 ────────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("Sam4s 프린터 서비스 시작 (Odroid C4)")
    logger.info("=" * 60)
    logger.info(f"사용자: {os.getenv('USER', 'unknown')}  Python: {os.sys.version.split()[0]}")

    if not connect_printer():
        logger.error("프린터 초기화 실패 — 종료")
        return

    preload_images()

    if not setup_gpio():
        logger.error("GPIO 초기화 실패 — 종료")
        cleanup()
        return

    watcher = threading.Thread(target=button_watcher, daemon=True, name="ButtonWatcher")
    watcher.start()

    logger.info("=" * 60)
    logger.info(f"준비 완료 — GPIO{BUTTON_PIN} 버튼을 누르면 출력")
    logger.info("=" * 60)

    heartbeat = 0
    try:
        while True:
            time.sleep(60)
            heartbeat += 1
            logger.info(f"heartbeat #{heartbeat}  총 출력: {print_count}회")
    except KeyboardInterrupt:
        logger.info("사용자 종료")
    except Exception as e:
        logger.error(f"런타임 오류: {e} ({type(e).__name__})")
    finally:
        cleanup()
        logger.info("서비스 종료")


if __name__ == "__main__":
    main()
