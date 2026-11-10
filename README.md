# podcast-studio

주제와 참고 링크만 주면 Claude Code가 자료 수집 → 2인 대화 대본 → TTS 정규화 → 음성 합성 → 영상 → YouTube 비공개 업로드와 Transistor.fm 초안 업로드(Spotify 배포)까지 무인으로 진행하는 프로젝트예요.

## 구조

```
.claude/skills/   단계별 스킬 + 오케스트레이터 (판단이 필요한 일)
tools/            게이트와 합성·렌더·업로드 스크립트 (결정적인 일)
podcast.yaml      설정
episodes/         회차별 산출물
```

| 단계 | 스킬 | 게이트 |
|---|---|---|
| 자료 수집 | podcast-research | links |
| 대본 | podcast-script | factcheck |
| TTS 정규화 | tech-term-hangul | script_lint |
| 음성 합성 | podcast-tts | audio, stt |
| 영상 | podcast-video | 렌더 성공 |
| 업로드 | podcast-upload | upload.json (YouTube), transistor.json (Transistor) |

## 설정 가이드

처음 한 번만 하면 돼요. 키를 발급받는 단계는 Claude Code 대화형 세션에서 `/podcast-setup`을 실행하면 하나씩 안내해 주고, 끝나면 `python3 -m tools.check_env`로 확인해요.

### 1. 도구 설치 (macOS 기준)

```
brew install uv ffmpeg-full
brew install --cask font-noto-sans-cjk-kr
```

- **ffmpeg**: 자막을 영상에 입히려면 libass와 freetype이 들어 있는 빌드가 필요해요. `ffmpeg-full`은 keg-only라서 PATH에 잡히지 않으니 `.env`의 `FFMPEG`에 경로를 적어요 (`/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`)
- **폰트**: 제목 카드와 자막은 `podcast.yaml`의 `video.font`(기본 Noto Sans CJK KR)를 써요
- **커버 이미지(선택)**: `assets/cover.png`를 두면 영상 배경으로 써요. 없으면 단색 배경에 제목 카드를 넣어요
- **에이전트**: Claude Code(`claude`). Codex CLI도 같은 스킬을 읽어요 (`.agents/skills`가 `.claude/skills`를 가리키는 심링크예요)

### 2. 파이썬 환경

```
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
source .venv/bin/activate
```

Homebrew 파이썬은 전역 pip 설치를 막고 의존성도 없어요. 새 터미널에서는 `source .venv/bin/activate`부터 하고, 이 문서의 `python3 -m tools.…` 명령은 활성화된 쉘에서 실행해요. 활성화하지 않았다면 `.venv/bin/python -m tools.<이름>`으로 실행해요. 그냥 `python3`로 돌리면 `check_env`가 종료 코드 2를 내요.

### 3. `.env` 만들기

```
cp .env.example .env && chmod 600 .env
```

`.env`는 `.gitignore`에 들어 있고, 도구들이 시작할 때 자동으로 읽어요. 쉘에서 이미 export한 값이 우선해요. 키는 채팅에 붙여 넣지 말고 이 파일에 직접 넣어요.

| 키 | 필요할 때 | 받는 곳 |
|---|---|---|
| `GOOGLE_TTS_API_KEY` | 기본 TTS (`tts.engine: google`) | 4단계 |
| `YOUTUBE_CLIENT_SECRETS` | YouTube 업로드 (필수) | 5단계. 기본값이 5단계의 저장 경로라 그대로 두면 돼요 |
| `YOUTUBE_TOKEN` | 선택. 토큰 경로를 바꿀 때만 | 기본 `~/.config/podcast-studio/youtube-token.json` |
| `TRANSISTOR_API_KEY` | Transistor 업로드 (`transistor.enabled: true`) | 6단계 |
| `TRANSISTOR_SHOW_ID` | 선택. 계정에 쇼가 둘 이상일 때만 | 6단계 |
| `FFMPEG` | `ffmpeg-full`처럼 PATH에 없는 ffmpeg를 쓸 때 | 1단계 |
| `CLOVA_CLIENT_ID`, `CLOVA_CLIENT_SECRET` | `tts.engine: clova`일 때만 (유료, 무료 제공량 없음) | NCP 콘솔 |

