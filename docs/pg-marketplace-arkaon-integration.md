# PG 입점 마켓플레이스 + ARKAON 연결 자동화 — 실행 설계 v1

## 핵심 모델
땡처리는 **PG사도 입점하는 결제솔루션 마켓플레이스**다. PG사는 결제상품을 등록하고 판매자는 등록 PG사의 조건을 비교해 선택한다. 땡처리는 연결 워크플로를 제공하고 ARKAON은 승인된 기술문서를 분석해 어댑터 초안·설치 안내·검증 결과를 만든다. PG의 법적 가맹점 심사와 계약을 우회하지 않는다.

## 역할과 소유권
- PG_OPERATOR: PG사 법인·담당자 인증, 서비스 상품 등록, 공식 API 문서 및 샌드박스 정보 제출, 요금·정산조건 업데이트 요청.
- SELLER: 입점·로그인, 상품 등록, PG 비교·선택, 자신의 PG 계정 연결 승인, 시험결제 확인.
- PLATFORM_OPERATOR: PG사 심사·공개 승인, 계약 검토, 기술지원 작업배정, 서비스 상태 관리.
- ARKAON_AGENT: 허용된 문서만 읽어 API 호환성 진단, 커넥터 코드/설정 패키지 초안, 테스트 및 오류 분석. 실행 권한은 제한.
- ETERNIAN_AUDITOR: 증거기반 최종 감사. 운영 승인권자와 분리.

## PG 입점 및 연결 상태기계
PG 신청: APPLIED → BUSINESS_VERIFIED → LEGAL_REVIEW → API_SECURITY_REVIEW → SANDBOX_VERIFIED → PUBLISHED (또는 REJECTED/SUSPENDED).
PG 상품: DRAFT → REVIEW → LISTED → WITHDRAWN. 상품별 수수료, 정산주기, 지원 결제수단, 계약 적용범위, API 버전, 웹훅·환불·에스크로·분리정산 지원여부와 증거 URL을 버전 관리.
판매자 연결: PG_SELECTED → PG_CONTRACT_PENDING → MERCHANT_UNDERWRITING → CONNECTION_REQUESTED → ARKAON_ANALYSIS → ADAPTER_PROPOSED → SECURITY_REVIEW → SANDBOX_PASS → MERCHANT_ACTIVATED → LIVE_APPROVED. 실패·중단·해지 상태 별도.
PG사가 입점했다고 모든 판매자에게 자동 개통되는 것은 아니다. 판매자별 가맹점 심사와 권한 확인을 거친다.

## 아르카온 커넥터 생성·지원 절차
1. PG 담당자가 공식 API 명세(OpenAPI 등), 인증방식, 샌드박스, 웹훅·환불·정산 스펙, SDK 라이선스·배포 허용범위를 제출한다.
2. 플랫폼이 자료의 출처·사용권·악성 입력 여부를 검증하고 격리된 분석 작업을 발행한다. 비밀키는 전달하지 않는다.
3. ARKAON이 공통 PGConnector 인터페이스와 차이를 분석해 지원 가능 기능/누락 기능/위험도 및 구현 계획을 생성한다.
4. ARKAON이 버전 고정 어댑터, 서버측 환경변수 템플릿(비밀값 없음), 설정 안내서, 자동화 테스트 초안을 별도 브랜치/PR로 제안한다.
5. CI에서 정적검사, 의존성/라이선스 검사, 샌드박스 결제·환불, 위조 웹훅·중복 요청·타임아웃·재시도·금액 변조·테넌트 격리 테스트를 수행한다.
6. ETERNIAN이 코드/로그/테스트/계약 증거를 감사하고 운영자가 승인한다.
7. 플랫폼의 **관리형 서버측 커넥터**로 배포하고 판매자별 merchant account를 연결한다. 판매자에게는 브라우저 기반 설정마법사와 검증 리포트를 제공한다.
8. 판매자가 자체 쇼핑몰 연동을 원할 때만 검증된 설치 패키지/플러그인 또는 설정파일을 제공한다. 서명된 아티팩트·체크섬·버전·롤백 절차를 포함하고 판매자 동의 없이 기기나 서버에 자동 업로드하지 않는다.
9. PG 버전 변경·오류·해지 시 영향을 받는 판매자와 거래만 증분 분석하고 기존 거래의 결제·환불·대사는 원 PG로 유지한다.

## API 및 DB 계약(제안)
- `pg_providers`: id, legal_entity, verified_status, published_at
- `pg_offerings`: provider_id, offering_version, fee_terms, supported_methods, eligibility, settlement_cycle, api_version, evidence
- `pg_api_specs`: provider_id, digest, license, reviewed_at, compatibility
- `seller_pg_connections`: seller_id, offering_id, merchant_account_ref, state, credential_vault_ref, approved_at
- `connector_builds`: provider_id, spec_digest, source_commit, artifact_digest, ci_proof, audit_verdict, release_version
- `connector_jobs`: seller_id, connection_id, phase, errors, retry_key, assigned_agent, approval_event
- `payment_attempts`: order_id, seller_id, provider_id, merchant_account_ref, amount, status, idempotency_key
- `audit_events`: actor, action, resource, evidence_digest, timestamp

서비스 경계 예시: `POST /pg/providers/apply`, `POST /pg/offerings`, `GET /pg/offerings`, `POST /sellers/me/pg-connections`, `POST /connections/{id}/analyze`, `GET /connections/{id}/report`, `POST /connections/{id}/activate`. 모든 변경 API에 역할·소유권·상태전이 검증과 감사로그 필수.

## 결제/배포 안전 불변조건
- 판매자가 PG 선택권을 갖고 플랫폼이 임의로 변경하지 않는다.
- PG별/판매자별 비밀키는 서버 비밀저장소에 격리; 브라우저·GitHub·ARKAON 학습자료로 유출 금지.
- 판매자 자체 쇼핑몰 업로드는 별도 명시적 승인·서명 검증·최소권한 연결만 허용.
- 실제 결제승인은 PG 서버 검증으로만 확정; 웹훅 서명·금액·주문·멱등 검증 및 대사 필수.
- 플랫폼 직접판매는 자체 PG 가맹점 연결을 사용.
- 다른 판매자/PG의 설정·거래·계약에 접근 불가.
- PG 간 수수료 비교는 표준화된 기준·유효기간·광고 표시 정책을 적용.
- 계약, 보안검사, 정산·환불, 장애복구, 개인정보 및 규제 검토가 완료되기 전 실결제 기능 공개 금지.

## 단계별 인수조건
P1: PG사 입점 신청·심사·상품 카탈로그·판매자 비교 화면 (실제 DB/RBAC).
P2: 판매자 PG 선택·계약·가맹점 심사 상태·관리형 연결 마법사.
P3: ARKAON 문서 분석·커넥터 초안·테스트·감사 PR 자동화.
P4: 1개 PG 샌드박스 end-to-end + 장애/환불/대사 검증.
P5: PG별 운영 계약 및 인허가/등록 검토, 실운영 제한적 개통, 감시·롤백.
