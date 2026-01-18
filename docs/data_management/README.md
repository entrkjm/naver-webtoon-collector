# Data Management 가이드

데이터 관리, 검증, 품질 관리 가이드입니다.

---

## 📚 주요 가이드

### 데이터 검증

- **[data_validation_guide.md](./data_validation_guide.md)** - 데이터 검증 절차 및 방법
  - 데이터 품질 검증 방법
  - 검증 스크립트 사용법
  - 문제 해결 방법

- **[data_collection_failure_policy.md](./data_collection_failure_policy.md)** - 데이터 수집 실패 정책 및 처리 방법
  - 실패 감지 기준
  - 알림 전송 조건
  - 대응 방법

- **[threshold_guide.md](./threshold_guide.md)** - 데이터 검증 임계값 설정 가이드
  - 임계값 설정 방법
  - 추천 값
  - 조정 가이드

---

## 🚀 빠른 시작

### 데이터 검증 실행

```bash
# 데이터 품질 검증
python scripts/data_management/validate_data_quality.py

# 데이터 무결성 검증
python scripts/data_management/verify_data.py
```

### 임계값 설정

```bash
# 환경 변수로 설정
export MIN_EXPECTED_RECORDS=500

# Cloud Function 재배포
cd functions/data_validation_function
./deploy.sh
```

---

## 🔗 관련 문서

- [Reference Guide](../reference/bigquery_tables_guide.md) - BigQuery 테이블 가이드
- [Monitoring Guide](../monitoring/monitoring_guide.md) - 모니터링 가이드

