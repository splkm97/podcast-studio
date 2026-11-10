# 기본 표기 사전

형식은 한 줄에 `- 영어 = 한글` 이에요. 파이프라인의 STT 역검증도 이 파일을 읽으니 형식을 지켜 주세요.
맥락이 다르면 SKILL.md의 판단 순서가 우선해요.


## 플랫폼·오케스트레이션
- Kubernetes = 쿠버네티스
- k8s = 쿠버네티스
- kubectl = 큐브컨트롤
- kubelet = 큐블릿
- kubeadm = 큐브어드민
- etcd = 엣시디
- Pod = 파드
- Deployment = 디플로이먼트
- StatefulSet = 스테이트풀셋
- DaemonSet = 데몬셋
- Namespace = 네임스페이스
- Ingress = 인그레스
- Service = 서비스
- ConfigMap = 컨피그맵
- Secret = 시크릿
- Operator = 오퍼레이터
- CRD = 씨알디
- Helm = 헬름
- chart = 차트
- OpenStack = 오픈스택
- Nova = 노바
- Neutron = 뉴트론
- Keystone = 키스톤
- Cinder = 신더
- Docker = 도커
- containerd = 컨테이너디
- Podman = 포드맨
- vCluster = 브이클러스터

## 네트워크
- nginx = 엔진엑스
- ingress-nginx = 인그레스 엔진엑스
- Envoy = 엔보이
- Istio = 이스티오
- Cilium = 실리움
- Calico = 캘리코
- eBPF = 이비피에프
- CNI = 씨엔아이
- DNS = 디엔에스
- TLS = 티엘에스
- mTLS = 엠티엘에스
- HTTP = 에이치티티피
- gRPC = 지알피씨
- TCP = 티씨피
- UDP = 유디피
- proxy = 프록시
- Gateway API = 게이트웨이 에이피아이
- VPN = 브이피엔
- WireGuard = 와이어가드

## 관측성
- Prometheus = 프로메테우스
- Grafana = 그라파나
- Loki = 로키
- Tempo = 템포
- OpenTelemetry = 오픈텔레메트리
- OTel = 오텔
- VictoriaMetrics = 빅토리아메트릭스
- InfluxDB = 인플럭스디비
- Telegraf = 텔레그래프
- Jaeger = 예거
- metric = 메트릭
- trace = 트레이스
- span = 스팬
- exporter = 익스포터
- scrape = 스크레이프

## 데이터·스토리지
- PostgreSQL = 포스트그레스
- MySQL = 마이에스큐엘
- SQL = 에스큐엘
- NoSQL = 노에스큐엘
- Redis = 레디스
- Kafka = 카프카
- MongoDB = 몽고디비
- Ceph = 세프
- MinIO = 미니오
- S3 = 에스쓰리
- Velero = 벨레로
- snapshot = 스냅샷
- replica = 레플리카
- shard = 샤드

## 보안·시크릿
- OpenBao = 오픈바오
- Vault = 볼트
- ESO = 이에스오
- OAuth = 오어스
- OIDC = 오아이디씨
- JWT = 제이더블유티
- RBAC = 알백
- SSO = 에스에스오
- Keycloak = 키클록

## 언어·도구
- Go = 고
- Golang = 고랭
- Rust = 러스트
- Python = 파이썬
- TypeScript = 타입스크립트
- React = 리액트
- Node.js = 노드제이에스
- Git = 깃
- GitHub = 깃허브
- GitLab = 깃랩
- Terraform = 테라폼
- Ansible = 앤서블
- Argo CD = 아르고 씨디
- Jenkins = 젠킨스
- YAML = 야믈
- JSON = 제이슨
- CLI = 씨엘아이
- SDK = 에스디케이
- IDE = 아이디이

## AI·LLM
- LLM = 엘엘엠
- GPU = 지피유
- CUDA = 쿠다
- vLLM = 브이엘엘엠
- inference = 인퍼런스
- token = 토큰
- embedding = 임베딩
- RAG = 래그
- fine-tuning = 파인튜닝
- quantization = 퀀타이제이션
- KV cache = 케이브이 캐시

## 운영 일반
- DevOps = 데브옵스
- SRE = 에스알이
- CI/CD = 씨아이씨디
- pipeline = 파이프라인
- rollout = 롤아웃
- rollback = 롤백
- failover = 페일오버
- DR = 디알
- SLA = 에스엘에이
- SLO = 에스엘오
- latency = 레이턴시
- throughput = 스루풋
- cache = 캐시
- queue = 큐
- sidecar = 사이드카
- SaaS = 사스
- PaaS = 파스
- IaaS = 이아스
- EOL = 이오엘

## 단위
- ms = 밀리초
- GB = 기가바이트
- MB = 메가바이트
- TB = 테라바이트
- vCPU = 브이씨피유
- QPS = 큐피에스

## 재해 복구·인증 (20261109-kubernetes-dr-study-curriculum 회차에서 추가)
- API = 에이피아이
- RPO = 알피오
- RTO = 알티오
- MTD = 엠티디
- HA = 에이치에이
- CA = 씨에이
- Certificate Authority = 서티피케이트 어소리티
- KMS = 케이엠에스
- PV = 피브이
- PVC = 피브이씨
- CSI = 씨에스아이
- NIST = 니스트
- VM = 브이엠
- GA = 지에이
- FAQ = 에프에이큐
- IP = 아이피
- ID = 아이디
- DB = 디비
- AKS = 에이케이에스
- RBD = 알비디
- GitOps = 깃옵스
- Consistency = 컨시스턴시
- Availability = 어베일러빌리티
- Partition tolerance = 파티션 톨러런스

## Kubernetes DR 시리즈 1차(EP1~EP5)에서 추가
- BIA = 비아이에이
- BCP = 비씨피
- AWS = 에이더블유에스
- IBM = 아이비엠
- IT = 아이티
- IaC = 아이에이씨
- CNCF = 씨엔씨에프
- PR = 피알
- UID = 유아이디
- KubeCon = 큐브콘
- Raft = 래프트
- Paxos = 팩소스
- quorum = 쿼럼
- Borg = 보그
- Omega = 오메가
- revision = 리비전
- etcdctl = 이티씨디 컨트롤
- etcdutl = 이티씨디 유틸
- StorageClass = 스토리지 클래스
- VolumeSnapshot = 볼륨 스냅샷
- Persistent Volume = 퍼시스턴트 볼륨
- Persistent Volume Claim = 퍼시스턴트 볼륨 클레임
- Container Storage Interface = 컨테이너 스토리지 인터페이스
- reconciliation = 리컨실리에이션
- cattle = 캐틀
- manifest = 매니페스트
- spec = 스펙
- drift = 드리프트
- Google = 구글
- Amazon = 아마존
- Microsoft = 마이크로소프트
- CERN = 세른
- Extended Play = 익스텐디드 플레이
- R&B = 알앤비

## Kubernetes DR 시리즈 2차(EP6~EP10)에서 추가
- admission = 애드미션
- SR = 에스알
- control plane = 컨트롤 플레인
- fencing = 펜싱
- split-brain = 스플릿 브레인
- IdP = 아이디피
- NTP = 엔티피
- IAM = 아이에이엠
- CBC = 씨비씨
- GCM = 지씨엠
- PKI = 피케이아이
- kubeconfig = 큐브컨피그
- % = 퍼센트
