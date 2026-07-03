# -*- coding: utf-8 -*-
"""댓글판 + 휴대폰 푸시 알림(ntfy.sh).

새 댓글이 등록되면 ntfy 토픽으로 푸시를 발송한다. 휴대폰에 ntfy 앱을 설치하고
같은 토픽을 구독하면 문자처럼 즉시 알림을 받는다 (무료, 전화번호 불필요).
진짜 SMS가 필요하면 st.secrets에 SOLAPI/Twilio 키를 넣고 notify()를 교체.
"""
import datetime
import json
import pathlib

import requests
import streamlit as st

COMMENTS_FILE = pathlib.Path(__file__).parent / "comments.json"
DEFAULT_TOPIC = "memdash-freejcj87-7743"


def _topic() -> str:
    try:
        return st.secrets.get("NTFY_TOPIC", DEFAULT_TOPIC)
    except Exception:
        return DEFAULT_TOPIC


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


def notify(name: str, text: str) -> bool:
    """ntfy.sh 푸시 발송. 성공 여부 반환."""
    try:
        r = requests.post(
            f"https://ntfy.sh/{_topic()}",
            data=f"{name}: {text}".encode("utf-8"),
            headers={"Title": "Memory dashboard new comment",
                     "Tags": "speech_balloon", "Priority": "default"},
            timeout=10,
        )
        return r.ok
    except Exception:
        return False


def render():
    st.markdown("#### 댓글")
    st.caption("댓글을 등록하면 지정된 ntfy 토픽으로 휴대폰 푸시 알림이 발송됩니다.")

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
            sent = notify(items[0]["name"], items[0]["text"])
            if sent:
                st.success("등록 완료 — 푸시 알림을 보냈습니다.")
            else:
                st.success("등록 완료 (푸시 발송은 실패 — 네트워크/토픽 확인).")

    items = load_comments()
    if not items:
        st.caption("아직 댓글이 없습니다.")
    for c in items[:50]:
        st.markdown(
            f"**{c['name']}** · {c['ts']}\n\n{c['text']}")
        st.divider()

    with st.expander("알림 수신 설정 방법"):
        st.markdown(f"""
1. 휴대폰에 **ntfy** 앱 설치 (App Store / Google Play, 무료)
2. 앱에서 **Subscribe to topic** → `{_topic()}` 입력
3. 이후 이 댓글창에 글이 올라올 때마다 휴대폰으로 즉시 푸시가 옵니다

- 토픽 이름을 바꾸려면 Streamlit Cloud의 **Secrets**에 `NTFY_TOPIC = "새이름"` 추가
- 토픽 이름을 아는 사람은 누구나 구독/발송 가능하니 추측 어려운 이름 권장
- **진짜 SMS(문자)**가 필요하면 유료 게이트웨이가 필요합니다: 솔라피(한국, 건당 ~9원) 또는
  Twilio 가입 후 API 키를 Secrets에 넣으면 `notify()`를 SMS 발송으로 교체해 드립니다
- 참고: Streamlit Cloud 파일시스템은 휘발성이라 댓글 자체는 앱 재시작 시 사라질 수 있습니다
  (푸시 알림은 이미 발송된 뒤라 영향 없음). 영구 보관이 필요하면 Google Sheets 연동 권장
""")
