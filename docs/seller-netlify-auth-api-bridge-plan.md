# 판매자 대시보드: 정적 Netlify → 인증 API 연결 설계

상태: **개발 설계 전용 / 미배포 / 실사용 금지**.

## 저장소 확인 결과

- `index.html`, `seller-dashboard-demo.html`: 정적 브라우저 시연 화면.
- `README.md`: Netlify 배포 디렉터리 `.`, 빌드 명령 없음.
- `backend/seller_dashboard_http_session_bridge.py`: 신뢰된 세션 쿠키 추출.
- `backend/seller_dashboard_route_adapter.py`: GET 전용 필터 검증.
- `backend/seller_dashboard_session_service.py`: 세션→회원권한→판매자 범위 재고 조회.
- `backend/seller_dashboard_read_response.py`: 프레임워크 독립 응답 생성.
- `db/migrations/001_inventory_contract_draft.sql`: **재고 쓰기 계약 초안**으로, 로그인/세션/판매자 회원 테이블은 포함하지 않음.

이 브랜치에는 운영 인증 서버·세션 저장소·판매자 회원 테이블·실제 HTTP 엔드포인트가 확인되지 않았다. 따라서 정적 HTML에 운영 API URL만 넣어서는 인증된 조회가 작동하지 않는다.

## 권장 연결 순서

1. 운영자가 서버 런타임(FastAPI 등), 호스팅 및 신뢰된 데이터베이스를 선택하고 승인한다.
2. 사용자·판매자·활성 회원관계 스키마를 별도 검토한다. 기존 재고 SQL 초안을 운영 DB에 즉시 적용하지 않는다.
3. 서버가 로그인 성공 시 난수 세션 ID를 발급하고, 서버 저장소에는 해시된 세션 식별자·만료·폐기 상태를 보관한다. 쿠키 이름은 `seller_session`이며 `Secure; HttpOnly; SameSite=Lax; Path=/` 속성을 사용한다. HTTPS를 강제한다.
4. `GET /api/seller/dashboard`는 브라우저 쿠키를 서버에서 읽고, 검증된 사용자 ID로 회원관계를 조회한 다음, **SQL WHERE seller_id = ?** 범위로만 재고를 조회한다. 응답에 `Cache-Control: no-store`를 설정한다.
5. 서버는 `handle_cookie_authenticated_dashboard`를 호출하고 반환한 상태 코드·본문을 HTTP 응답으로 변환한다. 클라이언트가 제출한 role/user_id를 인증 근거로 사용하지 않는다.
6. 프런트엔드는 인증 서버가 준비되기 전까지 **현재 데모만 노출**한다. 운영 API 호출을 자동으로 시작하거나 실제 재고로 전환하지 않는다.

## 배포 시 필수 보안 게이트

- Netlify와 API가 서로 다른 사이트라면 쿠키·CORS·CSRF 정책을 먼저 별도 설계한다. `SameSite=Lax`가 모든 교차 사이트 호출에 동작한다고 가정하지 않는다.
- 중복 `seller_session` 쿠키, 무효·만료·폐기 세션, 타 판매자 소속 재고, 비활성 회원, POST/PUT/PATCH/DELETE는 거부한다.
- 인증 실패·내부 오류에는 DB 주소·토큰·예외 메시지를 노출하지 않는다. 오류 상태 코드는 서비스 라우팅 정책에 맞게 최종 검토한다.
- 실제 HTTP 통합 테스트, 재고 테넌트 격리 테스트, 세션 고정·재사용 공격 테스트, 배포 환경 검증을 완료한 뒤 승인받는다.
- GitHub Actions 실행 문제가 해결되지 않은 동안 **PR #5 병합·운영 배포 금지**.

## 현재 범위

본 문서는 실행 코드나 운영 리소스를 만들지 않는다. 실서비스 인증 및 API 호스팅 선택 전까지 읽기 전용 계약을 유지한다.
