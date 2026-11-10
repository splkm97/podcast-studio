---
name: podcast-video
description: episode.mp3에 정지 커버 이미지와 원문 자막을 입혀 YouTube용 episode.mp4를 만든다. podcast-orchestrator의 5단계이며, 팟캐스트 오디오를 영상으로 바꿀 때 사용한다.
---

# 영상 변환

YouTube는 오디오 파일을 받지 않으므로 정지 이미지 영상으로 감싼다.

```
python3 -m tools.render_video episodes/<id>
```

- **커버**: `podcast.yaml`의 `video.cover` 이미지를 1920x1080에 맞춰 쓴다. 파일이 없으면 회차 제목을 넣은 단색 타이틀 카드를 만든다
- **자막**: `src`(원문 대본)로 만든다. 음성은 음차본이지만 자막에는 영어 기술 용어가 원래 표기로 보여야 청취자가 검색할 수 있다. 타이밍은 합성 단계의 segment 시각을 쓰고, 긴 segment는 문장 길이 비율로 나눈다. `subtitles.srt`도 회차 폴더에 남는다
- **폰트**: `video.font` (기본 Noto Sans CJK KR). 시스템에 설치돼 있어야 한글이 깨지지 않는다

렌더가 실패하면 대부분 환경 문제(ffmpeg의 libass 미포함, 폰트 미설치)라서 재시도하지 않고 중단해 report에 원인을 남긴다.
