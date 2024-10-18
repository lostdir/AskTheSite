
# Ask The Site

**Ask The Site** is an interactive web application designed to facilitate seamless communication with the content of any website. By leveraging the capabilities of advanced language models (LLMs), this tool allows users to ask questions and receive insightful responses based on the content of a specified URL.

## Key Features

- **URL Input**: Users can input any valid URL to initiate an analysis of the website's content. The application processes the URL to extract key information, enabling meaningful interaction.

- **Chat Functionality**: Once the URL is processed, users can engage in a conversational format by asking questions related to the website's content. The underlying LLM interprets the queries and provides contextually relevant answers.

- **Dynamic Content Extraction**: The application extracts various elements from the specified website, such as headings, paragraphs, and lists, which form the basis for generating responses. This dynamic content extraction allows for a richer user experience and more accurate information retrieval.


## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Adding Groq API](#adding-groq-api)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Features
- Enter any valid URL to chat with its content.
- Ask questions and receive relevant answers based on the website's content.
- Offers two modes: a simple Flask web interface and a more interactive Streamlit interface.
- Powered by a language model (LLM) for enhanced conversational capabilities.
- Simple and user-friendly design.

## Technologies Used
- **Python**: The main programming language.
- **Flask**: For the web application backend.
- **Streamlit**: For creating an interactive web application interface.
- **BeautifulSoup**: For web scraping to extract content from websites.
- **Requests**: To make HTTP requests for fetching website data.
- **LangChain Groq**: To integrate the language model for processing and responding to user queries.
- **HTML/CSS**: For styling the web application.

## Installation

### Prerequisites
Make sure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

### Steps to Install
1. Clone the repository:
   ```bash
   git clone https://github.com/lostdir/AskTheSite.git
   ```
2. Navigate to the project directory:
   ```bash
   cd AskTheSite
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Adding Groq API
To integrate the Groq API for enhanced conversational capabilities, follow these steps:

1. **Sign Up/Log In**:
   - Go to the [Groq Console](https://console.groq.com/).
   - Sign up for an account or log in if you already have one.

2. **Create a New API Key**:
   - Navigate to the API section in the Groq Console.
   - Click on "Create API Key".
   - Save the generated API key securely; you will need it for your application.

3. **Configure Your Application**:
   - In your project directory, create a `.env` file if it doesn't already exist.
   - Add your Groq API key to the `.env` file:
     ```plaintext
     GROQ_API_KEY=your_api_key_here
     ```

4. **Update the Application**:
   - Ensure your application is set up to read the API key from the environment variables.
   - Use the Groq API to process user queries in the application logic.

5. **Test the Integration**:
   - Run your Flask or Streamlit application.
   - Enter a URL and ask questions to verify that the integration is working correctly.


## Usage
### Flask Interface
1. Run the Flask application:
   ```bash
   python flask_app.py
   ```
2. Open your web browser and go to `http://localhost:5000`.
3. Enter the URL of the website you want to chat with in the input field.
4. Ask questions about the website's content and receive insightful answers!

### Streamlit Interface
1. Run the Streamlit application:
   ```bash
   streamlit run streamlit_app.py
   ```
2. Open your web browser and go to `http://localhost:8501`.
3. Enter the URL of the website you want to chat with.
4. Ask questions about the website's content and engage in conversation!

## How It Works
- The application takes a URL input from the user.
- It uses BeautifulSoup to scrape the website's content, including titles, descriptions, keywords, and main content.
- The user can ask questions related to the content of the website.
- The application utilizes a language model to generate responses based on the extracted content.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
