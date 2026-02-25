# ETL Layer

외부 데이터를 수집/가공하여 내부 DB에 적재하는 배치 파이프라인입니다.

## 모듈

| 모듈 | 역할 |
|------|------|
| `poi_collector.py` | Google/Kakao Places API로 지역별 POI 수집 |
| `review_collector.py` | POI별 리뷰 수집 및 LLM 요약 |
| `embedding_builder.py` | POI 텍스트를 벡터 임베딩으로 변환 |
| `place_cache_updater.py` | Place 정보 주기적 캐시 갱신 |

## 실행

```bash
python -m etl.scripts.seed_sample_data
python -m etl.scripts.run_etl_pipeline --region "제주"
```
