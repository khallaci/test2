import os
import re
import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import fitz  # PyMuPDF
import docx
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential

# --- Load environment ---
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")

# --- Validate ---
for var, name in zip([OPENAI_ENDPOINT, OPENAI_KEY, DEPLOYMENT, EMBEDDING_MODEL, SEARCH_ENDPOINT, SEARCH_KEY, INDEX_NAME],
                     ["OPENAI_ENDPOINT","OPENAI_KEY","DEPLOYMENT","EMBEDDING_MODEL","SEARCH_ENDPOINT","SEARCH_KEY","INDEX_NAME"]):
    if not var:
        raise ValueError(f"{name} nuk duhet të jetë bosh")

# --- Initialize Azure OpenAI ---
client = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_KEY,
    api_version="2024-12-01-preview"
)

# --- Initialize SQLite database ---
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

def save_message(role, content):
    c.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def load_all_messages():
    c.execute("SELECT role, content FROM messages ORDER BY timestamp")
    return c.fetchall()

# --- Streamlit layout ---
st.set_page_config(page_title="Q&A Assistant", page_icon="📄", layout="wide")

with st.sidebar:
    st.image("https://tse1.mm.bing.net/th/id/OIP.4nJCKko7st2GecTJgL3V0wHaHY?w=170&h=180&c=7&r=0&o=7&pid=1.7&rm=3", width=80)
    st.title("📄 Q&A Assistant")
    st.write("Ky aplikacion përdor Azure Cognitive Search dhe Azure OpenAI për të dhënë përgjigje mbi dokumentet e Rregullores së Punës ose të ngarkuara.")

st.markdown("<h1 style='text-align:center; color:#228B22;'>Q&A Assistant over Documents</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Tabs ---
tabs = st.tabs(["💬 Pyetje & Përgjigje", "📂 Pyetje mbi Dokumentin e Ngarkuar", "📊 Statistikat"])

# ------------------- Tab 0: Chat Indexed Documents (RAG) -------------------
with tabs[0]:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "Ju jeni një asistent ndihmës për dokumentet e Rregullores së Punës."}
        ]

    user_input = st.text_input("Shkruani pyetjen tuaj këtu:", key="rag_input")
    if st.button("Dërgo", key="rag_btn") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_message("user", user_input)

        # --- RAG parameters ---
        rag_params = {
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": SEARCH_ENDPOINT,
                        "index_name": INDEX_NAME,
                        "authentication": {
                            "type": "api_key",
                            "key": SEARCH_KEY,
                        },
                        "query_type": "vector",
                        "embedding_dependency": {
                            "type": "deployment_name",
                            "deployment_name": EMBEDDING_MODEL,
                        },
                        
                    }
                }
            ]
        }

        try:
            response = client.chat.completions.create(
                model=DEPLOYMENT,
                messages=st.session_state.messages,
                extra_body=rag_params
            )
            answer = response.choices[0].message.content
            cleaned_answer = re.sub(r"\[doc\d+\]", "", answer).strip()
            st.session_state.messages.append({"role": "assistant", "content": cleaned_answer})
            save_message("assistant", cleaned_answer)
        except Exception as e:
            st.error(f"Gabim: {e}")

    # Display chat
    for msg in st.session_state.messages[1:]:
        if msg["role"] == "user":
            st.markdown(f"<div style='background-color:#DCF8C6;padding:8px;border-radius:8px;margin-bottom:4px'><b>Ju:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#F1F0F0;padding:8px;border-radius:8px;margin-bottom:4px'><b>Asistenti:</b> {msg['content']}</div>", unsafe_allow_html=True)

# ------------------- Tab 1: Chat Uploaded Document -------------------
if "uploaded_doc_text" not in st.session_state:
    st.session_state.uploaded_doc_text = ""

with tabs[1]:
    uploaded_file = st.file_uploader("Ngarko PDF ose DOCX", type=["pdf", "docx"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            st.session_state.uploaded_doc_text = "\n".join([page.get_text() for page in pdf])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            st.session_state.uploaded_doc_text = "\n".join([p.text for p in doc.paragraphs])

    doc_input = st.text_input("Pyetja mbi dokumentin e ngarkuar:", key="uploaded_doc_input")
    if st.button("Dërgo Pyetjen", key="uploaded_doc_btn") and doc_input and st.session_state.uploaded_doc_text:
        messages = [
            {"role": "system", "content": "Ju jeni një asistent që përgjigjet vetëm mbi dokumentin e ngarkuar."},
            {"role": "user", "content": f"Dokumenti:\n{st.session_state.uploaded_doc_text}\nPyetja: {doc_input}"}
        ]
        try:
            response = client.chat.completions.create(model=DEPLOYMENT, messages=messages)
            answer = response.choices[0].message.content
            st.markdown(f"<div style='background-color:#F1F0F0;padding:8px;border-radius:8px;margin-bottom:4px'><b>Asistenti:</b> {answer}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Gabim: {e}")

# ------------------- Tab 2: Statistics -------------------
with tabs[2]:
    st.subheader("📊 Statistikat")
    all_messages = load_all_messages()
    questions = [m[1] for m in all_messages if m[0] == "user"]
    answers = [m[1] for m in all_messages if m[0] == "assistant"]

    col1, col2 = st.columns(2)
    col1.metric("Numri i Pyetjeve", len(questions))
    col2.metric("Numri i Përgjigjeve", len(answers))

    st.write("### 5 Pyetjet më të shpeshta")
    if questions:
        questions_norm = [q.strip().capitalize() for q in questions]
        counter = pd.Series(questions_norm).value_counts().head(5)
        for i, (q, count) in enumerate(counter.items(), start=1):
            st.markdown(f"{i}. {q} ({count} herë)")

    st.write("### Fjalë më të shpeshta në pyetje")
    if questions:
        all_questions_text = " ".join(questions)
        wordcloud = WordCloud(width=400, height=200, background_color="white").generate(all_questions_text)
        plt.figure(figsize=(6, 3))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)
