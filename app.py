import streamlit as st
from scorer import score_hook

st.title("Hook Scorer")
st.caption("Score direct-response video ad hooks on four dimensions.")

hook = st.text_area("Paste a hook", height=100)

if st.button("Score") and hook:
  with st.spinner("Scoring..."):
    r = score_hook(hook)
  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Attention", r["attention"])
  c2.metric("Clarity", r["clarity"])
  c3.metric("Specificity", r["specificity"])
  c4.metric("Tension", r["tension"])
  st.metric("Overall", r["overall"])
  st.write(r["reasoning"])
  st.success(f"Stronger version: {r['strongest_rewrite']}")