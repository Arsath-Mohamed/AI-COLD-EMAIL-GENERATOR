import os
from groq import Groq
from dotenv import load_dotenv


class LLMError(RuntimeError):
    """Raised when an email cannot be generated."""

# Load environment variables from the .env file
load_dotenv()

def generate_cold_email(company_name, job_role, user_details, scraped_content, tone="Formal", length="Medium"):
    """
    Generates a personalized cold email using the Groq API.
    """
    # Get the API key from the environment variables
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Check if the API key exists
    if not api_key:
        raise LLMError("GROQ_API_KEY is not set. Add it to your .env file.")
        
    # Initialize the Groq client
    client = Groq(api_key=api_key)
    
    # We limit the scraped content to the first 3000 characters to avoid exceeding token limits
    # and to only give the AI the most relevant top part of the page
    truncated_content = scraped_content[:3000] if scraped_content else "No context provided."
    
    # Construct the prompt instructing the AI what to do
    prompt = f"""
    You are an expert freelance business copywriter helping a freelancer win a project.
    Your task is to write a highly personalized, compelling cold email to a prospective client or decision-maker at {company_name}.
    
    Freelance Service: {job_role}
    
    Information about the applicant (Use this to personalize the email, but keep it natural):
    {user_details}
    
    Information about the client (scraped from their website or project brief):
    {truncated_content}
    
    Instructions:
    1. Write a professional, yet engaging subject line.
    2. The email should be of {length} length.
    3. Start by mentioning something specific about the company based on the scraped content to show genuine interest.
    4. Connect the freelancer's background and skills to the client's business or project needs.
    5. Include a clear Call to Action (CTA) asking for a brief chat.
    6. Keep the tone {tone}.
    7. Do not include placeholders like [Your Name] if the user provided their name. Use the provided details.
    
    Write the email now:
    """
    
    try:
        # Call the Groq API using the llama3-70b model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-20b",
            temperature=0.7, # A bit of creativity
        )
        
        # Return the generated text
        generated_email = chat_completion.choices[0].message.content
        if not generated_email or not generated_email.strip():
            raise LLMError("The LLM returned an empty email.")
        return generated_email.strip()
        
    except Exception as e:
        # Handle any API errors
        raise LLMError(f"Groq API request failed: {e}") from e
