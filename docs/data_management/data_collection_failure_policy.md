# 데이터 수집 실패 감지 정책 상세 설명

이 문서는 "데이터 수집 실패 (예상보다 적거나 없음)" 케이스에 대한 정책을 상세히 설명합니다.

## 개요

데이터 검증 Cloud Function은 주기적으로 BigQuery의 데이터를 확인하여 다음 세 가지 검증을 수행합니다:

1. **fact_weekly_chart 테이블 검증**
2. **fact_webtoon_stats 테이블 검증**
3. **최근 수집 시간 검증**

---

## 1. fact_weekly_chart 테이블 검증

### 검증 목적
주간 차트 데이터가 정상적으로 수집되었는지 확인합니다.

### 검증 기준

#### ✅ 통과 조건
- 해당 날짜(`chart_date`)에 **최소 700개 이상**의 레코드가 존재
- 실제 수집된 웹툰 수는 보통 739개 정도이므로, 700개는 여유를 둔 기준

#### ❌ 실패 조건

**케이스 1: 데이터가 전혀 없는 경우**
```
fact_weekly_chart: 2025-12-28 데이터가 없습니다.
```
- **원인 예시**:
  - 파이프라인이 실행되지 않음
  - API 엔드포인트 변경으로 데이터 수집 실패
  - BigQuery 업로드 실패
  - 날짜 파라미터 오류

**케이스 2: 예상보다 적은 데이터가 있는 경우**
```
fact_weekly_chart: 예상 레코드 수(700)보다 적습니다. 실제: 150개
```
- **원인 예시**:
  - API 응답이 부분적으로만 성공 (일부 웹툰만 수집됨)
  - 네트워크 오류로 중간에 중단
  - 파싱 오류로 일부 데이터 손실
  - Rate limiting으로 인한 부분 수집

### 검증 쿼리
```sql
SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT webtoon_id) AS unique_webtoons
FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
WHERE chart_date = '2025-12-28'
```

### 임계값 설정
- **기본값**: `MIN_EXPECTED_RECORDS = 700`
- **설정 방법**: 환경 변수로 변경 가능
  ```bash
  export MIN_EXPECTED_RECORDS=650  # 더 낮은 기준
  export MIN_EXPECTED_RECORDS=750  # 더 높은 기준
  ```

### 실제 데이터 기준
- **정상 수집 시**: 약 772개 레코드 (popular + view 정렬 타입)
- **최소 기준**: 700개 (약 90% 수준)
- **경고 기준**: 700개 미만

---

## 2. fact_webtoon_stats 테이블 검증

### 검증 목적
웹툰 상세 정보(관심 수, 에피소드 수 등)가 정상적으로 수집되었는지 확인합니다.

### 검증 기준

#### ✅ 통과 조건
- 해당 날짜(`DATE(collected_at)`)에 **최소 700개 이상**의 레코드가 존재
- 실제 수집된 웹툰 수는 보통 739개 정도

#### ❌ 실패 조건

**케이스 1: 데이터가 전혀 없는 경우**
```
fact_webtoon_stats: 2025-12-28 데이터가 없습니다.
```
- **원인 예시**:
  - 웹툰 상세 정보 수집 로직이 실행되지 않음
  - API 엔드포인트 변경으로 상세 정보 수집 실패
  - BigQuery 업로드 실패
  - 타임아웃으로 인한 중단

**케이스 2: 예상보다 적은 데이터가 있는 경우**
```
fact_webtoon_stats: 예상 레코드 수(700)보다 적습니다. 실제: 300개
```
- **원인 예시**:
  - Rate limiting으로 인한 부분 수집
  - 일부 웹툰의 상세 정보 API 호출 실패
  - 배치 저장 중 오류로 일부 데이터만 저장
  - 타임아웃으로 인한 중간 중단

### 검증 쿼리
```sql
SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT webtoon_id) AS unique_webtoons,
    MAX(collected_at) AS last_collected
FROM `naver-webtoon-collector.naver_webtoon.fact_webtoon_stats`
WHERE DATE(collected_at) = '2025-12-28'
```

### 임계값 설정
- **기본값**: `MIN_EXPECTED_RECORDS = 700`
- **fact_weekly_chart와 동일한 기준 사용**

