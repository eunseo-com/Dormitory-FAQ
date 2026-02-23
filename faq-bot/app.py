import os
import pandas as pd
import streamlit as st
from rapidfuzz import fuzz

st.set_page_config(page_title="Mini FAQ Bot", page_icon="💬")

st.title("💬 기숙사 FAQ 챗봇")
st.caption("😊 무엇을 도와드릴까요? 편하게 질문해 주세요.")

@st.cache_data
def load_faq(path="faq.csv"):
    # 절대 경로 변환
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    # 디버깅: 파일이 없으면 현재 폴더의 파일 목록을 화면에 보여줌
    if not os.path.exists(path):
        st.error(f"❌ 파일을 찾을 수 없습니다: {path}")
        st.write("📂 현재 폴더에 있는 파일들:")
        st.code(os.listdir(base_dir))
        st.stop()

    df = pd.read_csv(path).fillna("")
    # 검색용 텍스트(초급 핵심)
    df["search_text"] = (
        df["question"].astype(str) + " " +
        df.get("keywords", "").astype(str) + " " +
        df.get("category", "").astype(str)
    ).str.lower()
    return df

df = load_faq()

def score(query: str, text: str) -> int:
    # partial_ratio: 포함/유사 표현에 강함(초급에 잘 맞음)
    return fuzz.partial_ratio(query.lower(), text)

query = st.text_input("질문을 입력하세요", placeholder="예: 환불 규정이 어떻게 되나요?")

if query:
    df2 = df.copy()
    df2["score"] = df2["search_text"].apply(lambda t: score(query, t))
    top = df2.sort_values("score", ascending=False).head(3)

    best = top.iloc[0]
    confidence = int(best["score"])

    st.subheader("✅ 추천 답변")
    st.write(best["answer"] if best["answer"] else "(답변이 비어 있습니다. CSV를 확인해주세요.)")

    if best.get("link", ""):
        st.markdown(f"관련 링크: {best['link']}")

    st.caption(f"유사도 점수: {confidence}/100")

    st.subheader("🔎 관련 FAQ Top3")
    for i, row in enumerate(top.itertuples(index=False), start=1):
        with st.expander(f"{i}) {row.question}  (점수 {row.score})"):
            st.write(row.answer)
            if getattr(row, "link", ""):
                st.markdown(f"링크: {row.link}")
            st.write(f"카테고리: {getattr(row, 'category', '')}")

    st.divider()
    st.subheader("이 답이 도움이 되었나요?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 예, 해결됐어요"):
            st.success("좋습니다! 다음에도 질문 주세요.")
    with col2:
        if st.button("👎 아니오, 해결 안 됐어요"):
            st.warning("아래 중 하나를 선택해 주세요.")

            categories = sorted([c for c in df["category"].unique().tolist() if c])
            picked = st.selectbox("카테고리 선택", ["선택"] + categories)

            st.write("필요하면 문의로 바로 연결하세요:")
            st.markdown("- 이메일: info@creativeflow.co.kr")

            if picked != "선택":
                st.info(f"선택 카테고리: {picked} — 이 범주의 FAQ를 더 추가하면 정확도가 올라갑니다.")
