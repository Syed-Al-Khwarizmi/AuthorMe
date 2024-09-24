import streamlit as st
from author import get_sub_topics, generate_content, html_to_docx

# Streamlit app
st.title("AuthorMe: The content Alchemist")

main_topic = st.text_input("Enter the main topic:")
num_subtopics = st.number_input("Enter the number of subtopics:", min_value=1, max_value=50, value=5)
# Ask for OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")



if st.button("Generate and Download"):
    if main_topic:
        with st.spinner("Generating subtopics..."):
            subtopics = get_sub_topics(main_topic, num_subtopics, openai_api_key)["subtopics"]
        
        # Calculate estimated time range
        min_time = num_subtopics * 5
        max_time = num_subtopics * 9
        st.info(f"Estimated time: {min_time} to {max_time} seconds")
        with st.spinner(f"Generating content... (Estimated time: {min_time}-{max_time} seconds)"):
            article_content = generate_content(main_topic, subtopics, openai_api_key)
        
        with st.spinner("Converting to DOCX..."):
            docx_stream = html_to_docx(article_content, title=main_topic)
        
        if docx_stream:
            st.success("Content generated successfully!")
            st.download_button(
                label="Download DOCX",
                data=docx_stream,
                file_name=f"{main_topic.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.error("Failed to convert HTML to DOCX.")
    else:
        st.error("Please enter a main topic.")
