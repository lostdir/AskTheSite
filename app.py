import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, render_template

# Load environment variables
load_dotenv()

# Check for the GROQ API key
if "GROQ_API_KEY" not in os.environ:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

# Initialize the LLM
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Render index.html

def extract_title(url):
    """Extract the title from the given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else None
        return title
    except Exception as e:
        print(f"Error extracting title: {e}")
        return None

def extract_meta_description(url):
    """Extract the meta description from the given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        return meta_description['content'] if meta_description else None
    except Exception as e:
        print(f"Error extracting meta description: {e}")
        return None

def extract_keywords(url):
    """Extract the keywords from the given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        return keywords['content'] if keywords else None
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return None

def extract_main_content(url):
    """Extract main content from the given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the main content from paragraphs, unordered lists, and ordered lists
        paragraphs = soup.find_all('p')
        unordered_lists = soup.find_all('ul')
        ordered_lists = soup.find_all('ol')

        # Collect text from paragraphs
        content = ' '.join([para.get_text() for para in paragraphs])

        # Collect text from unordered lists
        for ul in unordered_lists:
            list_items = ul.find_all('li')
            content += ' '.join([li.get_text() for li in list_items])

        # Collect text from ordered lists
        for ol in ordered_lists:
            list_items = ol.find_all('li')
            content += ' '.join([li.get_text() for li in list_items])

        return content.strip()  # Strip whitespace
    except Exception as e:
        print(f"Error extracting main content: {e}")
        return None

def analyze_url(url):
    """Analyze the URL to extract title, meta description, keywords, and main content."""
    title = extract_title(url)
    meta_description = extract_meta_description(url)
    keywords = extract_keywords(url)
    main_content = extract_main_content(url)  # Extract main content

    # Handle None cases
    title = title if title else "No title found"
    meta_description = meta_description if meta_description else "No meta description found"
    keywords = keywords if keywords else "No keywords found"
    main_content = main_content if main_content else "No content found"

    # Construct the prompt with formatted strings
    prompt_text = (
        f"Title: {title}\n"
        f"Meta Description: {meta_description}\n"
        f"Keywords: {keywords}\n"
        f"Main Content: {main_content[:1000]}..."  # Limit content length for processing
    )

    # Create the messages list for invocation
    messages_to_invoke = [
        ("system", "You are a helpful assistant that analyzes website data. Analyze the input data and generate a response."),
        ("human", prompt_text),
    ]

    # Generate a response based on the scraped information
    response = llm.invoke(messages_to_invoke)

    # Extract the content from the response
    analysis_text = extract_analysis_text(response)  # This function needs to be implemented

    return analysis_text

def extract_analysis_text(response):
    """Extract analysis text from the LLM response."""
    # Assuming response is an object with a 'content' attribute
    try:
        analysis = response.content
        return analysis
    except Exception as e:
        print(f"Error extracting analysis text: {e}")
        return "Analysis could not be retrieved."

def ask_question_to_llm(question, main_content):
    """Ask a question to the LLM based on the extracted main content."""
    prompt_text = f"Based on the following content, answer the question,analyze the content and study it to answer the question:\n\n{main_content}\n\nQuestion: {question}"

    messages_to_invoke = [
        ("system", "You are a helpful assistant that provides answers based on given information.when asked for recent or latest give information available from the most recent year. dont respond like : according to the text,respond as you know that and clean the response if needed "),
        ("human", prompt_text),
    ]

    # Generate a response based on the question and main content
    response = llm.invoke(messages_to_invoke)

    return extract_analysis_text(response)


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the index page and handle URL analysis and questions."""
    analysis = None  # Initialize analysis to None
    
    if request.method == "POST":
        url = request.form.get("url")
        
        # Validate URL
        if not url:
            return render_template("index.html", error="URL is required")
        
        # Analyze the URL and get the response from LLM
        analysis = analyze_url(url)

        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'analysis': analysis})

    return render_template("index.html", analysis=analysis)

@app.route("/ask", methods=["POST"])
def ask_question():
    """Handle questions asked by the user."""
    question = request.json.get("question")
    url = request.json.get("url")

    if not question or not url:
        return jsonify({"error": "Both question and URL are required."}), 400

    # Get the main content to answer the question
    main_content = extract_main_content(url)
    
    if main_content:
        question_response = ask_question_to_llm(question, main_content)
        return jsonify({"response": question_response})
    else:
        return jsonify({"error": "Could not extract content from the URL."}), 400

if __name__ == "__main__":
    app.run(debug=True)
