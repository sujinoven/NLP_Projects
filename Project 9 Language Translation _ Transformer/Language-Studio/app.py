"""Run with: python -m streamlit run app.py"""
import json
import streamlit as st
from engine import LANGUAGES, NllbBackend, TranslationError, translate_message
from protection import detect_items

st.set_page_config(page_title="Language Studio", page_icon="🌐", layout="wide")
st.markdown("""
<style>
.stApp {background: #f5f4ef;}
.block-container {max-width: 1160px; padding-top: 2.8rem;}
h1 {font-size: 3.2rem !important; letter-spacing: -0.055em; font-weight: 700 !important;}
h2,h3 {letter-spacing: -0.025em;}
.eyebrow {font-size: .76rem; letter-spacing: .17em; color: #087f73; font-weight: 700;}
.intro {color: #63716c; font-size: 1.06rem; max-width: 650px; margin-bottom: 1.8rem;}
.pill {display: inline-block; padding: 6px 13px; border: 1px solid #ccd9d1;
border-radius: 40px; font-size: .76rem; color: #42645a; margin: 0 6px 8px 0;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 18px;}
.empty-result {min-height: 245px; padding: 48px 20px; text-align: center;
border: 1px dashed #cbd7cf; border-radius: 14px; color: #667a71; background: #f7faf7;}
.empty-result b {display:block; font-size:1.3rem; margin-bottom:12px; color:#284f44;}
.stButton > button {border-radius: 9px;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_backend():
    return NllbBackend()


EXAMPLES = {
    "Password reset": "Please help me reset my password.",
    "Account error": "My account shows error E403. Please help!",
    "Urgent request": "This is urgent! My account is locked. Please help immediately!",
}


def choose_example(name):
    st.session_state.message = EXAMPLES[name]
    st.session_state.pop("result", None)


def clear_message():
    st.session_state.message = ""
    st.session_state.pop("result", None)


st.markdown('<div class="eyebrow">OVEN / NLP PROJECT</div>', unsafe_allow_html=True)
st.title("A little less lost in translation.")
st.markdown('<div class="intro">Translate support messages across five languages. Keep the names and error codes that matter.</div>', unsafe_allow_html=True)
st.markdown('<span class="pill">5 languages</span><span class="pill">Protected terms</span><span class="pill">Runs on your computer</span>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Language Studio")
    st.caption("Your Transformer translation workspace")
    st.divider()
    st.markdown("**Supported languages**")
    st.write("English · French · Spanish · Hindi · Tamil")
    st.divider()
    st.markdown("**Getting started**")
    st.caption("Choose the target language, paste a message, and translate. Select a source manually for short messages.")
    st.info("First translation downloads the pretrained model. CPU works; a compatible NVIDIA GPU is faster.")
    with st.expander("About this project"):
        st.write("Uses NLLB-200 distilled 600M. This version has not been fine-tuned.")
        st.caption("Educational prototype. The model uses a noncommercial license and is not released for production deployment.")
        st.link_button("Model details", "https://huggingface.co/facebook/nllb-200-distilled-600M")
        st.caption("Messages are processed locally. First-use model downloads require internet. No message history is written to disk by this app.")

left, right = st.columns([1, 1], gap="large")
with left:
    with st.container(border=True):
        st.subheader("Your message")
        lang_left, lang_right = st.columns(2)
        with lang_left:
            source = st.selectbox("From", ["Auto-detect", *LANGUAGES], key="source")
        with lang_right:
            target = st.selectbox("To", list(LANGUAGES), index=3, key="target")
        text = st.text_area("Message", key="message", height=190, max_chars=4000,
                            placeholder="Paste a customer support message here…", label_visibility="collapsed")
        st.caption(f"{len(text):,} / 4,000 characters")
        st.caption("Try an example")
        example_cols = st.columns(3)
        for column, name in zip(example_cols, EXAMPLES):
            column.button(name, on_click=choose_example, args=(name,), use_container_width=True)
        with st.expander("Translation options", expanded=True):
            st.markdown("**Automatic term protection**")
            st.caption("Likely product names, technical identifiers, links and email addresses are detected from your message. No term list is required.")
            detected_items = detect_items(text)
            if detected_items:
                for item in detected_items:
                    st.text(f"{item['text']} · {item['category']}")
            else:
                st.caption("No items detected yet.")
            sentence_mode = st.toggle("Translate each sentence separately", value=True, key="sentence_mode",
                                      help="May reduce omissions. Can lose context or split abbreviations; switch off to compare.")
        action, clear = st.columns([3, 1])
        submit = action.button("Translate message →", type="primary", use_container_width=True)
        clear.button("Clear", on_click=clear_message, use_container_width=True)

request_key = (text, source, target, sentence_mode, "automatic-protection-v1")
if submit:
    # Never leave a previous successful translation visible after a failed request.
    st.session_state.pop("result", None)
    try:
        with st.spinner("Preparing your translation. The first model download can take several minutes…"):
            result = translate_message(text, source, target, [], sentence_mode, get_backend())
        st.session_state.result = result.to_dict()
        st.session_state.result_key = request_key
    except TranslationError as error:
        st.error(str(error))
    except Exception as error:
        st.error("The model could not complete this request. Check your connection and available memory, then retry.")
        with st.expander("Troubleshooting details"):
            st.code(f"{type(error).__name__}: {error}", language=None)

with right:
    with st.container(border=True):
        st.subheader("Translation")
        result = st.session_state.get("result")
        if result and st.session_state.get("result_key") == request_key:
            st.caption(f"{result['source']} → {result['target']} · {result['status']}")
            st.text_area("Translated message", value=result["translation"], height=220, disabled=True)
            if result["protected_terms"]:
                st.caption("Preserved: " + ", ".join(result["protected_terms"]))
            downloads = st.columns(2)
            downloads[0].download_button("Download text", result["translation"],
                                         file_name="translation.txt", mime="text/plain", use_container_width=True)
            downloads[1].download_button("Download details", json.dumps(result, ensure_ascii=False, indent=2),
                                         file_name="translation-details.json", mime="application/json", use_container_width=True)
            with st.expander("Review notes"):
                for note in result["notes"]:
                    st.write("• " + note)
                if result["detection_score"] is not None:
                    st.caption(f"Detection score: {result['detection_score']:.3f} (not accuracy)")
                st.caption(f"{result['sentence_count']} sentence(s) · {result['elapsed_seconds']:.1f} seconds")
        else:
            st.markdown('<div class="empty-result"><b>Words, across borders.</b>Your translation will appear here.<br>Choose a language and send your first message.</div>', unsafe_allow_html=True)
            st.caption("Changed your input? Translate again to generate a matching result.")
        st.divider()
        st.caption("Review meaning, tone, and technical details before sharing. Mixed-script messages are currently blocked; Romanised language detection is limited.")

st.caption("Built with a Transformer encoder–decoder · No fine-tuning or formal benchmark claimed")
