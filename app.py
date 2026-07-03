# -*- coding: utf-8 -*-
"""메모리 2사(삼성전자·SK하이닉스) 이익·밸류에이션 민감도 대시보드.

가격(범용 DRAM/NAND/HBM) x HBM 점유율 x PER 배수 → 영업이익/EPS/주가.
기초 추정치: 삼성전자 = 한국투자증권 2Q26 Preview(2026-07-02),
SK하이닉스 = 컨센서스 + 자체 조립(마진 가정). 투자 자문 아님.
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import comments
import market

st.set_page_config(page_title="메모리 2사 이익·밸류에이션 민감도", page_icon="📊", layout="wide")

TRILLION = "조"

SAMSUNG = dict(
    key="ss",
    name="삼성전자 (005930)",
    price0=286_000,
    price_date="2026-07-02",
    per0=6.7,
    tax=0.762,
    breakdown=[
        ("범용 DRAM", 249, "#1D9E75"),
        ("NAND", 87, "#5DCAA5"),
        ("HBM", 15, "#7F77DD"),
        ("세트·기타", 11, "#B4B2A9"),
    ],
    breakdown_note="적자: 시스템LSI+파운드리 −1.1조 · 가전 −0.4조 | DRAM 내 HBM 비중: 매출 7.1% → 2027년 20.7%",
    y26=dict(
        op=361.1, ni=282.2, eps=42_630,
        segs=[
            dict(label="범용 DRAM", rev=325.2, price=1.82, unit="$/Gb",
                 guide="2024~25 평균 ≈ $0.40 (−78% 지점)"),
            dict(label="NAND", rev=137.3, price=0.30, unit="$/GB",
                 guide="2024~25 평균 ≈ $0.08 (−72% 지점)"),
            dict(label="HBM", rev=25.0, price=1.49, unit="$/Gb",
                 guide="2025 평균 ≈ $1.36 (−9% 지점)"),
        ],
    ),
    y27=dict(
        op=544.3, ni=405.8, eps=61_068,
        segs=[
            dict(label="범용 DRAM", rev=396.9, price=2.26, unit="$/Gb",
                 guide="2026 평균 $1.82 (−19%) · 24~25 평균 (−82%)"),
            dict(label="NAND", rev=207.9, price=0.39, unit="$/GB",
                 guide="2026 평균 $0.30 (−23%) · 24~25 평균 (−78%)"),
        ],
        hbm=dict(mkt=225.0, margin=0.60, share0=46, price=2.88,
                 guide_share="현재 17% · HBM4 배분 전망 ~25% · 리포트 함의 46%"),
    ),
    source="한국투자증권 2Q26 Preview (2026-07-02) 표7 · HBM/범용 분리는 HBM 마진 60% 가정",
    target_note=(
        "**한국투자증권 목표주가 590,000원의 가정치** (2026-07-02): "
        "범용 DRAM $2.26/Gb (2026 대비 +24%) · NAND $0.39 (+33%) · HBM $2.88/Gb (+93%) · "
        "HBM 점유율 ~46% (2027년 업계 1위) · 2027 EPS 61,068원. "
        "원 리포트는 12MF BPS 118,062원 x 목표 PBR 5.0배로 산출 — 이 모델의 PER 프레임으로는 "
        "2027 EPS x **9.7배**에 해당. 아래에서 시나리오를 적용해 확인해 보세요."
    ),
    targets=[
        dict(house="한국투자증권", tp=590_000, date="2026-07-02",
             note="12MF BPS x PBR 5.0배, HBM 2027 업계 1위 가정"),
        dict(house="신한투자증권", tp=550_000, date="2026-06",
             note="목표가 상향 (6월 보도 기준)"),
        dict(house="현대차증권", tp=440_000, date="2026-06",
             note="6월 보도 기준"),
    ],
)

HYNIX = dict(
    key="hx",
    name="SK하이닉스 (000660)",
    price0=2_187_000,
    price_date="2026-07-02",
    per0=6.9,
    tax=0.79,
    breakdown=[
        ("범용 DRAM", 158, "#1D9E75"),
        ("HBM", 57, "#7F77DD"),
        ("NAND", 41, "#5DCAA5"),
        ("기타", 6, "#B4B2A9"),
    ],
    breakdown_note="순수 메모리 회사 — HBM이 이익의 22% (삼성 4%) | DRAM 내 HBM 매출 비중 30%",
    y26=dict(
        op=262.0, ni=225.0, eps=317_800,
        segs=[
            dict(label="범용 DRAM", rev=186.0, price=None, unit="",
                 guide="2024~25 평균가 ≈ −75% 지점 (근사)"),
            dict(label="NAND", rev=68.0, price=None, unit="",
                 guide="2024~25 평균가 ≈ −70% 지점 (근사)"),
            dict(label="HBM", rev=79.0, price=None, unit="",
                 guide="2025 평균 ≈ −10% 지점 (근사)"),
        ],
    ),
    y27=dict(
        op=395.0, ni=334.0, eps=471_600,
        segs=[],
        hbm=dict(mkt=225.0, margin=0.65, share0=55, price=None,
                 guide_share="삼성 대역전 시 40% · 완만 하락 55% · 현재 유지 62%"),
    ),
    source="컨센서스(노무라·KB 등) + 자체 조립: 마진 가정 범용 85% · HBM 72% · NAND 60%",
    target_note=None,
    targets=[
        dict(house="노무라", tp=5_000_000, date="2026-06-25", note="해외 최상단"),
        dict(house="한화투자증권", tp=4_300_000, date="2026-06-22", note="국내 최상단"),
        dict(house="미래에셋증권", tp=4_200_000, date="2026-06-25", note=""),
        dict(house="SK증권", tp=4_000_000, date="2026-06-01", note=""),
        dict(house="KB증권", tp=3_800_000, date="2026-06-24", note=""),
        dict(house="한국투자증권", tp=3_800_000, date="2026-05-20", note=""),
        dict(house="골드만삭스", tp=3_500_000, date="2026-05-31", note=""),
        dict(house="NH투자증권", tp=3_200_000, date="2026-06-08", note=""),
        dict(house="JP모건", tp=3_000_000, date="2026-05-18", note="외국계 하단"),
    ],
)


def _seed(key, val):
    """위젯 생성 전에 session_state 기본값을 심어 value 인자와의 충돌을 피한다."""
    if key not in st.session_state:
        st.session_state[key] = val


def _apply_target_scenario(cfg, implied_per):
    """가격 슬라이더를 리포트 기준(0%)으로, PER을 목표가 함의 배수로 설정."""
    st.session_state[f"{cfg['key']}_per"] = float(min(12.0, max(3.0, round(implied_per, 1))))
    for year_key, year_cfg in (("26", cfg["y26"]), ("27", cfg["y27"])):
        for seg in year_cfg["segs"]:
            st.session_state[f"{cfg['key']}{year_key}_{seg['label']}"] = 0
    st.session_state[f"{cfg['key']}_share"] = cfg["y27"]["hbm"]["share0"]
    if cfg["y27"]["hbm"].get("price"):
        st.session_state[f"{cfg['key']}_hbmp"] = 0


def render_targets(cfg):
    eps27 = cfg["y27"]["eps"]
    st.markdown("#### 증권사 목표주가 & 시나리오")
    if cfg.get("target_note"):
        st.info(cfg["target_note"])
    rows = []
    for t in cfg["targets"]:
        rows.append({
            "증권사": t["house"],
            "목표주가": f"{t['tp']:,}원",
            "기준일": t["date"],
            "현 주가 대비": f"{(t['tp'] / cfg['price0'] - 1) * 100:+.0f}%",
            "함의 PER(27E)": round(t["tp"] / eps27, 1),
            "비고": t["note"],
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption("함의 PER = 목표주가 ÷ 이 모델의 2027년 EPS. 증권사 자체 추정 EPS와 다를 수 있어 근사치.")

    labels = [f"{t['house']} {t['tp']:,}원" for t in cfg["targets"]]
    c1, c2 = st.columns([3, 1])
    pick = c1.selectbox("목표가 시나리오 선택", labels, key=f"{cfg['key']}_tpsel",
                        label_visibility="collapsed")
    idx = labels.index(pick)
    implied = cfg["targets"][idx]["tp"] / eps27
    c2.button("슬라이더에 적용", key=f"{cfg['key']}_tpbtn",
              on_click=_apply_target_scenario, args=(cfg, implied))
    st.caption("적용 시: 가격 슬라이더 = 리포트 기준(0%) · HBM 점유율 = 기본 가정 · PER = 함의 배수 "
               "→ 아래 2027년 주가 카드가 해당 목표주가 부근으로 이동합니다.")


def won(n: float) -> str:
    return f"{n:,.0f}원"


def breakdown_chart(cfg):
    fig = go.Figure()
    total = sum(v for _, v, _ in cfg["breakdown"])
    for label, value, color in cfg["breakdown"]:
        fig.add_trace(go.Bar(
            y=[""], x=[value], name=f"{label} {value}조", orientation="h",
            marker=dict(color=color),
            text=f"{label}<br>{value}조 ({value / total * 100:.0f}%)",
            textposition="inside", insidetextanchor="middle",
            hovertemplate=f"{label}: {value}조원 ({value / total * 100:.0f}%)<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack", height=110, showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig


def price_sliders(cfg, year_cfg, prefix):
    deltas = {}
    for seg in year_cfg["segs"]:
        label = seg["label"]
        base_txt = f" (기준 {seg['unit']} {seg['price']})" if seg.get("price") else ""
        _seed(f"{prefix}_{label}", 0)
        d = st.slider(
            f"{label} 가격 변화율{base_txt}", -85, 30, step=1,
            key=f"{prefix}_{label}", format="%d%%", help=seg["guide"],
        )
        implied = ""
        if seg.get("price"):
            implied = f" → {seg['unit'].split('/')[0]}{seg['price'] * (1 + d / 100):.2f}"
        impact = seg["rev"] * d / 100
        st.caption(f"눈금: {seg['guide']}{implied} · 이익 영향 {impact:+.0f}조")
        deltas[label] = impact
    return sum(deltas.values())


def metrics_row(op_base, ni_base, eps_base, d_op, tax, per, price0, label):
    op = op_base + d_op
    ni = ni_base + d_op * tax
    eps = max(0.0, eps_base * ni / ni_base)
    px = max(0.0, round(eps * per / 1000) * 1000)
    c1, c2, c3 = st.columns(3)
    op_pct = (op / op_base - 1) * 100
    c1.metric(f"{label} 영업이익", f"{op:,.0f}조",
              delta=f"{op_pct:+.0f}% vs 기준" if abs(op_pct) >= 0.5 else "기준 그대로",
              delta_color="normal" if abs(op_pct) >= 0.5 else "off")
    c2.metric(f"{label} EPS", won(eps))
    px_pct = (px / price0 - 1) * 100
    c3.metric(f"PER {per:.1f}배 시 주가", won(px), delta=f"{px_pct:+.0f}% vs 기준주가")


def render_company(cfg):
    st.subheader(cfg["name"])
    st.caption(f"기준주가 {won(cfg['price0'])} ({cfg['price_date']} 종가) · {cfg['source']}")

    st.markdown(f"**2026년 예상 영업이익 {cfg['y26']['op']:,.0f}조원 — 사업부별 분해**")
    st.plotly_chart(breakdown_chart(cfg), width="stretch",
                    config={"displayModeBar": False}, key=f"{cfg['key']}_chart")
    st.caption(cfg["breakdown_note"])

    render_targets(cfg)

    _seed(f"{cfg['key']}_per", cfg["per0"])
    per = st.slider(
        "적용 PER 배수 (4배 = 사이클 바닥 · 10배 = 과거 평균권)",
        3.0, 12.0, step=0.1, key=f"{cfg['key']}_per",
    )

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("#### 2026년 가격 민감도")
        d26 = price_sliders(cfg, cfg["y26"], f"{cfg['key']}26")
        metrics_row(cfg["y26"]["op"], cfg["y26"]["ni"], cfg["y26"]["eps"],
                    d26, cfg["tax"], per, cfg["price0"], "2026")

    with right:
        st.markdown("#### 2027년 민감도")
        d27 = 0.0
        if cfg["y27"]["segs"]:
            d27 += price_sliders(cfg, cfg["y27"], f"{cfg['key']}27")
        hbm = cfg["y27"]["hbm"]
        _seed(f"{cfg['key']}_share", hbm["share0"])
        share = st.slider(
            "HBM 점유율 (2027년, 시장 약 225조원 가정)", 10, 70, step=1,
            key=f"{cfg['key']}_share", format="%d%%", help=hbm["guide_share"],
        )
        hbm_price_d = 0
        if hbm.get("price"):
            _seed(f"{cfg['key']}_hbmp", 0)
            hbm_price_d = st.slider(
                f"HBM 가격 변화율 (기준 $/Gb {hbm['price']})", -85, 30, step=1,
                key=f"{cfg['key']}_hbmp", format="%d%%",
            )
        base_hbm_op = hbm["mkt"] * hbm["share0"] / 100 * hbm["margin"]
        new_hbm_op = hbm["mkt"] * share / 100 * (hbm["margin"] + hbm_price_d / 100)
        d27 += new_hbm_op - base_hbm_op
        st.caption(f"눈금: {hbm['guide_share']} · HBM 매출 "
                   f"{hbm['mkt'] * share / 100 * (1 + hbm_price_d / 100):,.0f}조")
        metrics_row(cfg["y27"]["op"], cfg["y27"]["ni"], cfg["y27"]["eps"],
                    d27, cfg["tax"], per, cfg["price0"], "2027")


st.title("메모리 2사 이익·밸류에이션 민감도")
st.caption(
    "투자 자문이 아니며 정보 제공·교육 목적입니다. 모든 수치는 증권사 추정치 기반 점추정으로 "
    "일 단위로 변동합니다. 가격 변동분은 전액 이익 반영(증분원가 ≈ 0) 근사이며, "
    "극단 하락 구간에서는 하방을 과장합니다."
)

tab_ss, tab_hx, tab_mkt, tab_peer, tab_cmt, tab_doc = st.tabs(
    ["삼성전자", "SK하이닉스", "시장 모니터", "피어그룹", "댓글", "모델 설명"])
with tab_ss:
    render_company(SAMSUNG)
with tab_hx:
    render_company(HYNIX)
with tab_mkt:
    market.render_spot_section()
with tab_peer:
    market.render_peer_section()
with tab_cmt:
    comments.render()
with tab_doc:
    st.markdown(
        """
