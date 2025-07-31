# Mail Pilot 📧

> Gmail API와 ChatGPT를 활용한 지능형 이메일 마케팅 및 자동 응답 시스템

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-72%25-yellow.svg)](https://codecov.io/)
[![Tests](https://img.shields.io/badge/tests-83%20passed-brightgreen.svg)](tests/)

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [시스템 요구사항](#시스템-요구사항)
- [설치 가이드](#설치-가이드)
- [사용 방법](#사용-방법)
- [프로젝트 구조](#프로젝트-구조)
- [설정](#설정)
- [API 문서](#api-문서)
- [테스트](#테스트)
- [보안](#보안)
- [문제 해결](#문제-해결)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 🚀 개요

Mail Pilot은 **Gmail API**와 **OpenAI ChatGPT**를 통합하여 아웃바운드 마케팅 이메일 발송과 고객 응답을 자동화하는 시스템입니다. YouTube Shorts Auto Generator 제품을 홍보하고, 고객 응답에 대해 맥락을 이해한 지능적인 답변을 생성하며, Zoom 미팅 일정까지 제안하는 완벽한 세일즈 자동화 도구입니다.

### 왜 Mail Pilot인가?

- **🚀 마케팅 자동화**: YouTube Shorts Auto Generator 제품 홍보 이메일 대량 발송
- **👤 개인화된 아웃리치**: 각 고객의 이름을 포함한 맞춤형 마케팅 메시지
- **⏰ 시간 절약**: 반복적인 이메일 응답을 자동화하여 업무 효율성 향상
- **💬 일관된 커뮤니케이션**: AI 기반 응답으로 일관된 톤과 품질 유지
- **🧠 맥락 인식**: 대화 히스토리를 기반으로 한 지능적인 응답 생성
- **📅 미팅 스케줄링**: Zoom 미팅 제안 및 추적 기능 내장

## ✨ 주요 기능

### 핵심 기능

- **🚀 아웃바운드 마케팅**
  - YouTube Shorts Auto Generator 제품 홍보 이메일 캠페인
  - 개인화된 마케팅 메시지 생성 (고객 이름 포함)
  - 발송 이력 추적 및 중복 방지
  - 캠페인별 관리 기능

- **🤖 AI 기반 이메일 응답**
  - OpenAI GPT-4 모델을 활용한 자연스러운 응답 생성
  - 제품 관련 질문에 대한 지능적인 답변
  - 대화 맥락을 고려한 개인화된 메시지 작성
  - 제품 특징을 자연스럽게 강조

- **📧 Gmail 통합**
  - OAuth2 기반 안전한 Gmail API 연동
  - 읽지 않은 이메일 자동 감지 및 처리
  - 스레드 기반 대화 관리
  - 고객 이메일 필터링 (중요 고객만 처리)

- **🗓️ Zoom 미팅 관리**
  - 제품 데모를 위한 15분 미팅 제안
  - 데모 세션 스케줄링 추적
  - 중복 미팅 예약 방지
  - 미팅 확정 자동 감지

- **✅ 승인 워크플로우**
  - 모든 응답 초안을 사용자가 검토
  - Rich 터미널 UI를 통한 직관적인 승인/거부
  - 한글 입력 지원 (UTF-8 인코딩)
  - 안전한 입력 처리

- **💾 데이터 관리**
  - 스레드별 대화 컨텍스트 저장
  - 마케팅 캠페인 발송 이력 추적
  - JSON 기반 영구 저장소
  - 첫 실행 시 10개 제한, 이후 새 이메일만 처리

### 고급 기능

- **🔐 보안**
  - 환경 변수를 통한 안전한 API 키 관리
  - 민감 정보 자동 마스킹
  - OAuth2 토큰 자동 갱신
  - `.env` 파일 git 커밋 방지

- **📊 로깅 시스템**
  - 구조화된 JSON 로깅
  - 환경별 로그 레벨 설정
  - 민감 데이터 자동 필터링
  - 써드파티 라이브러리 로그 제어

- **🧪 테스트**
  - 83개의 포괄적인 단위 테스트
  - 72% 코드 커버리지
  - 모의 객체를 활용한 API 테스트
  - pytest 기반 테스트 스위트

## 🛠️ 기술 스택

### 백엔드
- **Python 3.12+** - 최신 Python 기능 활용
- **Google API Python Client** - Gmail API 통합
- **OpenAI Python SDK** - ChatGPT API 연동
- **Rich** - 향상된 터미널 UI

### 개발 도구
- **pytest** - 테스트 프레임워크
- **pytest-cov** - 코드 커버리지 측정
- **pytest-mock** - 모의 객체 지원
- **uv** - 빠른 Python 패키지 관리자

## 💻 시스템 요구사항

### 필수 요구사항
- Python 3.12 이상
- macOS (Keychain 지원 권장) 또는 Linux/Windows
- 인터넷 연결
- Gmail 계정
- OpenAI API 계정

### 권장 사양
- 메모리: 4GB RAM 이상
- 저장 공간: 100MB 이상
- 터미널: UTF-8 및 256색 지원

## 📦 설치 가이드

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/mailPilot.git
cd mailPilot
```

### 2. Python 환경 설정

```bash
# Python 버전 확인
python --version  # 3.12+ 필요

# uv 설치 (권장)
pip install uv

# 가상 환경 생성 및 활성화
uv venv
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
# uv 사용 (권장 - 빠른 설치)
uv pip install -e .

# 개발 의존성 포함 설치
uv pip install -e ".[dev]"
```

### 4. Gmail API 설정

#### Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Gmail API 활성화:
   - "API 및 서비스" → "라이브러리"
   - "Gmail API" 검색 및 활성화

#### OAuth2 인증 정보 생성

1. "API 및 서비스" → "사용자 인증 정보"
2. "사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
3. 애플리케이션 유형: "데스크톱 앱" 선택
4. 이름 입력 (예: "Mail Pilot Desktop")
5. JSON 파일 다운로드
6. `config/credentials.json`으로 저장

#### OAuth 동의 화면 구성

1. "API 및 서비스" → "OAuth 동의 화면"
2. 필수 정보 입력:
   - 앱 이름: Mail Pilot
   - 사용자 지원 이메일
   - 개발자 연락처 정보
3. 필요한 스코프 추가:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`

### 5. OpenAI API 키 설정

#### 환경 변수 설정

```bash
# .env.sample을 .env로 복사
cp .env.sample .env

# .env 파일 편집
vi .env  # 또는 원하는 에디터 사용

# OPENAI_API_KEY 설정
OPENAI_API_KEY=sk-your-api-key-here
```

**중요**: `.env` 파일은 절대 git에 커밋하지 마세요!

### 6. 고객 이메일 목록 설정

`config/customer_emails.txt` 파일을 편집하여 고객 정보 추가:

```
# Customer Email Addresses
# Format: Name <email@example.com>

John Doe <john.doe@example.com>
Jane Smith <jane.smith@company.com>
김철수 <chulsoo@example.kr>
```

## 🎯 사용 방법

### 기본 실행

```bash
# UTF-8 환경으로 실행 (권장)
./run.sh

# 또는 직접 실행
export PYTHONIOENCODING=utf-8
uv run python src/main.py
```

### 첫 실행 시

1. Gmail 인증 브라우저 창이 열립니다
2. Google 계정으로 로그인
3. Mail Pilot에 Gmail 접근 권한 부여
4. 인증 완료 후 터미널로 돌아옴

### 메인 메뉴

```
🤖 Email Marketing & Auto-Responder System

Options:
1. Send marketing emails (YouTube Shorts Auto Generator)
2. Check for new emails and responses
3. View active threads
4. Exit

Select option (1-4): 
```

### 워크플로우

#### 1. 마케팅 이메일 발송

1. 옵션 1 선택
2. 각 고객에게 보낼 개인화된 이메일 검토
3. 승인(y) 또는 거부(n) 선택
4. 발송 완료 후 이력 자동 저장

#### 2. 고객 응답 처리

1. 옵션 2 선택
2. 고객 이메일만 필터링하여 표시
3. AI가 생성한 응답 초안 검토
4. 승인 시 자동 발송

#### 3. 대화 관리

- 옵션 3으로 진행 중인 대화 확인
- Zoom 미팅 스케줄 상태 추적
- 대화 히스토리 확인

### 고급 사용법

#### 마케팅 캠페인 관리

```python
# src/marketing/outbound.py에서 캠페인 템플릿 수정
def generate_marketing_email(self, name: str) -> Dict[str, str]:
    subject = f"Hi {name} - Your Custom Subject"
    body = f"""Your custom marketing message..."""
```

#### 고객 필터링 설정

```python
# 첫 실행 시 처리할 이메일 수 변경
max_results = 20  # 기본값: 10
```

## 📁 프로젝트 구조

```
mailPilot/
├── config/                      # 설정 파일
│   ├── credentials.json        # Gmail OAuth2 인증 정보 (git 제외)
│   ├── customer_emails.txt     # 고객 이메일 목록
│   └── HOW_TO_GET_CREDENTIALS.md  # Gmail API 설정 가이드
│
├── data/                        # 런타임 데이터 (git 제외)
│   ├── token.json              # OAuth2 액세스 토큰
│   ├── thread_memory.json      # 대화 기록 저장소
│   ├── marketing_sent.json     # 마케팅 발송 이력
│   └── last_processed.json     # 마지막 처리 상태
│
├── scripts/                     # 유틸리티 스크립트
│   └── keychain_env.py         # macOS Keychain 헬퍼
│
├── src/                         # 소스 코드
│   ├── approval/               # 이메일 승인 인터페이스
│   │   └── interface.py        # Rich UI 구현
│   │
│   ├── chatgpt/                # ChatGPT 통합
│   │   └── client.py           # OpenAI API 클라이언트
│   │
│   ├── gmail/                  # Gmail API 통합
│   │   └── client.py           # Gmail API 클라이언트
│   │
│   ├── marketing/              # 마케팅 기능
│   │   └── outbound.py         # 아웃바운드 이메일 캠페인
│   │
│   ├── storage/                # 데이터 저장소
│   │   └── thread_memory.py    # 대화 기록 관리
│   │
│   ├── utils/                  # 유틸리티 모듈
│   │   └── logging_config.py   # 로깅 설정
│   │
│   └── main.py                 # 메인 애플리케이션
│
├── tests/                       # 테스트 스위트
│   ├── test_*.py               # 단위 테스트 파일들
│   └── ...
│
├── .gitignore                   # Git 제외 파일
├── CLAUDE.md                    # AI 개발 가이드라인
├── pyproject.toml               # 프로젝트 설정
├── pytest.ini                   # 테스트 설정
├── README.md                    # 이 문서
├── run.sh                       # 실행 스크립트
└── uv.lock                      # 의존성 잠금 파일
```

## ⚙️ 설정

### 환경 변수

`.env` 파일에서 설정:

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | - | ✅ |
| `PYTHONIOENCODING` | Python 인코딩 | `utf-8` | ✅ |
| `MAILPILOT_ENV` | 실행 환경 | `development` | ❌ |
| `MAILPILOT_LOG_DIR` | 로그 디렉토리 | `logs/` | ❌ |

### 고객 이메일 형식

`config/customer_emails.txt`:
```
# Format: Name <email@example.com>
John Doe <john@example.com>
Jane Smith <jane@company.com>
```

### 마케팅 발송 이력

`data/marketing_sent.json`:
```json
{
  "youtube_shorts": {
    "email@example.com": {
      "sent_at": "2025-07-20T15:10:11.612105",
      "status": "sent"
    }
  }
}
```

## 🧪 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest

# 상세 출력
uv run pytest -v

# 코드 커버리지
uv run pytest --cov=src --cov-report=term-missing

# HTML 리포트 생성
uv run pytest --cov=src --cov-report=html
```

### 테스트 통계
- **총 테스트**: 83개
- **코드 커버리지**: 72%
- **테스트 시간**: ~1초

## 🔒 보안

### API 키 관리

#### 환경 변수 사용
```bash
# .env 파일에 API 키 저장
echo "OPENAI_API_KEY=sk-..." >> .env

# 환경 변수로 직접 설정 (임시)
export OPENAI_API_KEY="sk-..."
```

### 보안 정책

1. **금지사항**:
   - `.env` 파일 git 커밋 금지
   - API 키 하드코딩 금지
   - 민감 정보 로깅 금지

2. **필수사항**:
   - 환경 변수 사용
   - OAuth2 토큰 자동 갱신
   - HTTPS 전용 통신

### 로깅 보안
- API 키, 토큰 자동 마스킹
- 이메일 주소 부분 마스킹
- 민감 정보 필터링

## 🔧 문제 해결

### 일반적인 문제

#### 1. UnicodeDecodeError

**해결책**:
```bash
# run.sh 스크립트 사용
./run.sh

# 또는 환경 변수 설정
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8
```

#### 2. Gmail API 인증 실패

**해결책**:
```bash
# 토큰 재생성
rm data/token.json
uv run python src/main.py
```

#### 3. OpenAI API 오류

**해결책**:
```bash
# API 키 확인
echo $OPENAI_API_KEY

# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API 사용량 확인
# https://platform.openai.com/usage
```

#### 4. 로깅 오류

**증상**: OpenAI/httpx 라이브러리 로깅 오류

**해결책**: 이미 수정됨 - SafeMessageAdapter가 자동 처리

### 디버깅 팁

```bash
# 상세 로깅 활성화
export MAILPILOT_ENV=development

# 로그 확인
tail -f logs/mailpilot.log
```

## 🤝 기여하기

Mail Pilot 프로젝트에 기여해 주셔서 감사합니다!

### 기여 가이드라인

1. 이슈 생성
2. 포크 & 클론
3. 브랜치 생성: `feature/기능명`
4. 코드 작성 (타입 힌트 사용)
5. 테스트 작성
6. 커밋 & PR

### 코딩 스타일

- PEP 8 준수
- 타입 힌트 사용
- 독스트링 작성
- 테스트 커버리지 70% 이상

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- Google Gmail API 팀
- OpenAI ChatGPT 팀
- Python 커뮤니티
- 모든 기여자들

## 📞 연락처

- **개발자**: Sueun Cho
- **이메일**: sueun.dev@gmail.com
- **버그 리포트**: [GitHub Issues](https://github.com/yourusername/mailPilot/issues)

---

<div align="center">
  Made with ❤️ for YouTube Shorts Auto Generator
</div>