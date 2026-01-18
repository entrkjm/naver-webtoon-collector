# 비용 모니터링 가이드

이 문서는 네이버 웹툰 수집 파이프라인의 GCP 비용 모니터링 방법을 설명합니다.

## 목차

1. [Always Free 범위](#always-free-범위)
2. [비용 모니터링 방법](#비용-모니터링-방법)
3. [월별 비용 추적](#월별-비용-추적)
4. [비용 최적화 팁](#비용-최적화-팁)

---

## Always Free 범위

이 프로젝트는 GCP Always Free 범위 내에서 운영되도록 설계되었습니다.

### 주요 서비스별 Always Free 한도

#### 1. Cloud Storage (GCS)
- **저장**: 5GB/월
- **Class A 작업** (읽기, 쓰기): 5,000회/월
- **Class B 작업** (목록): 50,000회/월
- **네트워크 송신**: 1GB/월

**예상 사용량**:
- 주 1회 실행 × 2개 정렬 타입 = 주당 2개 JSON 파일
- 파일 크기: 약 300KB/파일
- 월간 저장: 약 2.4MB (매우 여유)
- 업로드 작업: 주당 2회 = 월 8회 (한도 내)

#### 2. BigQuery
- **저장**: 10GB/월
- **쿼리**: 1TB/월
- **스토리지**: 10GB/월

**예상 사용량**:
- `dim_webtoon`: 약 1,000개 레코드 × 500 bytes = 0.5MB
- `fact_weekly_chart`: 주당 1,500개 레코드 × 200 bytes = 0.3MB/주 = 1.2MB/월
- `fact_webtoon_stats`: 주당 1,000개 레코드 × 300 bytes = 0.3MB/주 = 1.2MB/월
- **총 예상 저장**: 약 3MB/월 (한도 내)

#### 3. Cloud Functions (Gen 2)
- **요청**: 200만 회/월
- **컴퓨팅 시간**: 400,000GB-초/월
- **네트워크 송신**: 1GB/월

**예상 사용량**:
- 주 1회 실행 = 월 4회
- 실행 시간: 약 10분 (600초) × 512MB = 307,200MB-초 = 0.3GB-초/실행
- 월간 컴퓨팅: 4회 × 0.3GB-초 = 1.2GB-초 (한도 내)

#### 4. Cloud Scheduler
- **작업**: 3개 무료
- **실행**: 무제한

**예상 사용량**:
- 현재 1개 작업 사용 (한도 내)

#### 5. Cloud Logging
- **로그 수집**: 50GB/월
- **로그 저장**: 30일 보관

**예상 사용량**:
- 주 1회 실행 × 약 100줄 로그 = 월 400줄
- 로그 크기: 약 10KB/실행 = 월 40KB (한도 내)

#### 6. Cloud Monitoring
- **메트릭 수집**: 무료 (제한 없음)
- **알림**: 무료 (제한 없음)

---

## 비용 모니터링 방법

### 1. Cloud Console에서 확인

#### 비용 대시보드
1. [GCP 비용 대시보드](https://console.cloud.google.com/billing?project=naver-webtoon-collector) 접속
2. "비용 분석" 메뉴 선택
3. 프로젝트별, 서비스별 비용 확인

#### 사용량 대시보드
1. [GCP 사용량 대시보드](https://console.cloud.google.com/billing/usage?project=naver-webtoon-collector) 접속
2. 서비스별 사용량 확인:
   - Cloud Storage: 저장 용량, 작업 수
   - BigQuery: 저장 용량, 쿼리 용량
   - Cloud Functions: 요청 수, 컴퓨팅 시간
   - Cloud Scheduler: 작업 수, 실행 수

### 2. gcloud CLI로 확인

#### BigQuery 사용량 확인
```bash
# BigQuery 저장 용량 확인
bq query --use_legacy_sql=false --format=prettyjson "
SELECT 
  table_schema,
  table_name,
  ROUND(SUM(size_bytes) / 1024 / 1024, 2) AS size_mb
FROM \`naver-webtoon-collector.naver_webtoon.__TABLES__\`
GROUP BY table_schema, table_name
ORDER BY size_mb DESC
"

# BigQuery 쿼리 사용량 확인 (최근 30일)
bq query --use_legacy_sql=false --format=prettyjson "
SELECT 
  DATE(creation_time) AS date,
  COUNT(*) AS query_count,
  SUM(total_bytes_processed) / 1024 / 1024 / 1024 AS total_gb
FROM \`region-asia-northeast3.INFORMATION_SCHEMA.JOBS_BY_PROJECT\`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY date
ORDER BY date DESC
"
```

#### Cloud Storage 사용량 확인
```bash
# GCS 버킷 크기 확인
gsutil du -sh gs://naver-webtoon-raw

# GCS 버킷 파일 수 확인
gsutil ls -l gs://naver-webtoon-raw/** | wc -l
```

#### Cloud Functions 사용량 확인
```bash
# Cloud Functions 실행 횟수 확인 (최근 30일)
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=pipeline_function AND timestamp>=\"$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --format="value(timestamp)" \
  --limit=10000 | wc -l
```

### 3. 비용 알림 설정

#### 예산 및 알림 설정
1. [GCP 예산 및 알림](https://console.cloud.google.com/billing/budgets?project=naver-webtoon-collector) 접속
2. "예산 만들기" 클릭
3. 예산 설정:
   - 예산 금액: $0 (Always Free 범위 내)
   - 알림 임계값: 50%, 90%, 100%
   - 알림 채널: 이메일

#### 비용 알림 정책 생성
```bash
# 예산 생성 (예시)
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Webtoon Pipeline Budget" \
  --budget-amount=0USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## 월별 비용 추적

### 1. 비용 추적 스크립트

`scripts/check_cost_usage.sh` 스크립트를 사용하여 월별 사용량을 확인할 수 있습니다.

```bash
# 월별 사용량 확인
./scripts/check_cost_usage.sh
```

### 2. 비용 리포트 생성

매월 초에 다음 명령어로 전월 사용량을 확인합니다:

```bash
# 전월 사용량 리포트
./scripts/generate_cost_report.sh --month=2025-11
```

### 3. Always Free 범위 초과 확인

다음 스크립트로 Always Free 범위를 초과했는지 확인합니다:

```bash
# Always Free 범위 확인
./scripts/check_free_tier_usage.sh
```

---

## 비용 최적화 팁

### 1. BigQuery 최적화
- 파티션 및 클러스터링 활용 (이미 적용됨)
- 불필요한 쿼리 최소화
- 결과 캐싱 활용

### 2. Cloud Storage 최적화
- 오래된 데이터 아카이빙 (필요시)
- 중복 파일 제거
- 압축 활용 (JSON은 이미 압축됨)

### 3. Cloud Functions 최적화
- 불필요한 실행 방지
- 타임아웃 적절히 설정 (현재 3600초)
- 메모리 사용량 최적화 (현재 512MB)

### 4. 로깅 최적화
- 불필요한 로그 제거
- 로그 레벨 적절히 설정
- 로그 보존 기간 조정 (기본 30일)

---

## 비용 모니터링 체크리스트

매월 다음 항목을 확인하세요:

- [ ] BigQuery 저장 용량 < 10GB
- [ ] BigQuery 쿼리 < 1TB
- [ ] GCS 저장 용량 < 5GB
- [ ] GCS Class A 작업 < 5,000회
- [ ] Cloud Functions 요청 < 200만 회
- [ ] Cloud Functions 컴퓨팅 < 400,000GB-초
- [ ] 총 비용 = $0 (Always Free 범위 내)

---

## 참고 자료

- [GCP Always Free](https://cloud.google.com/free/docs/free-cloud-features)
- [비용 관리 가이드](https://cloud.google.com/billing/docs/how-to/budgets)
- [사용량 모니터링](https://cloud.google.com/monitoring/api/v3)

