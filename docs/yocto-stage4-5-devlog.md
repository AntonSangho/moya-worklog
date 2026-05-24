# Yocto로 나만의 앱 이미지 만들기 — 레시피 작성부터 RPi3 부팅까지

> **시리즈**: moya-worklog Yocto 커스텀 이미지 학습 로드맵 (issue #21)
> **환경**: Yocto scarthgap 5.0.17 / MACHINE=raspberrypi3-64
> **이전 단계**: meta-raspberrypi BSP 추가, meta-moya-worklog 레이어 생성, python3-python-barcode 레시피 작성 완료

---

## 개요

이 글에서는 실제 Python 애플리케이션(moya-worklog)을 Yocto 커스텀 이미지에 통합하는 과정을 기록한다. PyPI 패키지 레시피 작성, 앱 레시피, 이미지 레시피, 그리고 systemd 서비스 자동 시작까지 진행했다. 작업 중 마주친 에러와 해결 방법을 중심으로 서술한다.

---

## 미리 알았더라면 좋았을 것들

### 1. `file://` SRC_URI는 반드시 `files/` 하위 디렉토리에 파일이 있어야 한다

레시피와 같은 디렉토리에 서비스 파일을 두면 Yocto가 찾지 못한다.

```
# 잘못된 구조
recipes-moya/moya-worklog/
├── moya-worklog_git.bb
└── moya-printer.service   ← 여기 두면 ERROR

# 올바른 구조
recipes-moya/moya-worklog/
├── moya-worklog_git.bb
└── files/
    └── moya-printer.service   ← files/ 하위에 위치
```

에러 메시지:
```
ERROR: Unable to get checksum for moya-worklog SRC_URI entry moya-printer.service:
file could not be found
```

---

### 2. `LIC_FILES_CHKSUM`에는 실제 파일명과 md5를 직접 확인해야 한다

`LICENSE`, `LICENCE`, `LICENSE.txt`, `LICENSE.rst` — PyPI 패키지마다 제각각이다. 추측으로 쓰면 반드시 에러가 난다.

```
# 틀린 예 (python-escpos는 LICENCE가 아닌 LICENSE)
LIC_FILES_CHKSUM = "file://LICENCE;md5=34400b68..."

# 올바른 예
LIC_FILES_CHKSUM = "file://LICENSE;md5=b8bfd36d..."
```

**미리 확인하는 방법**: 아래 Python 한 줄로 tarball 내 라이선스 파일명과 md5를 확인할 수 있다.

```python
python3 -c "
import urllib.request, tarfile, io, hashlib
url = 'https://files.pythonhosted.org/packages/source/r/rpi-lgpio/rpi_lgpio-0.6.tar.gz'
with urllib.request.urlopen(url) as r:
    data = r.read()
with tarfile.open(fileobj=io.BytesIO(data)) as t:
    for m in t.getmembers():
        if 'licen' in m.name.lower() or 'copying' in m.name.lower():
            f = t.extractfile(m)
            if f:
                print(m.name, hashlib.md5(f.read()).hexdigest())
"
```

---

### 3. `setup_requires`에 있는 빌드 도구는 `DEPENDS`에 `-native`로 추가해야 한다

Yocto 크로스컴파일 환경에는 `pip`이 없다. `setup.py`가 `setup_requires = ["setuptools_scm"]`처럼 빌드 의존성을 선언하면, Yocto가 pip으로 이를 설치하려다 실패한다.

```
# 에러: No module named pip
# Command 'python3 -m pip wheel setuptools_scm' returned non-zero exit status 1.
```

해결 방법:

```bitbake
# python3-python-barcode_0.15.1.bb, python3-python-escpos_3.1.bb 에서
DEPENDS += "python3-setuptools-scm-native"
```

---

### 4. PyPI 패키지명의 대시(`-`)는 파일명에서 언더스코어(`_`)로 바뀐다

`pypi` bbclass는 `PYPI_PACKAGE` 변수로 URL을 자동 구성하는데, `rpi-lgpio`처럼 대시가 포함된 패키지명은 실제 PyPI 파일명(`rpi_lgpio-0.6.tar.gz`)과 불일치가 발생한다.

```
# pypi 클래스가 시도하는 URL (잘못됨)
https://.../rpi-lgpio/rpi-lgpio-0.6.tar.gz

# 실제 PyPI 파일명
rpi_lgpio-0.6.tar.gz
```

해결: `PYPI_ARCHIVE_NAME`과 `S` 변수를 명시적으로 재정의한다.

```bitbake
PYPI_PACKAGE = "rpi-lgpio"
PYPI_ARCHIVE_NAME = "rpi_lgpio-${PV}.tar.gz"
S = "${WORKDIR}/rpi_lgpio-${PV}"
```

---

### 5. C 확장 모듈에 SWIG가 필요하면 `swig-native`를 DEPENDS에 추가해야 한다

`lgpio`처럼 `.i` (SWIG 인터페이스) 파일을 포함한 패키지는 빌드 시 SWIG가 필요하다. pre-generated C 래퍼가 없으면 컴파일이 실패한다.

```bitbake
# python3-lgpio_0.2.2.0.bb
DEPENDS += "swig-native"

# setup.py의 PYPI 빌드 모드로 C 소스 정적 링크
do_compile:prepend() {
    export PYPI=1
}
```

---

### 6. PyPI 레시피 작성 전에 사전 검증 스크립트를 돌려라

위의 함정들을 bitbake 실행 전에 미리 탐지하는 스크립트를 만들었다.

```bash
python3 meta-moya-worklog/scripts/check_pypi_recipe.py <패키지명> <버전>
```

**출력 예시 (rpi-lgpio 0.6):**
```
==================================================
  rpi-lgpio 0.6
==================================================
[sdist]   rpi_lgpio-0.6.tar.gz
          sha256: 84579b11...
          ⚠ PYPI_ARCHIVE_NAME 재정의 필요 (대시→언더스코어)
          PYPI_ARCHIVE_NAME = "rpi_lgpio-0.6.tar.gz"
          S = "${WORKDIR}/rpi_lgpio-0.6"

[license] LICENSE.txt  md5=10a1f024...
          LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=10a1f024..."

[build]   setup_requires: (없음)
          C 확장: (없음) — 순수 Python 패키지
```

한 번 실행으로 sha256, 라이선스 파일명, PYPI_ARCHIVE_NAME 필요 여부, SWIG 의존성을 모두 파악할 수 있다.

---

### 7. 앱 레시피에서 하드코딩된 경로는 `do_install`에서 sed로 처리한다

`print_sam4s_production.py`에는 `/home/pi/moya-worklog/printer.log` 같은 경로가 하드코딩되어 있다. Yocto 이미지에는 `pi` 사용자도 없고 해당 경로도 없다.

```bitbake
do_install() {
    install -d ${D}/opt/moya-worklog
    install -m 0755 ${S}/print_sam4s_production.py ${D}/opt/moya-worklog/

    # 하드코딩된 경로 치환
    sed -i 's|/home/pi/moya-worklog/|/opt/moya-worklog/|g' \
        ${D}/opt/moya-worklog/print_sam4s_production.py
}
```

`${D}`는 패키징 스테이징 루트로, 이미지에서는 `/`로 매핑된다. 따라서 코드는 `/opt/moya-worklog/`에 설치된다.

---

### 8. systemd 서비스 파일도 Yocto용으로 수정해야 한다

Raspbian용 서비스 파일을 그대로 쓰면 경로와 사용자 문제가 생긴다.

| 항목 | Raspbian | Yocto |
|---|---|---|
| `User=` | `pi` | 제거 (root 사용) |
| `WorkingDirectory` | `/home/pi/moya-worklog` | `/opt/moya-worklog` |
| `ExecStart` | `venv-64bit/bin/python ...` | `/usr/bin/python3 ...` |
| `Wants=` | `usb_modeswitch.service` | 제거 (필요 여부 검증 후 추가) |

서비스 자동 시작은 레시피에 두 줄로 설정한다:

```bitbake
inherit systemd
SYSTEMD_SERVICE:${PN} = "moya-printer.service"
SYSTEMD_AUTO_ENABLE = "enable"
```

---

### 9. `core-image-base`는 기본적으로 sysvinit을 사용한다

systemd가 당연히 있을 거라고 생각했다가 부팅 후 `systemctl not found`를 마주쳤다.

`local.conf`에 아래를 추가해야 systemd가 init manager로 동작한다:

```
DISTRO_FEATURES:append = " systemd usrmerge"
VIRTUAL-RUNTIME_init_manager = "systemd"
DISTRO_FEATURES_BACKFILL_CONSIDERED:append = " sysvinit"
VIRTUAL-RUNTIME_initscripts = "systemd-compat-units"
```

`usrmerge`가 빠지면 아래 에러가 난다:

```
ERROR: Nothing PROVIDES 'systemd'
systemd was skipped: missing required distro feature 'usrmerge'
```

scarthgap(systemd 255+)부터는 `/bin` → `/usr/bin` 통합(`usrmerge`)이 systemd의 필수 조건이다.

---

### 10. systemd를 추가하면 이미지 크기와 빌드 시간이 크게 늘어난다

systemd 의존성 체인이 자동으로 포함되기 때문이다:

```
systemd → openssl → glib-2.0 → dbus → libpam → zstd → libunistring ...
```

처음 빌드는 오래 걸리지만, sstate-cache가 쌓이면 이후 빌드는 빠르다. systemd vs sysvinit 비교(Stage 7)는 **별도 build 디렉토리**로 진행해야 cache 오염을 막을 수 있다.

```bash
source poky/oe-init-build-env build-systemd   # systemd 이미지
source poky/oe-init-build-env build-sysvinit  # sysvinit 이미지 (비교용)
```

`DL_DIR`과 `SSTATE_DIR`은 `/mnt/shared/yocto/`로 공유하므로 다운로드는 중복되지 않는다.

---

## 빌드 순서 정리

```bash
# 1. 의존성 레시피
bitbake python3-python-escpos
bitbake python3-lgpio
bitbake python3-rpi-lgpio

# 2. 앱 레시피
bitbake moya-worklog

# 3. 전체 이미지
bitbake moya-image-rpi3

# 4. SD카드 기록
sudo umount /dev/sdc1 /dev/sdc2
sudo bmaptool copy moya-image-rpi3-raspberrypi3-64.rootfs.wic.bz2 /dev/sdc
```

---

## 최종 레이어 구조

```
meta-moya-worklog/
├── conf/layer.conf
├── scripts/
│   └── check_pypi_recipe.py          ← PyPI 레시피 사전 검증 도구
├── recipes-core/images/
│   └── moya-image-rpi3.bb            ← 커스텀 이미지 레시피
├── recipes-moya/moya-worklog/
│   ├── moya-worklog_git.bb           ← 앱 레시피 (git 소스)
│   └── files/
│       └── moya-printer.service      ← Yocto용 수정 서비스 파일
└── recipes-python/
    ├── python-barcode/python3-python-barcode_0.15.1.bb
    ├── python-escpos/python3-python-escpos_3.1.bb
    ├── lgpio/python3-lgpio_0.2.2.0.bb
    └── rpi-lgpio/python3-rpi-lgpio_0.6.bb
```

---

## 검증 결과

RPi3 부팅 후:

```bash
$ systemctl is-enabled moya-printer.service
enabled

$ systemctl status moya-printer.service
# → activating (USB 프린터 미연결로 exit code 1, 예상된 동작)
```

서비스가 부팅 시 자동으로 시작을 시도함을 확인. USB 프린터 + GPIO 버튼 실제 동작 검증은 Stage 6에서 진행 예정.

---

## 다음 단계

- **Stage 6**: USB 프린터 + GPIO 버튼 실제 동작 검증, udev 룰 패키징
- **Stage 7**: systemd vs sysvinit vs busybox 이미지 크기·부팅 시간 비교
