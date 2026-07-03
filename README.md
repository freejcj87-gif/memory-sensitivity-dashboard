# 메모리 2사 이익·밸류에이션 민감도 대시보드

삼성전자(005930)·SK하이닉스(000660)의 2026/2027년 예상 이익을 사업부(범용 DRAM / HBM / NAND)로 분해하고,
가격 변화율 x HBM 점유율 x PER 배수를 슬라이더로 조작해 영업이익 → EPS → 주가 영향을 즉시 계산하는 Streamlit 앱.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포 (share.streamlit.io)

1. https://share.streamlit.io → New app
2. Repository: `freejcj87-gif/memory-sensitivity-dashboard`, Branch: `main`, Main file: `app.py`
3. Deploy — secrets 불필요 (외부 API 없음)

## 기초 추정치

- 삼성전자: 한국투자증권 2Q26 Preview (2026-07-02, 채민숙·김연준) 표7
- SK하이닉스: 컨센서스(노무라·KB 등) + 자체 마진 가정으로 조립
- 기준주가: 2026-07-02 종가 (삼성 286,000원 / 하이닉스 2,187,000원)

> 투자 자문 아님. 정보 제공·교육 목적. 모든 수치는 점추정이며 일 단위로 변동.
