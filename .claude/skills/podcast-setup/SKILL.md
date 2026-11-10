---
name: podcast-setup
description: 팟캐스트 파이프라인에 필요한 시크릿(.env)과 YouTube OAuth 토큰을 준비한다. .env 템플릿을 만들고, TTS 키(Google Cloud TTS 또는 CLOVA Voice)와 Google OAuth 클라이언트를 발급받는 절차를 안내하고, tools.check_env로 검증한다. 최초 설정, 키 교체, 토큰 만료 시, 또는 podcast-orchestrator의 사전 점검이 실패했을 때 사용한다.
---

# 사전 설정

사람이 함께하는 대화형 스킬이다. 콘솔에서 키를 발급받고 브라우저로 인증하는 일은 사람만 할 수 있다. 무인 실행(`claude -p`)에서는 이 스킬을 돌리지 않는다.

## 원칙

- **시크릿 값을 채팅으로 받지 않는다.** 대화 기록에 남기 때문이다. 사용자가 편집기로 `.env`를 직접 채우게 한다. 이 스킬은 `.env`의 값을 읽거나 출력하지 않는다
- **검증은 `python3 -m tools.check_env` 하나로 한다.** 이 도구는 키 이름과 경로만 출력한다
- 이미 통과한 항목은 다시 발급받게 하지 않는다. `check_env`가 보고한 항목만 진행한다

## 절차

### 1. 현재 상태 확인

```
python3 -m tools.check_env
```

종료 코드가 0이면 이미 준비된 상태라 여기서 끝낸다. 1이면 출력에 나온 항목만 아래 단계로 처리한다.

### 2. .env 템플릿 만들기

저장소 루트에 `.env`가 **없을 때만** 아래 내용으로 만들고 `chmod 600 .env`를 실행한다. 파일이 이미 있으면 덮어쓰지 않는다. 빠진 키가 있을 때만 빈 줄로 덧붙인다. `.env`는 `.gitignore`에 들어 있다.

```
# podcast-studio secrets. Never commit this file.
# Google Cloud Text-to-Speech API key (tts.engine: google)
GOOGLE_TTS_API_KEY=
# CLOVA Voice, only when tts.engine: clova (paid plan, no free tier)
# CLOVA_CLIENT_ID=
# CLOVA_CLIENT_SECRET=
# Google OAuth client JSON (Desktop app). Keep it outside the repo.
YOUTUBE_CLIENT_SECRETS=~/.config/podcast-studio/client_secret.json
# Optional: token path (default ~/.config/podcast-studio/youtube-token.json)
# YOUTUBE_TOKEN=
```

이미 쉘에서 export한 값은 `.env`보다 우선한다.

### 3. TTS 키 발급 (`podcast.yaml`의 `tts.engine`에 맞는 것만)

#### 3a. Google Cloud TTS (`GOOGLE_TTS_API_KEY`가 비어 있을 때, 기본 엔진)

Chirp 3: HD 음성은 월 100만 자까지 무료다. 4단계의 YouTube용 Google Cloud 프로젝트와 같은 프로젝트를 쓰면 된다.

