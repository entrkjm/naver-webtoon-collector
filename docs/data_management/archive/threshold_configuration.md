# 임계값 설정 가이드

## 현재 설정

- **기본값**: 500개
- **환경 변수 오버라이드**: 가능

## 설정 방법

### 방법 1: 기본값 사용 (500개)

기본값을 그대로 사용하면 500개가 적용됩니다:

```bash
cd functions/data_validation_function
./deploy.sh
```

### 방법 2: 환경 변수로 변경

배포 시 환경 변수로 임계값을 변경할 수 있습니다:

```bash
# 더 높은 기준 (600개)
export MIN_EXPECTED_RECORDS=600
cd functions/data_validation_function
./deploy.sh

# 더 낮은 기준 (400개)
export MIN_EXPECTED_RECORDS=400
cd functions/data_validation_function
./deploy.sh
```

### 방법 3: 배포 후 환경 변수 업데이트

이미 배포된 함수의 환경 변수를 업데이트:

```bash
gcloud functions deploy data-validation-function \
  --gen2 \
  --region=asia-northeast3 \
  --update-env-vars MIN_EXPECTED_RECORDS=600
```

## 권장 임계값

- **500개** (기본값): 웹툰 수가 자연스럽게 줄어들어도 오탐 방지
- **600개**: 중간 정도의 부분 실패도 감지
- **400개**: 웹툰 수가 크게 줄어들어도 오탐 없음

## 현재 설정 확인

```bash
gcloud functions describe data-validation-function \
  --gen2 \
  --region=asia-northeast3 \
  --format="value(serviceConfig.environmentVariables.MIN_EXPECTED_RECORDS)"
```

