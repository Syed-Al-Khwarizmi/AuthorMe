import io
import re  # Add this import at the top of your file
import html  # Add this import at the top of your file
import os
from typing import List
import openai
import json  # Add this import at the top of your file
from openai import OpenAI  # Add this import at the top of your file
from docx import Document
from html2docx import html2docx
from tqdm import tqdm  # Add this import at the top of your file


def get_sub_topics(topic, num_subtopics, openai_api_key):
    client = OpenAI(api_key=openai_api_key)  # Initialize the client with the provided API key
    prompt = f"""Generate {num_subtopics} subtopics for the main topic: {topic}.
    Return the result as a JSON array of strings, without any additional text.
    Example format:
        "main_topic": "Main Topic",
        "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"]

    The above format should be returned like a json object. Don't include any triple quotes or code block markers or backticks in your response. 
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-3.5-turbo", depending on your preference
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates subtopics."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_content = response.choices[0].message.content
    
    # Remove code block markers if present
    clean_content = re.sub(r'(```|\'\'\'|""")(json|html)?\s*|\s*(```|\'\'\'|""")', '', raw_content).strip()
    
    try:
        parsed_data = json.loads(clean_content)
        subtopics = parsed_data.get('subtopics', [])
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw content:")
        print(raw_content)
        subtopics = []

    response_data = {
        "main_topic": topic if topic else 'default_topic',
        "subtopics": subtopics
    }

    return response_data

def generate_content(main_topic, subtopics, openai_api_key):
    client = OpenAI(api_key=openai_api_key)  # Initialize the client with the provided API key
    full_content = f"<h1>{html.escape(main_topic)}</h1>\n"

    # Wrap the subtopics iteration with tqdm
    for subtopic in tqdm(subtopics, desc="Generating content", unit="subtopic"):
        prompt = f"""Generate detailed content for the subtopic '{subtopic}' within the context of '{main_topic}'.
        Use HTML formatting including <h2> for the subtopic, <p> for paragraphs, <ul> or <ol> for lists, and <blockquote> for examples or quotes.
        Aim for about 300-500 words of informative, well-structured content."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a knowledgeable content creator skilled in writing informative articles."},
                {"role": "user", "content": prompt}
            ]
        )

        subtopic_content = response.choices[0].message.content.strip()
        full_content += f"\n{subtopic_content}\n"

    return full_content

# Convert HTML to DOCX
def html_to_docx(html_content, title):
    try:
        # Print the HTML content for debugging
        print("HTML Content:", html_content)
        
        # Convert HTML to DOCX
        docx_stream = html2docx(html_content, title=title)
        
        # Save the document to a BytesIO stream
        output_stream = io.BytesIO()
        output_stream.write(docx_stream.getvalue())
        output_stream.seek(0)
        
        return output_stream
    except Exception as e:
        print("Error during HTML to DOCX conversion:", e)
        return None
