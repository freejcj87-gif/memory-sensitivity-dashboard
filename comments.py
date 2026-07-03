# -*- coding: utf-8 -*-
"""댓글판. comments.json에 저장 (Streamlit Cloud에서는 재시작 시 초기화될 수 있음)."""
import datetime
import json
import pathlib

import streamlit as st

COMMENTS_FILE = pathlib.Path(__file__).parent / "comments.json"


def load_comments() -> list:
    if COMMENTS_FILE.exists():
        try:
            return json.loads(COMMENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_comments(items: list) -> None:
    COMMENTS_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")


def render():
    st.markdown("#### 댓글")

    with st.form("comment_form", clear_on_submit=True):
        name = st.text_input("이름", max_chars=20, placeholder="이름 또는 별명")
        text = st.text_area("내용", max_chars=500, placeholder="메시지를 입력하세요")
        submitted = st.form_submit_button("등록")

    if submitted:
        if not text.strip():
            st.warning("내용을 입력해 주세요.")
        else:
            items = load_comments()
            items.insert(0, {
                "name": (name or "익명").strip(),
                "text": text.strip(),
                "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            save_comments(items)
            st.success("등록 완료.")

    items = load_comments()
    if not items:
        st.caption("아직 댓글이 없습니다.")
    for c in items[:50]:
        st.markdown(f"**{c['name']}** · {c['ts']}\n\n{c['text']}")
        st.divider()

    st.caption("Streamlit Cloud 파일시스템은 휘발성이라 앱 재시작 시 댓글이 초기화될 수 있습니다. "
               "영구 보관이 필요하면 Google Sheets 연동으로 확장 가능.")
