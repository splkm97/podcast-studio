---
name: podcast-script
description: research.md를 바탕으로 진행자와 전문가 2인 대화형 기술 팟캐스트 대본(script.json)을 쓰고, 대본의 사실 주장을 출처와 교차 검토한다. podcast-orchestrator의 2단계이며, 팟캐스트·오디오용 대화 대본을 써 달라는 요청에도 사용한다.
---

# 팟캐스트 대본

## 화자

- **host (진행자)**: 청취자 대신 묻는다. 모르는 척이 아니라 청취자가 막힐 지점을 짚는다. 정리와 전환을 맡는다
- **expert (전문가)**: 설명한다. 비유와 실제 운영 사례를 들되 research.md 밖의 사실을 지어내지 않는다

## 구조

길이는 **자료 분량에 맞춘다.** 할 말이 끝나면 끝낸다. 늘리려고 반복하지 않는다. 상한은 `podcast.yaml`의 `max_minutes`이고, 분량 추정은 tts 글자 수 ÷ `chars_per_minute`이다.

1. 오프닝: 이번 회차 주제와 왜 지금 이 얘기를 하는지
2. 개념 소개: 처음 나오는 개념을 정의한다. **약어 풀이는 여기서** 한다
3. 본론: 동작 원리 → 실제로 부딪히는 문제 → 대응 방법
4. 정리: 핵심 두세 가지를 진행자가 요약
5. 클로징: 참고 자료는 설명란에 있다고 안내

## 약어 풀이

청취자는 화면을 못 보므로 낯선 약어는 개념 소개 구간에서 **한 번** 풀어 준다. 진행자가 묻고 전문가가 답하는 형태가 자연스럽다.

- host: "알백이 정확히 뭐의 약자예요?" / expert: "롤 베이스드 액세스 컨트롤, 역할 기반 접근 제어예요."
- API, CPU, DNS, HTTP, JSON, YAML, SQL처럼 개발자에게 일상어인 약어는 풀지 않는다. 애매하면 푼다
- 이후 등장은 약어만 쓴다
- 약어가 개념 소개 없이 본론에서 처음 나오게 되면, 대본을 고쳐 소개 구간에 넣는다. 무인 실행이라 "작성자 확인"으로 미룰 수 없다

## script.json

형식은 `references/script-format.md`. 핵심만:

- segment 하나는 한 화자의 한 발화. 길면 문장 단위로 나눈다 (자막 가독성, 300자 이내 권장)
- `src`는 원문 대본이다. **영어 기술 용어는 원래 표기 그대로** 쓴다. 자막에 그대로 나간다
- `tts`는 비워 둔다. 다음 단계 tech-term-hangul이 채운다
- 사실을 주장하는 segment는 `"claim": true`와 근거 `sources`를 단다. 의견, 비유, 질문, 전환 멘트는 claim이 아니다
- `episode`에 `title`(100자 이내), `description`(두세 문장 요약), `tags`를 쓴다

## 사실 교차 검토 (factcheck 게이트)

대본을 다 쓴 뒤, 쓴 사람이 아니라 검토자의 눈으로 본다.

1. `claim: true`인 segment마다 달린 출처를 **원문에서 다시 확인**한다. research.md 요약이 아니라 출처 원문이 기준이다. 요약 단계에서 생긴 왜곡을 잡기 위해서다
2. 판정: `supported` / `unsupported`(출처에 없음) / `contradicted`(출처와 반대)
3. claim 표시가 빠졌지만 사실을 주장하는 segment도 찾아 판정한다
4. 결과를 `gates/factcheck.json`에 쓴다

```json
{"gate": "factcheck", "passed": false,
 "problems": ["s014: contradicted — …"],
 "items": [{"id": "s014", "claim": "…", "sources": ["src2"], "verdict": "contradicted", "note": "…"}]}
```

`unsupported`나 `contradicted`가 하나라도 있으면 `passed: false`. 고칠 때는 주장을 출처에 맞게 바꾸거나 삭제하고, 대화 흐름이 끊기지 않게 앞뒤 segment를 다듬는다.
