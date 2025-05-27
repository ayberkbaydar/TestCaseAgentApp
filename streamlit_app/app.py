import streamlit as st
import sys
import os
import json

st.set_page_config(page_title="Testinel", layout="wide")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine import generate_test_cases
from parse import parse_test_cases

# 🔐 API Konfigürasyonu
st.sidebar.subheader("🔐 API Configuration")
provider = st.sidebar.selectbox("AI Provider", ["openrouter", "openai"])
api_key = st.sidebar.text_input("API Key", type="password")

if not api_key:
    st.warning("Please enter your API key in the sidebar.")
    st.stop()

# --- Başlık ---
st.title("🤖 AI Test Case Generator")

# --- Çıktı İçin Dil Seçimi ---
lang = st.radio(
    label="🌍 Select Output Language",
    options=["English", "Turkish"],
    index=0,
    horizontal=True
)

st.markdown("Select input method then enter test documentation or upload as `.json`.")

# --- Session State ---
def init_session():
    st.session_state.setdefault("input_method", "Manual Entry")
    st.session_state.setdefault("manual_inputs", {
        "domain": "",
        "product_name": "",
        "title": "",
        "content": "",
        "output": ""
    })
    st.session_state.setdefault("json_docs", [])
    st.session_state.setdefault("json_output", "")
    st.session_state.setdefault("json_filename", "")

init_session()

# --- Veri Giriş Yöntemi ---
input_method = st.radio("📥 Data Entry Method", ["Manual Entry", "Upload as JSON"], horizontal=True)

# === MANUAL ENTRY ===
if input_method == "Manual Entry":
    inputs = st.session_state.manual_inputs

    inputs["domain"] = st.text_input("Domain", value=inputs["domain"], placeholder="e.g. e-commerce, banking, telecom...")
    inputs["product_name"] = st.text_input("Product Name", value=inputs["product_name"], placeholder="e.g. Checkout Module")
    inputs["title"] = st.text_input("Feature/User Story", value=inputs["title"])
    inputs["content"] = st.text_area("Content", value=inputs["content"], height=300)

    if st.button("🧠 Generate Test Case "):
        if not inputs["content"].strip():
            st.error("❌ Content field cannot be empty.")
            st.stop()

        doc = {
            "title": inputs["title"] or "Untitled",
            "content": inputs["content"]
        }
        # print(f"📦 generate_test_cases input: {doc}, lang: {lang}, domain: {inputs['domain']}, product_name: {inputs['product_name']}",flush=True)
        result = generate_test_cases(
            doc,
            lang=lang,
            domain=inputs["domain"],
            product_name=inputs["product_name"],
            api_key=api_key,
            provider=provider
        )
        inputs["output"] = result
        st.success("✅ Test cases were generated!")

    if inputs["output"]:
        st.text_area("Test Case Outputs", inputs["output"], height=400)
        st.download_button("⬇️ Download as TXT", inputs["output"], file_name="test_cases.txt")
        # print(f"🧩 parse_test_cases input (manual): {inputs['output']}",flush=True)
        structured_cases = parse_test_cases(inputs["output"])
        json_export = json.dumps({
            "title": inputs["title"] or "Untitled",
            "test_cases": structured_cases
        }, indent=2, ensure_ascii=False)
        st.download_button("⬇️ Download as JSON", json_export, file_name="test_cases.json", mime="application/json")

# === JSON YÜKLE ===
elif input_method == "Upload as JSON":
    uploaded_file = st.file_uploader("Upload Documentation JSON File", type="json")

    if uploaded_file is not None:
        try:
            docs = json.load(uploaded_file)
            if isinstance(docs, dict):
                docs = [docs]
            st.session_state.json_docs = docs
            st.session_state.json_filename = uploaded_file.name
        except Exception as e:
            st.error(f"❌ JSON could not be loaded: {str(e)}")

    if st.session_state.json_filename:
        st.markdown(f"""
            <div style='
                background-color: #262730;
                padding: 0.5em 1em;
                border-radius: 0.5em;
                margin-top: 0.5em;
                display: inline-block;
                color: #4ade80;
                font-weight: 500;
            '>📄 {st.session_state.json_filename}</div>
        """, unsafe_allow_html=True)

    if st.session_state.json_docs:
        st.markdown("### 🧠 Generate test cases for all documents")

        if st.button("🧠 Generate All"):
            combined_result = ""
            for doc in st.session_state.json_docs:
                # print(f"📦 generate_test_cases input (json): {doc}, lang: {lang}", flush=True)
                result = generate_test_cases(
                    doc,
                    lang=lang,
                    domain="",
                    product_name="the product",
                    api_key=api_key,
                    provider=provider
                )
                combined_result += f"\n\n### {doc.get('title', 'Untitled')}\n{result.strip()}"
            st.session_state.json_output = combined_result
            st.success("✅ Test cases were generated for all documents!")

        if st.session_state.json_output:
            st.text_area("Test Case Outputs", st.session_state.json_output, height=400)
            st.download_button("⬇️ Download as TXT", st.session_state.json_output, file_name="json_test_cases.txt")
            # print(f"🧩 parse_test_cases input (json): {st.session_state.json_output}",flush=True)
            structured_cases = parse_test_cases(st.session_state.json_output)
            json_export = json.dumps({"test_cases": structured_cases}, indent=2, ensure_ascii=False)
            st.download_button("⬇️ Download as JSON", json_export, file_name="json_test_cases.json")
