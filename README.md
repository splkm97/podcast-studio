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

## 준비

1. `ffmpeg`(libass 포함), Noto Sans CJK KR 폰트, Python 3.10+
2. `uv venv --python 3.12 .venv && uv pip install -r requirements.txt` 후 `source .venv/bin/activate` 상태에서 `claude` 실행 (Homebrew Python은 전역 pip 설치를 막아요)
3. 시크릿: 대화형 세션에서 `/podcast-setup`을 실행하면 `.env` 템플릿을 만들고 발급 절차를 안내해요. 저장소 루트의 `.env`는 도구들이 자동으로 읽어요(이미 export한 값이 우선)
   - `GOOGLE_TTS_API_KEY`: Google Cloud TTS API 키 (기본 엔진, Chirp 3: HD 월 100만 자 무료)
   - `CLOVA_CLIENT_ID`, `CLOVA_CLIENT_SECRET`: `tts.engine: clova`일 때만. NCP CLOVA Voice 애플리케이션 인증 정보 (유료)
   - Gemini Flash TTS: 새 키 없이 `GOOGLE_TTS_API_KEY`를 그대로 써요. 키가 속한 Google Cloud 프로젝트에서 Agent Platform(Vertex AI) API를 켜고, `podcast.yaml`의 `tts.voices`에 `model: gemini-2.5-flash-tts`를 넣으면 돼요(예시는 주석 참고)
   - 로컬 Qwen3-TTS: `tts.engine: qwen`. 키가 필요 없어요. `uv pip install -r requirements-qwen.txt`로 torch와 `qwen-tts`를 설치하고, 첫 합성 때 모델 가중치를 내려받아요. 한국어 기본 화자는 Sohee 하나뿐이에요
   - `YOUTUBE_CLIENT_SECRETS`: Google Cloud에서 만든 OAuth 클라이언트(데스크톱 앱) JSON 경로
4. YouTube 최초 인증 (한 번, 브라우저 필요): `python3 -m tools.upload_youtube --auth`
5. Transistor API 키(`TRANSISTOR_API_KEY`)를 `.env`에 넣고, Spotify에는 쇼를 한 번만 등록해요. 절차는 `/podcast-setup`이 안내해요. Transistor를 안 쓰면 `podcast.yaml`의 `transistor.enabled`를 false로 두면 돼요
5. 확인: `python3 -m tools.check_env` (오케스트레이터도 시작 전에 이 점검을 돌려요)

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

결과는 `episodes/<id>/report.md`에 남아요. 업로드는 항상 비공개라서, 영상을 확인한 뒤 YouTube Studio에서 직접 공개로 바꾸면 돼요. Transistor는 초안으로 올라가니, 대시보드에서 발행하면 RSS를 통해 Spotify에도 나가요.

## 드라이런

`podcast.yaml`에서 `tts.engine: dryrun`으로 바꾸면 API 비용 없이 흐름을 검증해요. 음성 대신 톤이 들어가고, STT 검증과 업로드는 건너뛰어요.
