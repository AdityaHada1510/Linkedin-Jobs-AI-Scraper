import openai
import streamlit as st

openai.api_key = st.secrets["openai_api_key"]

def parse_job_with_llm(description: str, model="gpt-3.5-turbo") -> str:
    try:
        prompt_template = """
            You are an expert recruiter assistant. Analyze the following job description and extract structured information.

            Job Description:
            {description}

            Return the results in this format:
            ---
            Job Summary:
            - (2 lines max)

            Required Skills:
            - Skill 1
            - Skill 2

            Tools & Technologies:
            - Tool 1
            - Tool 2

            Key Responsibilities:
            - Responsibility 1
            - Responsibility 2

            Seniority Level: (Entry / Mid / Senior / Internship / Not mentioned)
            ---
            """
        messages = [
            {"role": "system", "content": "You are a helpful recruiter assistant."},
            {"role": "user", "content": prompt_template.format(description=description)}
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.4
        )

        return response.choices[0].message["content"]

    except Exception as e:
        print(f"❌ GPT Error: {e}")
        return ""

