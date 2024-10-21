import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Retrieve the API key from Streamlit secrets
try:
    api_key = st.secrets["general"]["GROQ_API_KEY"]  # Adjust according to your secrets setup
except KeyError as e:
    st.error(f"Error: {str(e)}")
    st.stop()  # Stop further execution if the API key is missing

# Initialize the LLM
llm = ChatGroq(
    api_key=api_key,
    model="llama-3.1-70b-versatile",
    temperature=1,
    max_tokens=7950,
    timeout=None,
    max_retries=2,
)
chat = ChatGroq(
    api_key=api_key,
    model="llama-3.1-8b-instant",
    temperature=1,
    max_tokens=8000,
    timeout=None,
    max_retries=2,
)


# Functions for data extraction
def extract_title(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else None
        return title
    except Exception as e:
        st.error(f"Error extracting title: {e}")
        return None

def extract_meta_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        return meta_description['content'] if meta_description else None
    except Exception as e:
        st.error(f"Error extracting meta description: {e}")
        return None

def extract_main_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_parts = []
        paragraphs = soup.find_all('p')
        content_parts.extend([para.get_text() for para in paragraphs])
        spans = soup.find_all('span')
        content_parts.extend([span.get_text() for span in spans])
        unordered_lists = soup.find_all('ul')
        for ul in unordered_lists:
            list_items = ul.find_all('li')
            content_parts.extend([li.get_text() for li in list_items])
        ordered_lists = soup.find_all('ol')
        for ol in ordered_lists:
            list_items = ol.find_all('li')
            content_parts.extend([li.get_text() for li in list_items])
        return ' '.join(content_parts).strip()
    except Exception as e:
        st.error(f"Error extracting main content: {e}")
        return None


def analyze_url(url):
    title = extract_title(url) or "No title found"
    meta_description = extract_meta_description(url) or "No meta description found"
    main_content = extract_main_content(url) or "No content found"

    prompt_text = (
        f"Title: {title}\n"
        f"Meta Description: {meta_description}\n"
        f"Main Content: {main_content[:1000]}..."
    )

    messages_to_invoke = [
        ("system", "You are a helpful assistant that analyzes website data and only return a short summary of the website contents, don't return SEO, recommendations, etc."),
        ("human", prompt_text),
    ]

    response = chat.invoke(messages_to_invoke)
    return extract_analysis_text(response), main_content

def extract_analysis_text(response):
    try:
        return response.content
    except Exception as e:
        st.error(f"Error extracting analysis text: {e}")
        return "Analysis could not be retrieved."

def ask_question_to_llm(question, main_content):
    truncated_content = main_content[:5000]
    prompt_text = f"Based on the following content, answer the question:\n\n{truncated_content}\n\nQuestion: {question}"
    messages_to_invoke = [
        ("system", "You are a helpful assistant."),
        ("human", prompt_text),
    ]
    response = llm.invoke(messages_to_invoke, max_tokens=8000)
    return extract_analysis_text(response)

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .p {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.markdown('<div class="title">🌐 Chat With Site</div>', unsafe_allow_html=True)
st.write('<p class="p">Analyze any website and get insights or ask questions about the content.</p>', unsafe_allow_html=True)
st.toast('Still in beta, some sites may not function perfectly.')
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for URL analysis
if url := st.chat_input("Enter the URL you want to analyze:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": url})

    # Analyze the URL and display results
    with st.chat_message("assistant"):
        st.write("Analyzing the URL, please wait...")
        analysis, main_content = analyze_url(url)
        st.session_state.messages.append({"role": "assistant", "content": analysis})
        st.markdown(analysis)

    # Store the main content for further questions
    st.session_state.main_content = main_content

# Input for user questions if analysis is available
if 'main_content' in st.session_state:
    if question := st.chat_input("Ask a question about the analyzed content:"):
        # Add user question to chat history
        st.session_state.messages.append({"role": "user", "content": question})

        # Display the user question
        with st.chat_message("user"):
            st.markdown(question)

        # Get the response from the LLM and display it
        with st.chat_message("assistant"):
            st.write("Thinking...")
            answer = ask_question_to_llm(question, st.session_state.main_content)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.markdown(answer)