### 4. Google Cloud TTS 키

Chirp 3: HD 음성은 월 100만 자까지 무료예요. 회차 하나가 대략 7천~9천 자예요.

1. [Google Cloud 콘솔](https://console.cloud.google.com)에서 프로젝트를 만들고 결제 계정을 연결해요. 무료 제공량 안에서는 청구되지 않지만 API를 켜려면 결제 계정이 필요해요
2. API 및 서비스 → 라이브러리에서 **Cloud Text-to-Speech API**를 사용 설정해요
3. 사용자 인증 정보 → **API 키**를 만들고, 키 제한에서 Cloud Text-to-Speech API만 허용해요
4. `.env`의 `GOOGLE_TTS_API_KEY`에 넣어요. 키는 `AIza`로 시작해요. 다른 형식의 자격 증명을 넣으면 401 "API keys are not supported"가 나요
5. 결제 → 예산 및 알림에서 소액 예산 알림을 걸어 두면 안전해요

목소리는 `podcast.yaml`의 `tts.voices`에서 바꿔요 (기본: 진행자 `ko-KR-Chirp3-HD-Kore`, 전문가 `ko-KR-Chirp3-HD-Charon`).

### 5. YouTube 업로드

1. 업로드할 Google 계정에 **YouTube 채널**이 있어야 해요. 없으면 업로드가 `youtubeSignupRequired`로 실패해요
2. 4단계와 같은 프로젝트에서 **YouTube Data API v3**를 사용 설정해요
3. OAuth 동의 화면을 외부로 만들고, 업로드할 계정을 **테스트 사용자**로 추가해요
4. OAuth 클라이언트 ID를 **데스크톱 앱**으로 만들고 JSON을 `~/.config/podcast-studio/client_secret.json`에 저장해요(`chmod 600`). 저장소 안에 두지 않아요
5. 브라우저 인증을 한 번 해요

```
python3 -m tools.upload_youtube --auth
```

동의 화면이 "테스트" 상태면 토큰이 7일 뒤 만료돼요. 업로드가 토큰 문제로 멈추면 `python3 -m tools.upload_youtube --auth`만 다시 실행하면 돼요.

업로드는 항상 비공개이고 "변경·합성 콘텐츠"(AI 생성) 표시가 켜져요. 토큰 권한이 업로드뿐이라 공개 전환은 YouTube Studio에서 직접 해요.

### 6. Transistor.fm (Spotify 배포용)

Transistor는 유료 호스팅이에요(무료 체험 후 월 구독). 쓰지 않으면 `podcast.yaml`의 `transistor.enabled`를 false로 두면 돼요.

1. [Transistor](https://transistor.fm)에서 쇼를 만들고 이름, 설명, 카테고리, 언어(한국어), 정사각형 커버(1400~3000px)를 채워요. 이 정보가 그대로 Spotify에 나가요
2. 대시보드 → Account → API에서 키를 복사해 `.env`의 `TRANSISTOR_API_KEY`에 넣어요
3. 쇼가 둘 이상이면 아래로 id를 확인해 `TRANSISTOR_SHOW_ID`에 넣어요

```
python3 -m tools.upload_transistor --shows
```

### 7. 확인

```
python3 -m tools.check_env
```

`env OK`가 나오면 끝이에요. 키 이름과 경로만 출력하고 값은 보여 주지 않아요. YouTube 항목은 항상 필수이고, `tts.engine: dryrun`이면 점검 전체를 건너뛰어요. 종료 코드 1이면 빠진 항목만 다시 하면 되고, 2면 파이썬 환경(2단계) 문제예요. 오케스트레이터도 회차를 시작하기 전에 이 점검을 돌려요.

### 8. Spotify 등록 (첫 회차를 발행한 뒤, 쇼마다 한 번)

Spotify에는 회차를 따로 올리지 않아요. Transistor 쇼를 한 번 등록하면, 그 뒤로 Transistor에서 발행한 회차를 Spotify가 RSS로 가져가요.

1. Transistor에서 회차를 하나 이상 발행해요. 초안만 있으면 제출할 수 없어요
2. 쇼 화면의 **Distribution** 탭에서 Spotify를 제출해요. 보통 하루 안에 반영돼요. 같은 탭에서 Apple Podcasts 등에도 낼 수 있어요
3. 재생 통계는 [Spotify for Creators](https://creators.spotify.com)에서 봐요

### 다른 TTS 엔진 (선택)

- **로컬 Qwen3-TTS** (`tts.engine: qwen`): 키가 필요 없어요. `uv pip install -r requirements-qwen.txt`로 설치하고, 첫 합성 때 모델(약 4GB)을 내려받아요. 한국어 화자가 Sohee 하나뿐이고, 합성이 실제 음성 길이만큼 걸려요
- **Gemini TTS**: `podcast.yaml` 주석에 설정 예시가 있지만, Gemini 음성은 API 키 인증을 받지 않아요(401). 지금 어댑터는 API 키만 지원해서 쓸 수 없어요

### 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| `uploadLimitExceeded` | 채널의 하루 업로드 개수 한도예요. API 할당량과 별개라 코드로 풀 수 없어요. 다음 날 다시 올리고, 채널 전화번호 인증(youtube.com/verify)을 해 두면 한도가 늘 수 있어요 |
| `youtubeSignupRequired` (401) | 계정에 YouTube 채널이 없어요. 채널을 만든 뒤 다시 올려요 |
| Google TTS 401 "API keys are not supported" | `GOOGLE_TTS_API_KEY`에 `AIza…` API 키가 아닌 값이 들어 있어요 |
| `libx265` dyld 오류, 자막 필터 없음 | 일반 `ffmpeg` 빌드 문제예요. `ffmpeg-full`을 설치하고 `.env`의 `FFMPEG`에 경로를 적어요 |
| faster-whisper `metadata_errors` TypeError | PyAV 버전 문제예요. `requirements.txt`의 `av<16`으로 다시 설치해요 |
| Transistor 429 | API 한도(10초에 10회)예요. 도구가 기다렸다가 다시 시도해요. 몇 분간 막히면 잠시 뒤 다시 실행해요 |
| `already uploaded` | 같은 회차를 두 번 올리지 않게 막는 기록(`upload.json`, `transistor.json`)이 있어요. 정말 다시 올릴 때만 그 파일을 정리해요 |

## 실행

대화형:

```
claude
> 팟캐스트 만들어줘. 주제: etcd 백업 자동화. 참고: https://…
```

무인:

```
claude -p "팟캐스트 만들어줘. 주제: … 참고: …" --permission-mode acceptEdits
```

결과는 `episodes/<id>/report.md`에 남아요. YouTube는 비공개로 올라가니, 영상을 확인한 뒤 YouTube Studio에서 직접 공개로 바꾸면 돼요. Transistor는 초안으로 올라가요. 확인한 뒤 대화형 세션에서 `/podcast-publish`를 실행하면 초안을 업로드 순서대로 발행하고, 발행된 회차는 RSS로 Spotify에 나가요. 이 스킬은 발행 전에 목록을 보여 주고 확인을 받아요.

## 드라이런

`podcast.yaml`에서 `tts.engine: dryrun`으로 바꾸면 API 비용 없이 흐름을 검증해요. 음성 대신 톤이 들어가고, STT 검증과 업로드는 건너뛰어요.
