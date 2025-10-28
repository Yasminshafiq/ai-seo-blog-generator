import google.generativeai as genai

# 🔹 Configure your API key
genai.configure(api_key="AIzaSyAf1X-nWg83HHAdxsqa29A0R2zPtC8wBQ0")

# 🔹 Use the latest working model
model = genai.GenerativeModel("models/gemini-2.5-flash")

def generate_blog_idea(keyword):
    prompt = f"""
    Write a detailed, SEO-optimized blog post about "{keyword}".
    Include:
    - A catchy title
    - Meta description
    - Introduction
    - 3-4 subheadings with short paragraphs
    - A short conclusion
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    keyword = input("Enter a keyword: ")
    print(generate_blog_idea(keyword))