1. Google Cloud 콘솔(https://console.cloud.google.com)에서 프로젝트를 고르고, 결제 계정을 연결한다. 무료 제공량 안에서는 청구되지 않지만 API 사용 설정에 결제 계정이 필요하다
2. API 및 서비스 → 라이브러리에서 **Cloud Text-to-Speech API**를 사용 설정한다
3. API 및 서비스 → 사용자 인증 정보 → 사용자 인증 정보 만들기 → **API 키**를 만든다
4. 만든 키를 편집해 API 제한사항을 **키 제한 → Cloud Text-to-Speech API**만 허용하도록 한다. 키가 새도 다른 API에 쓰이지 않게 하기 위해서다
5. 키를 `.env`의 `GOOGLE_TTS_API_KEY`에 붙여 넣고 저장한다
6. 무료 제공량을 넘기지 않으려면 결제 → 예산 및 알림에서 소액 예산 알림을 걸어 두도록 권한다

키를 넣은 뒤 두 목소리로 짧게 합성해 본다. 목소리 이름이 틀렸거나 키 제한이 잘못되었으면 여기서 오류가 난다.

```
python3 -c "from pathlib import Path; from tools.common import load_config; from tools.tts import get_engine; c=load_config()['tts']; e=get_engine(c); [e.synth('안녕하세요, 테스트입니다.', v, Path(f'/tmp/tts-{k}.wav')) for k,v in c['voices'].items()]; print('ok')"
```

`/tmp/tts-host.wav`, `/tmp/tts-expert.wav`를 사용자가 들어 보고 목소리를 바꾸고 싶다면 `podcast.yaml`의 `tts.voices.*.name`을 다른 `ko-KR-Chirp3-HD-<이름>`으로 고친다.

#### 3b. CLOVA Voice (`tts.engine: clova`이고 `CLOVA_*`가 비어 있을 때)

유료 플랜이며 무료 제공량이 없다. 애플리케이션을 만들면 호출이 없어도 기본료가 나간다. 사용자가 명시적으로 원할 때만 안내한다.

1. NAVER Cloud Platform 콘솔(https://console.ncloud.com)에 로그인한다. 결제 수단이 등록되어 있어야 한다
2. Services → AI·NAVER API → Application에서 애플리케이션을 등록한다. 서비스 선택에서 **CLOVA Voice**를 체크한다
3. 등록한 애플리케이션의 인증 정보에서 Client ID와 Client Secret을 확인한다
4. `.env`의 `CLOVA_CLIENT_ID`, `CLOVA_CLIENT_SECRET`에 붙여 넣고 저장한다

콘솔 메뉴 이름은 바뀔 수 있다. 사용자가 메뉴를 찾지 못하면 NCP의 CLOVA Voice 공식 문서를 찾아 현재 경로를 알려 준다.

### 4. Google OAuth 클라이언트 발급 (`YOUTUBE_CLIENT_SECRETS`에 문제가 있을 때)

1. Google Cloud 콘솔(https://console.cloud.google.com)에서 프로젝트를 만들거나 고른다
2. API 및 서비스 → 라이브러리에서 **YouTube Data API v3**를 사용 설정한다
3. OAuth 동의 화면에서 사용자 유형을 외부로 정하고, 업로드할 채널의 Google 계정을 **테스트 사용자**로 추가한다
4. 사용자 인증 정보 → OAuth 클라이언트 ID 만들기에서 애플리케이션 유형을 **데스크톱 앱**으로 고른다
5. JSON을 내려받아 `~/.config/podcast-studio/client_secret.json`에 두고 `chmod 600`을 실행한다. 저장소 안에 두지 않는다. 다른 경로에 두었다면 `.env`의 `YOUTUBE_CLIENT_SECRETS`를 그 경로로 고친다

동의 화면이 "테스트" 상태면 갱신 토큰이 7일 뒤 만료된다. 업로드가 토큰 만료로 멈추면 5단계만 다시 하면 된다고 알린다.

### 5. YouTube 토큰 발급 (토큰이 없을 때)

4단계가 끝난 뒤 실행한다. 브라우저가 열리면 사용자가 테스트 사용자로 등록한 계정으로 허용한다.

```
python3 -m tools.upload_youtube --auth
```

### 6. 검증

사용자가 `.env`를 저장했다고 하면 다시 확인한다.

```
python3 -m tools.check_env
```

0이 나올 때까지 출력된 항목의 단계만 반복한다. 통과하면 "설정 완료"를 알린다. podcast-orchestrator에서 넘어왔다면 원래 요청으로 돌아가 이어서 진행한다.

## 하지 않는 것

- `.env`나 client_secret JSON의 내용을 읽거나 채팅에 출력하지 않는다
- `podcast.yaml`의 `tts.engine`을 사용자 동의 없이 `dryrun`으로 바꿔 점검을 피하지 않는다
