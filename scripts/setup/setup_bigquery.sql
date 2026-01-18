-- ============================================================================
-- 네이버 웹툰 주간 차트 수집 파이프라인 - BigQuery 스키마 설정
-- ============================================================================
-- 
-- 이 스크립트는 BigQuery 데이터셋과 테이블을 생성합니다.
-- 
-- 실행 방법:
--   1. 데이터셋 생성: bq mk --dataset --location=asia-northeast3 PROJECT_ID:naver_webtoon
--   2. 테이블 생성: bq query --use_legacy_sql=false < 이 파일
--   3. 또는 BigQuery 콘솔에서 직접 실행
--
-- ============================================================================

-- 데이터셋 생성 (수동 실행 필요)
-- bq mk --dataset --location=asia-northeast3 PROJECT_ID:naver_webtoon

-- ============================================================================
-- 1. dim_webtoon 테이블 (웹툰 마스터 테이블)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `naver-webtoon-collector.naver_webtoon.dim_webtoon` (
  webtoon_id STRING NOT NULL,
  title STRING NOT NULL,
  author STRING,
  genre STRING,
  tags ARRAY<STRING>,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
CLUSTER BY webtoon_id
OPTIONS(
  description="웹툰 기본 정보 마스터 테이블. webtoon_id는 고유해야 함."
);

-- ============================================================================
-- 2. fact_weekly_chart 테이블 (주간 차트 히스토리)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `naver-webtoon-collector.naver_webtoon.fact_weekly_chart` (
  chart_date DATE NOT NULL,
  webtoon_id STRING NOT NULL,
  rank INTEGER NOT NULL,
  collected_at TIMESTAMP NOT NULL,
  weekday STRING,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,
  week INTEGER NOT NULL,
  view_count INTEGER
)
PARTITION BY chart_date
CLUSTER BY webtoon_id, chart_date
OPTIONS(
  description="주간 차트 순위 히스토리. chart_date 기준으로 파티션됨. (chart_date, webtoon_id) 조합은 고유해야 함."
);

-- ============================================================================
-- 3. fact_webtoon_stats 테이블 (웹툰 상세 정보 히스토리)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `naver-webtoon-collector.naver_webtoon.fact_webtoon_stats` (
  webtoon_id STRING NOT NULL,
  collected_at TIMESTAMP NOT NULL,
  favorite_count INTEGER,
  favorite_count_source STRING,
  finished BOOLEAN,
  rest BOOLEAN,
  total_episode_count INTEGER,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,
  week INTEGER NOT NULL
)
PARTITION BY DATE(collected_at)
CLUSTER BY webtoon_id, collected_at
OPTIONS(
  description="웹툰 상세 정보 히스토리. collected_at 기준으로 파티션됨."
);

-- ============================================================================
-- 인덱스 및 제약 조건 (참고용)
-- ============================================================================
-- BigQuery는 PRIMARY KEY를 명시적으로 지원하지 않지만,
-- CLUSTER BY를 사용하여 쿼리 성능을 최적화합니다.
--
-- Foreign Key 관계는 애플리케이션 레벨에서 검증합니다.
-- 
-- 중복 방지:
-- - dim_webtoon: webtoon_id는 고유해야 함 (애플리케이션 레벨에서 보장)
-- - fact_weekly_chart: (chart_date, webtoon_id) 조합은 고유해야 함
-- - fact_webtoon_stats: (webtoon_id, collected_at) 조합은 고유해야 함
--
-- ============================================================================