### 실제 데이터 기준
- **정상 수집 시**: 약 744개 레코드 (739개 고유 웹툰 + 중복 가능)
- **최소 기준**: 700개 (약 94% 수준)
- **경고 기준**: 700개 미만

---

## 3. 최근 수집 시간 검증

### 검증 목적
파이프라인이 최근에 실행되었는지 확인합니다. (장기간 미실행 감지)

### 검증 기준

#### ✅ 통과 조건
- **최근 48시간 이내**에 데이터가 수집됨
- 즉, 마지막 수집 시간이 현재 시각으로부터 48시간 이내

#### ❌ 실패 조건

**케이스 1: 최근 2일 이내 데이터가 전혀 없는 경우**
```
최근 2일 이내 데이터 수집 기록이 없습니다.
```
- **원인 예시**:
  - Cloud Scheduler가 실행되지 않음
  - 파이프라인이 2일 이상 실행되지 않음
  - 스케줄러 설정 오류

**케이스 2: 마지막 수집 시간이 48시간 이상 지난 경우**
```
최근 수집 시간: 72.5시간 전 (마지막 수집: 2025-12-26 10:00:00)
```
- **원인 예시**:
  - 주간 스케줄러가 실행되지 않음
  - 파이프라인 실행은 되었지만 데이터 저장 실패
  - 스케줄러 시간대 설정 오류

### 검증 쿼리
```sql
SELECT 
    MAX(collected_at) AS last_collected
FROM `naver-webtoon-collector.naver_webtoon.fact_webtoon_stats`
WHERE DATE(collected_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)
```

### 임계값 설정
- **기본값**: 48시간
- **설정 위치**: 코드 내 하드코딩 (`hours_ago < 48`)
- **변경 필요 시**: 코드 수정 필요

### 실제 운영 기준
- **정상 실행**: 매주 월요일 오전 9시 (KST)
- **최대 허용 지연**: 48시간 (2일)
- **경고 기준**: 48시간 이상 지연

---

## 검증 실행 시점

### 자동 검증
- **스케줄**: 매주 월요일 오전 10시 (KST) - 파이프라인 실행 1시간 후
- **목적**: 파이프라인 실행 후 데이터가 정상적으로 저장되었는지 확인

### 수동 검증
```bash
# 특정 날짜 검증
curl -X POST "https://data-validation-function-xxx.run.app" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-12-28"}'

# 오늘 날짜 검증 (기본)
curl -X POST "https://data-validation-function-xxx.run.app" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 알림 동작 방식

### 알림 전송 조건
다음 중 **하나라도 실패**하면 알림이 전송됩니다:

1. `fact_weekly_chart` 검증 실패
2. `fact_webtoon_stats` 검증 실패
3. 최근 수집 시간 검증 실패

### 알림 메시지 예시

#### 예시 1: 데이터 없음
```
제목: 파이프라인 데이터 수집 실패 - 2025-12-28

내용:
날짜: 2025-12-28

오류:
- fact_weekly_chart: 2025-12-28 데이터가 없습니다.
- fact_webtoon_stats: 2025-12-28 데이터가 없습니다.
- 최근 2일 이내 데이터 수집 기록이 없습니다.

상세:
{
  "date": "2025-12-28",
  "all_passed": false,
  "checks": {
    "fact_weekly_chart": {
      "total_records": 0,
      "unique_webtoons": 0,
      "passed": false
    },
    "fact_webtoon_stats": {
      "total_records": 0,
      "unique_webtoons": 0,
      "passed": false
    },
    "recent_collection": {
      "last_collected": null,
      "hours_ago": null,
      "passed": false
    }
  }
}
```

#### 예시 2: 데이터 부족
```
제목: 파이프라인 데이터 수집 실패 - 2025-12-28

내용:
날짜: 2025-12-28

오류:
- fact_weekly_chart: 예상 레코드 수(700)보다 적습니다. 실제: 150개
- fact_webtoon_stats: 예상 레코드 수(700)보다 적습니다. 실제: 150개

상세:
{
  "date": "2025-12-28",
  "all_passed": false,
  "checks": {
    "fact_weekly_chart": {
      "total_records": 150,
      "unique_webtoons": 150,
      "passed": false
    },
    "fact_webtoon_stats": {
      "total_records": 150,
      "unique_webtoons": 150,
      "passed": false
    },
    "recent_collection": {
      "last_collected": "2025-12-28 10:00:00",
      "hours_ago": 2.5,
      "passed": true
    }
  }
}
```

#### 예시 3: 장기간 미실행
```
제목: 파이프라인 데이터 수집 실패 - 2025-12-30

