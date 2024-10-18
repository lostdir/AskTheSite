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

def extract_keywords(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        return keywords['content'] if keywords else None
    except Exception as e:
        st.error(f"Error extracting keywords: {e}")
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
    keywords = extract_keywords(url) or "No keywords found"
    main_content = extract_main_content(url) or "No content found"

    prompt_text = (
        f"Title: {title}\n"
        f"Meta Description: {meta_description}\n"
        f"Keywords: {keywords}\n"
        f"Main Content: {main_content[:1000]}..."
    )

    messages_to_invoke = [
        ("system", "You are a helpful assistant that analyzes website data and only return a short summary of the website contents , dont return seo,recomendations ect."),
        ("human", prompt_text),
    ]

    response = chat.invoke(messages_to_invoke)
    return extract_analysis_text(response)

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
    response = llm.invoke(messages_to_invoke,max_tokens=12000)
    return extract_analysis_text(response)

# Apply custom CSS
st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f5;
        color: #333333;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput>div>input {
        background-color: #ffffff;
        border: 2px solid #cccccc;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        transition: all 0s;  /* Prevents fading or sliding animations */
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.2s ease-in-out;  /* Smooth hover effect */
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSpinner {
        color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Streamlit UI
st.title("🌐 Chat With Site")
st.write("Analyze any website and get insights or ask questions about the content.")

# Layout with columns for better arrangement
col1, col2 = st.columns(2)

# URL Input in first column
with col1:
    url = st.text_input("Enter the URL you want to analyze:", placeholder="https://example.com")

    if url:
        if st.button("Analyze"):
            with st.spinner("Analyzing the URL..."):
                analysis = analyze_url(url)
                st.subheader("🔍 Analysis Result")
                st.write(analysis)

# Question Input in the second column
with col2:
    question = st.text_input("Your question:", placeholder="Ask about the website content")
    if question and url:
        if st.button("Ask"):
            with st.spinner("Generating response..."):
                main_content = extract_main_content(url)
                if main_content:
                    answer = ask_question_to_llm(question, main_content)
                    st.subheader("💬 Question Response")
                    st.write(answer)
                else:
                    st.warning("Unable to extract content from the provided URL.")
