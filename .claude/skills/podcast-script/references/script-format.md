# script.json 형식

```json
{
  "episode": {
    "title": "쿠버네티스 엣시디 백업, 어디까지 자동화할까",
    "description": "두세 문장 요약. 업로드 설명란 첫 단락이 된다.",
    "tags": ["Kubernetes", "etcd", "DR"]
  },
  "segments": [
    {"id": "s001", "speaker": "host",
     "src": "오늘은 etcd 백업 얘기를 해 볼게요.",
     "tts": "오늘은 엣시디 백업 얘기를 해 볼게요."},
    {"id": "s002", "speaker": "expert",
     "src": "etcd는 클러스터의 모든 상태를 저장하는 key-value 저장소예요.",
     "tts": "엣시디는 클러스터의 모든 상태를 저장하는 키 밸류 저장소예요.",
     "claim": true, "sources": ["src1"],
     "tts_notes": ["key-value → 키 밸류: 하이픈 읽지 않음"]}
  ]
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | `s001`부터 순서대로. 고쳐 쓸 때 번호를 다시 매기지 않는다 (합성 캐시가 id 기준) |
| `speaker` | O | `podcast.yaml`의 `tts.voices` 키 (`host`, `expert`) |
| `src` | O | 원문. 자막용 |
| `tts` | O | 음차본. TTS 입력. 라틴 문자, 기호, 소수점 없음 |
| `claim` | | 사실 주장이면 `true` |
| `sources` | claim이면 O | `sources.json`의 id |
| `tts_notes` | | 확신 낮은 음차 기록 |

segment를 중간에 추가해야 하면 `s014a`처럼 접미사를 붙인다.