내용:
날짜: 2025-12-30

오류:
- 최근 수집 시간: 72.5시간 전 (마지막 수집: 2025-12-27 10:00:00)

상세:
{
  "date": "2025-12-30",
  "all_passed": false,
  "checks": {
    "fact_weekly_chart": {
      "total_records": 772,
      "unique_webtoons": 739,
      "passed": true
    },
    "fact_webtoon_stats": {
      "total_records": 744,
      "unique_webtoons": 739,
      "passed": true
    },
    "recent_collection": {
      "last_collected": "2025-12-27 10:00:00",
      "hours_ago": 72.5,
      "passed": false
    }
  }
}
```

---

## 임계값 조정 가이드

### MIN_EXPECTED_RECORDS 조정

현재 기본값은 700개입니다. 실제 운영 데이터를 기반으로 조정할 수 있습니다:

#### 조정 방법 1: 환경 변수로 설정
```bash
# 배포 시 환경 변수 설정
export MIN_EXPECTED_RECORDS=650
cd functions/data_validation_function
./deploy.sh
```

#### 조정 방법 2: 코드 수정
```python
# functions/data_validation_function/main.py
MIN_EXPECTED_RECORDS = int(os.environ.get("MIN_EXPECTED_RECORDS", "650"))  # 기본값 변경
```

#### 조정 기준
- **현재 수집량**: 약 739개 웹툰
- **권장 기준**: 
  - 보수적: 700개 (약 95%)
  - 일반적: 650개 (약 88%)
  - 관대함: 600개 (약 81%)

### 최근 수집 시간 임계값 조정

현재는 48시간으로 설정되어 있습니다. 코드에서 직접 수정해야 합니다:

```python
# functions/data_validation_function/main.py (155번째 줄)
"passed": hours_ago < 48  # 48시간을 원하는 값으로 변경 (예: 72시간)
```

---

## 검증 결과 해석

### 모든 검증 통과
```json
{
  "status": "success",
  "message": "데이터 수집 정상",
  "results": {
    "all_passed": true,
    "checks": {
      "fact_weekly_chart": {
        "total_records": 772,
        "unique_webtoons": 739,
        "passed": true
      },
      "fact_webtoon_stats": {
        "total_records": 744,
        "unique_webtoons": 739,
        "passed": true
      },
      "recent_collection": {
        "last_collected": "2025-12-28 10:00:00",
        "hours_ago": 2.5,
        "passed": true
      }
    }
  }
}
```

### 일부 검증 실패
- **HTTP 상태 코드**: 500
- **응답 본문**: 실패한 검증 항목과 상세 정보 포함
- **알림 전송**: 자동으로 이메일 알림 전송

---

## 문제 해결 가이드

### 데이터가 없는 경우

1. **파이프라인 실행 확인**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pipeline-function" --limit=50
   ```

2. **Cloud Scheduler 실행 확인**
   ```bash
   gcloud scheduler jobs describe naver-webtoon-weekly-collection --location=asia-northeast3
   ```

3. **BigQuery 업로드 확인**
   ```bash
   bq query --use_legacy_sql=false "
   SELECT COUNT(*) FROM \`naver-webtoon-collector.naver_webtoon.fact_weekly_chart\`
   WHERE chart_date = '2025-12-28'
   "
   ```

### 데이터가 적은 경우

1. **파이프라인 로그 확인**
   - 중간에 오류가 발생했는지 확인
   - Rate limiting으로 인한 중단 확인

2. **API 응답 확인**
   - GCS에 저장된 원본 데이터 확인
   - API 응답 구조 변경 여부 확인

3. **배치 저장 로그 확인**
   - 배치 저장이 정상적으로 완료되었는지 확인

---

## 참고

- 실제 수집 데이터 기준: 약 739개 웹툰
- 정상 수집 시 레코드 수:
  - `fact_weekly_chart`: 약 772개 (popular + view)
  - `fact_webtoon_stats`: 약 744개 (중복 포함 가능)
- 검증 실행 주기: 매주 월요일 오전 10시 (파이프라인 실행 1시간 후)

