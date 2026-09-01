# crumb-tracker

바이브코딩하면서 실제로 뭘 했고 어디서 막혔는지를 추적해서
작업일지와 트러블슈팅 목록으로 정리한다.

## 왜

LLM한테 시키고 → 실행하고 → 에러 나고 → 물어보고 → 고치는 흐름이
전부 터미널에만 남는다. 터미널을 끄면 사라진다.
나중에 "그때 그거 어떻게 고쳤더라"가 안 떠오른다.

## 어떻게

- 수집: zsh 훅(명령어·종료코드·cwd), git, LLM 도구 훅
- 저장: ~/.tracker/log.db (레포 밖. 데이터는 커밋되지 않는다)
- 조회: CLI → MCP 서버 → VS Code 확장 순으로 확장 예정

## 설치

    git clone https://github.com/ahrdyrxkddhfl/crumb-tracker.git
    cd crumb-tracker
    ./install.sh

새 터미널을 열고 `crumb status`로 확인.

## 현재 상태

셸 수집기만 동작. 세션화와 요약은 미구현.

## 알려진 한계

- 여러 줄을 한 번에 붙여넣으면 하나의 이벤트로 기록되고
  종료 코드도 마지막 명령 것만 남는다
- 명령 출력(stdout/stderr)은 수집하지 않는다
- 브라우저에서 쓰는 LLM 대화는 아직 수집 경로가 없다

## 하지 않을 것(혹은 보류)

- 코딩 시간 측정 (WakaTime 같은 도구의 영역)
- 데이터 외부 전송