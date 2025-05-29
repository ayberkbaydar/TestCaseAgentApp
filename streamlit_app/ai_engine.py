import openai

def get_openai_client(api_key, provider):
    if provider == "openrouter":
        return openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    elif provider == "openai":
        return openai.OpenAI(api_key=api_key)
    else:
        raise ValueError("Unsupported AI provider. Use 'openai' or 'openrouter'.")

def generate_test_cases(doc, lang="English", domain=None, product_name="the product", api_key=None, provider="openrouter"):
    client = get_openai_client(api_key, provider)

    title=doc.get("title","Untitled")
    content=doc.get("content","")
    domain_instruction = f"This documentation belongs to a product in the {domain} domain.\n\n" if domain else ""
    language_instruction = "\n🟩 IMPORTANT: Write all test cases in **TURKISH** language only.\n" if lang == "Turkish" else ""

    prompt = f"""
{language_instruction}
You are a skilled QA engineer with extensive experience in analyzing software requirements and 
generating structured test cases for {product_name}. 
Your task is to read the following documentation, understand the functional and non-functional 
aspects of the feature, and generate detailed manual test cases accordingly.
Please determine whether the documentation represents a user story, feature description, or 
acceptance criteria, and use that context to define relevant and realistic test cases. 
Consider both positive and negative scenarios, edge cases, and user roles if applicable.
{domain_instruction}

🛑 IMPORTANT RULE:
Each test case MUST include the following 4 sections — no test case is valid without all of them:
•⁠  ⁠Test Name
•⁠  ⁠Preconditions
•⁠  ⁠Steps
•⁠  ⁠Expected Result ← This must NEVER be skipped or left empty.

FORMAT:
Test cases must be clearly separated. For each test case, include:

Title: [Test Case Title]
Preconditions:
[Bullet list or numbered conditions]
Steps:
[Numbered steps]
Expected Result:
[Expected outcome. Must always be filled.]

Guidelines:
•⁠  ⁠Keep test cases clear and concise.
•⁠  ⁠Include multiple test cases to cover different paths (happy path, edge cases, validations).
•⁠  ⁠Where applicable, include boundary conditions and error handling scenarios.
•⁠  ⁠Tailor test cases for different user roles if mentioned (e.g., Admin, Guest, Registered User).
•⁠  ⁠Ensure traceability back to the documented requirement or acceptance criteria.

•⁠  ⁠Product Name: {product_name}
•⁠  ⁠Feature/User Story: {title}
•⁠  ⁠Content:{content}

Title: {title}
Content:
{content}
"""

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": f"You are a skilled QA engineer with extensive experience in analyzing software requirements and generating clear, structured test cases for {product_name}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API error: {e}"