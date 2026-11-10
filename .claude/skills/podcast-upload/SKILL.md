---
name: podcast-upload
description: 완성된 episode.mp4를 YouTube에 비공개로 업로드하고 결과를 upload.json에 남긴다. podcast-orchestrator의 마지막 단계이며, 모든 게이트를 통과한 회차에만 사용한다.
---

# YouTube 업로드

```
python3 -m tools.upload_youtube episodes/<id>
```

- **모든 게이트가 통과했을 때만** 실행한다. 하나라도 실패 기록이 남아 있으면 실행하지 않는다
- **공개 범위는 설정값(기본 private)을 따른다.** 이 스킬은 공개 상태를 바꾸지 않는다. 공개 전환은 사용자가 영상을 확인한 뒤 직접 한다
- **AI 생성 콘텐츠 표시는 설정값(`youtube.contains_synthetic_media`, 기본 true)을 따른다.** 음성이 TTS 합성이라 YouTube의 변경·합성 콘텐츠 공개 항목(`status.containsSyntheticMedia`)을 켜서 올린다
- 제목과 설명은 `script.json`의 `episode`에서, 참고 자료 목록은 `sources.json`에서 만든다. 설명 끝에 TTS 합성 음성임을 밝힌다
- `upload.json`이 이미 있으면 스크립트가 거부한다. **같은 회차를 두 번 올리지 않기 위해서다.** 실패 후 재시도라도 이 파일을 지우지 않는다
- 토큰이 없거나 갱신에 실패하면 스크립트가 중단 메시지를 낸다. 무인 실행에서는 고칠 수 없으므로 재시도하지 않고 중단해, report에 `python3 -m tools.upload_youtube --auth`를 사람이 실행해야 한다고 남긴다
