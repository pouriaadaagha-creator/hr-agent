import os
import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="دستیار منابع انسانی",
    page_icon="🏢",
    layout="centered",
)

# On Railway both services run on the same container → localhost works.
# Override via API_URL env var if you ever split them into separate services.
API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

# Persian sample questions paired with their English equivalents sent to the API
SAMPLE_QUESTIONS = [
    ("چند روز مرخصی سالانه داریم؟",           "How many annual leave days do employees have?"),
    ("ساعات کاری شرکت چیست؟",                  "What are the working hours?"),
    ("نرخ اضافه‌کاری آخر هفته چقدر است؟",      "What is the overtime pay rate on weekends?"),
    ("بیمه درمانی از چه زمانی فعال می‌شود؟",   "When does health insurance activate?"),
    ("آیا اعضای خانواده تحت پوشش بیمه‌اند؟",  "Are dependents covered under the insurance plan?"),
    ("سیاست دورکاری چگونه است؟",               "How does the remote work policy work?"),
    ("دوره آزمایشی چند ماه است؟",              "What is the probation period for new employees?"),
    ("روز اول کاری چه باید انجام دهم؟",        "What happens on the first day of work?"),
    ("چند روز مرخصی استعلاجی داریم؟",          "How many sick leave days are allowed per year?"),
    ("مرخصی ازدواج چند روز است؟",              "How many days of marriage leave do employees get?"),
]

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Page background */
    .stApp { background-color: #f0f2f6; }

    /* Header card */
    .hr-header {
        background: linear-gradient(135deg, #1e3c78 0%, #2a5298 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: white;
        text-align: center;
    }
    .hr-header h1 { font-size: 2rem; margin: 0; font-weight: 700; }
    .hr-header .subtitle-en { margin: 6px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .hr-header .subtitle-fa {
        margin: 4px 0 0;
        opacity: 0.85;
        font-size: 0.95rem;
        direction: rtl;
        font-family: 'Tahoma', 'Arial', sans-serif;
    }

    /* Source badge */
    .source-badge {
        display: inline-block;
        background: #e8f0fe;
        color: #1e3c78;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px 3px 0 0;
    }

    /* Sample question pills — RTL for Persian */
    div[data-testid="stButton"] > button {
        border-radius: 20px;
        border: 1.5px solid #2a5298;
        color: #2a5298;
        background: white;
        font-size: 0.88rem;
        padding: 6px 16px;
        transition: all 0.2s;
        direction: rtl;
        font-family: 'Tahoma', 'Arial', sans-serif;
        width: 100%;
        text-align: right;
    }
    div[data-testid="stButton"] > button:hover {
        background: #2a5298;
        color: white;
    }

    /* Chat input */
    div[data-testid="stChatInput"] { background: white; border-radius: 12px; }

    /* RTL user messages */
    .rtl-msg {
        direction: rtl;
        text-align: right;
        font-family: 'Tahoma', 'Arial', sans-serif;
        font-size: 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hr-header">
    <h1>🏢 دستیار منابع انسانی</h1>
    <p class="subtitle-fa">سوالات خود را درباره قوانین شرکت، مرخصی، بیمه و بیشتر بپرسید</p>
    <p class="subtitle-en">HR Assistant — powered by AI</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None   # (persian_label, english_query)

# ---------------------------------------------------------------------------
# Sample questions (Persian labels, English queries sent to LLM)
# ---------------------------------------------------------------------------

with st.expander("💡 سوالات نمونه — برای پرسیدن کلیک کنید", expanded=len(st.session_state.messages) == 0):
    cols = st.columns(2)
    for i, (persian, english) in enumerate(SAMPLE_QUESTIONS):
        if cols[i % 2].button(persian, key=f"sample_{i}"):
            st.session_state.pending_question = (persian, english)

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🏢"):
        if msg["role"] == "user":
            st.markdown(
                f'<div class="rtl-msg">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(msg["content"])
            if msg.get("sources"):
                source_html = " ".join(
                    f'<span class="source-badge">📄 {s}</span>'
                    for s in msg["sources"]
                )
                st.markdown(f"**منبع:** {source_html}", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Handle input — typed (English) or sample click (Persian display / English query)
# ---------------------------------------------------------------------------

typed = st.chat_input("سوال خود را بنویسید یا از نمونه‌ها انتخاب کنید...")
pending = st.session_state.pending_question

if pending:
    st.session_state.pending_question = None
    display_text, query_text = pending
else:
    display_text = typed
    query_text = typed

if query_text:
    # Show user bubble with the Persian label (or whatever they typed)
    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(
            f'<div class="rtl-msg">{display_text}</div>',
            unsafe_allow_html=True,
        )

    # Call FastAPI — always send the English query for best retrieval accuracy
    with st.chat_message("assistant", avatar="🏢"):
        with st.spinner("در حال جستجو در اسناد منابع انسانی..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"question": query_text},
                    timeout=30,
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "پاسخی دریافت نشد.")
                    sources = data.get("sources", [])
                else:
                    answer = f"خطای سرور ({response.status_code}). لطفاً مطمئن شوید API در حال اجراست."
                    sources = []
            except requests.exceptions.ConnectionError:
                answer = (
                    "اتصال به سرور برقرار نشد.\n\n"
                    "لطفاً مطمئن شوید دستور زیر در ترمینال اجرا شده است:\n\n"
                    "```\nuvicorn app:app --reload\n```"
                )
                sources = []
            except requests.exceptions.Timeout:
                answer = "درخواست با تاخیر مواجه شد. لطفاً دوباره تلاش کنید."
                sources = []

        st.markdown(answer)
        if sources:
            source_html = " ".join(
                f'<span class="source-badge">📄 {s}</span>'
                for s in sources
            )
            st.markdown(f"**منبع:** {source_html}", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ وضعیت سیستم")

    try:
        health = requests.get("http://localhost:8000/health", timeout=3)
        if health.status_code == 200:
            st.success("API: آنلاین ✅")
        else:
            st.error("API: خطا ❌")
    except Exception:
        st.error("API: آفلاین ❌")
        st.caption("`uvicorn app:app --reload`")

    st.divider()
    st.markdown("### 🗂️ اسناد منابع انسانی")
    st.caption("📄 employee_handbook.pdf")
    st.caption("📄 leave_policy.pdf")
    st.caption("📄 insurance_policy.pdf")
    st.caption("📄 onboarding_policy.pdf")

    st.divider()
    if st.button("🗑️ پاک کردن چت", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        "<div style='text-align:center; color:#999; font-size:0.75rem;'>"
        "Powered by OpenRouter + LangChain + ChromaDB"
        "</div>",
        unsafe_allow_html=True,
    )
