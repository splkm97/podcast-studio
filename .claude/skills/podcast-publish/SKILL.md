---
name: podcast-publish
description: Transistor.fm에 초안으로 올라간 팟캐스트 회차를 공개 발행한다. 발행된 회차는 RSS로 Spotify 등 배포 앱에 나간다. 사용자가 직접 "/podcast-publish" 또는 "초안 발행해줘", "트랜지스터 publish"처럼 발행을 명시적으로 요청할 때만 쓴다. 파이프라인이 자동으로 부르지 않는다.
disable-model-invocation: true
---

# 회차 발행 (Transistor draft → published)

공개 상태를 바꾸는 유일한 스킬이다. 파이프라인(podcast-orchestrator, podcast-upload)은 초안까지만 올리고, 발행은 사람이 이 스킬을 불러서 한다.

## 원칙

- **사람이 부를 때만 실행한다.** 다른 스킬이나 무인 실행(`claude -p`)에서 부르지 않는다
- **발행 전에 계획을 보여 주고 확인을 받는다.** 발행하면 RSS로 Spotify 등에 바로 나가고, 되돌려도 이미 가져간 앱에는 남을 수 있다
- 사용자가 회차를 지정하면 그 회차만, 지정하지 않으면 초안 전체를 대상으로 한다
- YouTube 공개 전환은 하지 않는다. 업로드 토큰이 `youtube.upload` 범위뿐이라 공개 상태를 바꿀 수 없다. YouTube Studio에서 직접 바꾸라고 안내한다

## 절차

### 1. 계획 확인 (발행하지 않음)

```
python3 -m tools.publish_transistor [episodes/<id> ...]
```

Transistor에서 실제 상태를 읽어 아직 초안인 회차만 고르고, **업로드한 순서**(Transistor 에피소드 id 오름차순)로 번호를 매겨 보여 준다. 이 순서대로 발행해야 피드와 Spotify에서 회차 순서가 맞는다.

### 2. 발행 전 점검

목록의 각 회차에 대해 확인하고 걸리는 것이 있으면 사용자에게 알린다.

- `state.json`이 `done` 또는 `ready_for_upload`인지 (게이트를 모두 통과한 회차인지)
- `report.md`의 "공개 전 확인 포인트"에 남은 항목 (정정이 필요한 주장, 확신이 낮은 표기)
- 실제 인물을 다루는 회차는 공개 정보만 담았는지 report에 근거가 있는지

### 3. 사용자 확인

목록, 발행 순서, 점검에서 나온 주의 사항을 보여 주고 "이대로 발행할까요?"라고 묻는다. 사용자가 일부를 빼라고 하면 남은 회차만 인자로 넘긴다. 확인 없이 다음 단계로 가지 않는다.

### 4. 발행

```
python3 -m tools.publish_transistor --yes [episodes/<id> ...]
```

회차마다 `PATCH /v1/episodes/:id/publish`로 발행하고, `transistor.json`의 `status`와 `published_at`을 갱신하고 `logs/run.log`에 남긴다. 발행 사이에 1.5초 쉬어 API 한도(10초에 10회)를 지키고 발행 시각을 서로 다르게 한다.

중간에 실패하면 거기서 멈춘다. 다시 실행하면 이미 발행된 회차는 건너뛰므로 그대로 재시도하면 된다.

### 5. 보고

- 발행한 회차 목록과 공유 링크(`share_url`)
- Spotify에 쇼가 아직 등록되지 않았다면 podcast-setup 스킬의 "Spotify 등록" 단계를 안내한다. 등록돼 있으면 보통 몇 시간 안에 Spotify에 반영된다고 알린다
- YouTube는 비공개 그대로라는 점

## 하지 않는 것

- 사용자 확인 없이 `--yes`로 실행하지 않는다
- 게이트를 통과하지 않은 회차를 발행하지 않는다
- 발행 취소(unpublish)는 이 스킬의 일이 아니다. 필요하면 Transistor 대시보드에서 사람이 한다
