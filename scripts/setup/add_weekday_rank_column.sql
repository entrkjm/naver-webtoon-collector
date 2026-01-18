-- ============================================================================
-- weekday_rank 컬럼 추가 및 기존 데이터 마이그레이션
-- ============================================================================
-- 
-- 문제: 현재 rank는 통합 순위(global rank)로 저장되어 수집 시점의 요일에 따라 편향됨
-- 해결: 요일별 순위(weekday_rank) 컬럼 추가
--
-- 실행 방법:
--   bq query --use_legacy_sql=false < 이 파일
--
-- ============================================================================

-- 1. weekday_rank 컬럼 추가
ALTER TABLE `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
ADD COLUMN IF NOT EXISTS weekday_rank INTEGER;

-- 2. 컬럼 설명 추가
-- 주의: 기존 데이터가 없으므로 마이그레이션 불필요
ALTER TABLE `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
ALTER COLUMN weekday_rank SET OPTIONS(description="요일별 순위 (각 요일 내에서 1, 2, 3, ... 순위)");

-- ============================================================================
-- 검증 쿼리
-- ============================================================================
-- 다음 쿼리로 마이그레이션 결과 확인:
--
-- SELECT 
--   chart_date,
--   weekday,
--   COUNT(*) AS total,
--   COUNT(weekday_rank) AS with_weekday_rank,
--   MIN(weekday_rank) AS min_rank,
--   MAX(weekday_rank) AS max_rank
-- FROM `naver-webtoon-collector.naver_webtoon.fact_weekly_chart`
-- GROUP BY chart_date, weekday
-- ORDER BY chart_date DESC, weekday
-- ============================================================================
