# -*- coding: utf-8 -*-
"""시장 데이터: TrendForce 스팟 가격 스크래핑 + 피어그룹 비교(yfinance)."""
import io

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
}

SPOT_URLS = {
    "DRAM": "https://www.trendforce.com/price/dram/dram_spot",
    "NAND": "https://www.trendforce.com/price/flash/flash_spot",
}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_spot(kind: str):
    """TrendForce 스팟 가격 테이블. 실패 시 None (호출부에서 링크 안내)."""
    try:
        r = requests.get(SPOT_URLS[kind], headers=HEADERS, timeout=15)
        r.raise_for_status()
        tables = pd.read_html(io.StringIO(r.text))
    except Exception:
        return None
    best = None
    for t in tables:
        cols = " ".join(str(c) for c in t.columns)
        if "Session" in cols or "Item" in cols:
            if best is None or len(t) > len(best):
                best = t
    return best if best is not None else (tables[0] if tables else None)


# fwd_eps: 12개월 선행 EPS(원) — 한국 종목은 야후 컨센서스가 부실해 국내 추정치로 계산
# (삼성전자 = 한투 2026/27F 평균 51,849원, SK하이닉스 = 컨센 2026/27F 평균 394,700원, 2026-07 기준)
PEER_GROUPS = {
    "DRAM": [
        dict(ticker="005930.KS", name="삼성전자", cur="KRW", fwd_eps=51_849, share=38.6),
        dict(ticker="000660.KS", name="SK하이닉스", cur="KRW", fwd_eps=394_700, share=28.8),
        dict(ticker="MU", name="Micron", cur="USD", fwd_eps=None, share=22.4),
        dict(ticker="2408.TW", name="Nanya Tech", cur="TWD", fwd_eps=None, share=2.5),
    ],
    "NAND": [
        dict(ticker="005930.KS", name="삼성전자", cur="KRW", fwd_eps=51_849, share=29.0),
        dict(ticker="000660.KS", name="SK하이닉스(+솔리다임)", cur="KRW", fwd_eps=394_700, share=22.0),
        dict(ticker="285A.T", name="Kioxia", cur="JPY", fwd_eps=None, share=16.0),
        dict(ticker="MU", name="Micron", cur="USD", fwd_eps=None, share=13.0),
        dict(ticker="SNDK", name="SanDisk", cur="USD", fwd_eps=None, share=11.0),
    ],
}

SHARE_NOTE = ("매출 점유율은 1Q26 보도 기준 근사치 (DRAM: Omdia/TrendForce, NAND: TrendForce/Counterpoint). "
              "Fwd PER: 한국 종목은 국내 추정 12MF EPS(2026-07 기준), 해외는 야후 컨센서스.")

FX_FALLBACK = {"USD": 1456.0, "JPY": 9.2, "TWD": 45.0, "KRW": 1.0}


@st.cache_data(ttl=900, show_spinner=False)
def fx_to_krw() -> dict:
    fx = dict(FX_FALLBACK)
    for cur, sym in {"USD": "KRW=X", "JPY": "JPYKRW=X", "TWD": "TWDKRW=X"}.items():
        try:
            v = yf.Ticker(sym).fast_info["last_price"]
            if v and v > 0:
                fx[cur] = float(v)
        except Exception:
            pass
    return fx


@st.cache_data(ttl=900, show_spinner=False)
def fetch_peers(group: str) -> pd.DataFrame:
    fx = fx_to_krw()
    rows = []
    for p in PEER_GROUPS[group]:
        price = mcap = fwd_pe = None
        tk = yf.Ticker(p["ticker"])
        try:
            fi = tk.fast_info
            price = float(fi["last_price"])
            mcap = float(fi["market_cap"])
        except Exception:
            pass
        if p["fwd_eps"] and price:
            fwd_pe = price / p["fwd_eps"]
        elif price:
            try:
                fwd_pe = tk.info.get("forwardPE")
            except Exception:
                fwd_pe = None
        mcap_krw = mcap * fx.get(p["cur"], 1.0) if mcap else None
        rows.append({
            "기업": p["name"],
            "티커": p["ticker"],
            "주가(현지통화)": f"{price:,.0f}" if price else "—",
            "시가총액(조원)": round(mcap_krw / 1e12, 0) if mcap_krw else None,
            "Fwd PER(배)": round(fwd_pe, 1) if fwd_pe else None,
            "매출 점유율(%)": p["share"],
        })
    return pd.DataFrame(rows)


def render_spot_section():
    st.markdown("#### DRAM·NAND 스팟 가격 (TrendForce)")
    st.caption("30분 캐시. 스팟가는 현물 소량 거래 가격으로, 고정거래가(계약가)·기업 블렌디드 ASP와 레벨이 다름 — 방향성 지표로만 사용.")
    c1, c2 = st.columns(2)
    for col, kind in ((c1, "DRAM"), (c2, "NAND")):
        with col:
            st.markdown(f"**{kind} Spot**")
            df = fetch_spot(kind)
            if df is None or df.empty:
                st.info(f"{kind} 스팟 테이블을 불러오지 못했습니다 (사이트 차단/구조 변경 가능). "
                        f"[TrendForce에서 직접 보기]({SPOT_URLS[kind]})")
            else:
                st.dataframe(df, width="stretch", height=320)
                st.caption(f"출처: [{SPOT_URLS[kind]}]({SPOT_URLS[kind]})")


def render_peer_section():
    st.markdown("#### 피어그룹 비교 — DRAM / NAND")
    st.caption(SHARE_NOTE)
    for group in ("DRAM", "NAND"):
        st.markdown(f"**{group} 피어**")
        try:
            df = fetch_peers(group)
            st.dataframe(
                df, width="stretch", hide_index=True,
                column_config={
                    "시가총액(조원)": st.column_config.NumberColumn(format="%.0f조"),
                    "Fwd PER(배)": st.column_config.NumberColumn(format="%.1f"),
                    "매출 점유율(%)": st.column_config.ProgressColumn(
                        format="%.1f%%", min_value=0, max_value=45),
                },
            )
        except Exception as e:
            st.warning(f"{group} 피어 데이터 조회 실패: {e}")
    st.caption("시세는 yfinance(야후) 지연 시세, 시가총액은 실시간 환율로 원화 환산 (15분 캐시).")
