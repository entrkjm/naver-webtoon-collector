# 데이터 검증 임계값 가이드

> **통합 가이드**: 임계값 설정 및 추천 가이드

---

## 📋 목차

1. [임계값 개요](#임계값-개요)
2. [임계값 설정](#임계값-설정)
3. [임계값 추천](#임계값-추천)
4. [임계값 조정](#임계값-조정)

---

## 임계값 개요

### MIN_EXPECTED_RECORDS란?

데이터 검증 함수에서 사용하는 최소 예상 레코드 수입니다. 이 값보다 적은 데이터가 수집되면 알림이 전송됩니다.

### 기본값

- **기본값**: `500`
- **환경 변수**: `MIN_EXPECTED_RECORDS`로 오버라이드 가능

---

## 임계값 설정

### 환경 변수로 설정

```bash
export MIN_EXPECTED_RECORDS=500
```

### Cloud Function 배포 시 설정

```bash
cd functions/data_validation_function
export MIN_EXPECTED_RECORDS=500
./deploy.sh
```

### deploy.sh에서 설정

`functions/data_validation_function/deploy.sh` 파일에서:

```bash
export MIN_EXPECTED_RECORDS="${MIN_EXPECTED_RECORDS:-500}"
```

---

## 임계값 추천

### 추천 값: 500

**이유:**
- 네이버 웹툰 주간 차트는 보통 700-800개 웹툰이 포함됨
- 정렬 타입별로 수집하므로 (popular, view) 약 1,400-1,600개 레코드 예상
- 500은 안전한 최소값 (약 30% 마진)

### 값 조정 가이드

#### 낮은 값 (300-400)
- **장점**: 더 민감하게 감지
- **단점**: 정상적인 변동에도 알림 가능

#### 높은 값 (600-700)
- **장점**: 확실한 문제만 감지
- **단점**: 실제 문제를 놓칠 수 있음

#### 권장 범위
- **최소**: 400
- **권장**: 500
- **최대**: 600

---

## 임계값 조정

### 현재 값 확인

```bash
# Cloud Function 환경 변수 확인
gcloud functions describe data-validation-function \
    --gen2 \
    --region=asia-northeast3 \
    --format="value(serviceConfig.environmentVariables.MIN_EXPECTED_RECORDS)"
```

### 값 변경

1. **환경 변수 설정**:
```bash
export MIN_EXPECTED_RECORDS=500
```

2. **Cloud Function 재배포**:
```bash
cd functions/data_validation_function
./deploy.sh
```

### 실제 데이터 확인 후 조정

```bash
# 최근 수집된 데이터 확인
bq query --use_legacy_sql=false "
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT webtoon_id) as unique_webtoons
FROM \`naver-webtoon-collector.naver_webtoon.fact_weekly_chart\`
WHERE chart_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
"
```

**조정 기준:**
- 실제 레코드 수의 30-40%를 최소값으로 설정
- 예: 실제 1,500개 → 최소값 500-600

---

## 📝 요약

### 기본 설정

- **MIN_EXPECTED_RECORDS**: `500`
- **설정 위치**: Cloud Function 환경 변수
- **오버라이드**: 환경 변수로 가능

### 추천 값

- **권장**: `500`
- **범위**: `400-600`
- **조정**: 실제 데이터 수집량에 따라 조정

---

## 🔗 관련 문서

- [Data Validation Guide](./data_validation_guide.md) - 데이터 검증 전체 가이드
- [Data Collection Failure Policy](./data_collection_failure_policy.md) - 실패 정책 상세

