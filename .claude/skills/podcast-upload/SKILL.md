---
name: podcast-upload
description: 완성된 회차를 YouTube(episode.mp4, 비공개)와 Transistor.fm(episode.mp3, 초안)에 올리고 결과를 upload.json과 transistor.json에 남긴다. Transistor에 올라간 회차는 발행 후 RSS로 Spotify에 전달된다. podcast-orchestrator의 마지막 단계이며, 모든 게이트를 통과한 회차에만 사용한다.
---

# 업로드 (YouTube + Transistor)

두 곳에 따로 올린다. 서로 독립이라 한쪽이 실패해도 다른 쪽은 진행하고, 결과는 각자 기록한다.

```
python3 -m tools.upload_youtube episodes/<id>   # episode.mp4 → upload.json
python3 -m tools.upload_transistor episodes/<id>   # episode.mp3 → transistor.json (transistor.enabled: true일 때만)
```

## 공통 규칙

- **모든 게이트가 통과했을 때만** 실행한다. 하나라도 실패 기록이 남아 있으면 실행하지 않는다
- **공개 상태를 바꾸지 않는다.** YouTube는 `youtube.privacy`(기본 private), Transistor는 `transistor.status`(기본 draft)를 따른다. 공개 전환과 발행은 사용자가 결과물을 확인한 뒤 직접 한다
- 제목과 설명은 `script.json`의 `episode`에서, 참고 자료 목록은 `sources.json`에서 만든다. 설명 끝에 TTS 합성 음성임을 밝힌다
- **같은 회차를 두 번 올리지 않는다.** `upload.json`이나 `transistor.json`이 이미 있으면 해당 스크립트가 거부한다. 실패 후 재시도라도 이 파일들을 지우지 않는다
- 인증 문제(토큰 없음, 키 없음, 갱신 실패)는 무인 실행에서 고칠 수 없다. 재시도하지 않고 중단해 report에 사람이 할 일을 남긴다

## YouTube

- **AI 생성 콘텐츠 표시는 설정값(`youtube.contains_synthetic_media`, 기본 true)을 따른다.** 음성이 TTS 합성이라 변경·합성 콘텐츠 공개 항목(`status.containsSyntheticMedia`)을 켜서 올린다
- 토큰이 없거나 갱신에 실패하면 사람이 `python3 -m tools.upload_youtube --auth`를 실행해야 한다
- `uploadLimitExceeded`는 채널의 하루 업로드 한도다. 코드로 풀 수 없으니 회차를 `ready_for_upload`로 두고 나중에 다시 시도한다

## Transistor

- `episode.mp3`를 올리고 Transistor 쇼에 에피소드를 만든다. 기본은 `transistor.status: draft`라 초안으로만 남는다. 설명은 HTML로 만들어 참고 자료를 링크로 넣는다
- 쇼는 `TRANSISTOR_SHOW_ID`로 정한다. 계정에 쇼가 하나뿐이면 비워 둬도 그 쇼를 쓴다. 쇼가 여럿인데 비어 있으면 스크립트가 쇼 목록을 보여 주고 멈춘다
- 키가 없으면(`TRANSISTOR_API_KEY`) 사람이 podcast-setup 스킬의 Transistor 단계를 해야 한다
- API는 10초에 10회로 제한된다. 회차 하나에 3~4회만 부르므로 연속 업로드도 문제없다
- 결과 보고에 `transistor.json`의 `share_url`과 상태를 적는다

## Spotify까지 가는 길

Spotify에는 회차마다 올리지 않는다. **쇼(팟캐스트)를 한 번만 Spotify에 등록**하면, 그 뒤로는 Transistor RSS 피드에 발행된 회차를 Spotify가 자동으로 가져간다.

1. 쇼 등록이 아직이면 podcast-setup 스킬의 "Spotify 등록" 단계를 사람에게 안내한다 (최초 1회)
2. 회차마다 사용자가 Transistor 대시보드에서 초안을 확인하고 **발행(Publish)**한다. 초안은 RSS에 나가지 않아 Spotify에 보이지 않는다
3. 발행 후 Spotify 반영까지 보통 몇 시간이 걸린다

report.md에는 회차마다 "Transistor 초안 → 사람이 발행하면 Spotify에 반영"을 사람이 할 일로 남긴다.
