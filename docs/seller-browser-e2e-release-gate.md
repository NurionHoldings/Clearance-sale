# 판매자 시연 브라우저 E2E 릴리스 게이트

상태: CI 설정 추가 / 실행 미확인 / 운영 승인 아님

## 변경 범위
- 워크플로: `.github/workflows/seller-dashboard-browser-required.yml`
- 시험: `tests/test_seller_dashboard_browser_e2e.py`
- 독립형 읽기 전용 화면: `seller-dashboard-demo.html`
- Chromium 설치 후 3개 테스트 실행, 실패·건너뜀·시험 수 부족은 모두 비정상 종료.
- 외부 API, 운영 DB, 계정 인증, 실제 결제는 사용하지 않음.

## 현재 차단 사항
- GitHub Actions는 계정 결제 오류로 실행 불가 상태로 보고됨.
- 따라서 CI 통과, 브라우저 성공, 배포 준비 완료로 판정하지 않는다.
- 별도 GitHub branch protection 또는 ruleset에서 아래 상태 검사를 **Required**로 지정하기 전에는 CI 워크플로 추가만으로 병합이 기술적으로 차단된다고 보장할 수 없다.

## 운영자 조치
1. GitHub 조직 `NurionHoldings`의 Billing 설정에서 결제 오류 확인·해결.
2. PR #5의 신규 `Seller dashboard browser required / Chromium browser E2E (no skips)` 상태 검사 실행 여부 확인.
3. GitHub 저장소 Settings → Rules → Rulesets 또는 Branches의 main 보호 규칙에서 위 검사를 필수 상태 검사로 지정.
4. 기존 Codex offline safety checks, Cloud development verification 역시 필수 검사로 유지.
5. 모든 필수 검사 Green, 변경 검토 및 명시적 운영자 승인 이후에만 병합·배포를 별도 결정.

## 검증 실패 처리
- Playwright/Chromium 설치 실패: 실패
- 브라우저 시험 건너뜀: 실패
- 3개 미만 실행: 실패
- 어느 하나의 테스트 실패: 실패
- Actions 시작 불가/검사 미생성: 검증 미완료. 병합 금지.

이 문서는 설정 방법과 수용 기준만 정의한다. 실제 GitHub 보호 규칙 변경 또는 운영 배포를 수행하지 않았다.