### 모델 구조
- **영업이익 변화 = Σ (세그먼트 매출 x 가격 변화율)** — 메모리는 고정비 산업이라 가격 변동분이 거의 전액 이익으로 반영된다는 근사.
- **순이익 변화 = 영업이익 변화 x (1 − 유효세율)** — 삼성전자 24%, SK하이닉스 21% 적용.
- **주가 = EPS x 적용 PER** — PER 슬라이더로 멀티플 리레이팅/디레이팅을 분리해 볼 수 있음.
- **2027 HBM**: 시장 약 225조원($160B, TrendForce 수요 +68% 기반 추산) x 점유율 x 마진.

### 기초 추정치 출처
| | 삼성전자 | SK하이닉스 |
|---|---|---|
| 2026F 영업이익 | 361조 (한국투자증권) | 262조 (컨센서스) |
| 2026F EPS | 42,630원 | 317,800원 (순이익 225조) |
| 2027F 영업이익 | 544조 | 395조 (순이익 334조 역산) |
| 세그먼트 분해 | 리포트 표7 + HBM 마진 60% 가정 | 자체 조립 (마진 가정 명기) |

### 주의
- SK하이닉스 사업부 분해는 회사 비공시 → 범용/HBM 분리(158조/57조)는 ±20% 오차 가능.
- 과거 평균가 눈금은 삼성 블렌디드 ASP 시계열 기반. 시장 스팟가와 레벨이 다름 — 변화율로만 해석.
- HBM 가격은 연간 장기계약 비중이 높아 범용처럼 일 단위로 출렁이지 않음.
        """
    )
