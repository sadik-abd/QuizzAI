
PRIMARY_PROMPT = """
Generate 24 questions and answers in JSON format from the given context, which is raw scraped data from a PDF. The output should include both multiple-choice and single-line questions. The format for multiple-choice questions should include the question followed by four options, with the correct answer indicated. The format for single-line questions should simply have the question followed by the answer. Ensure all data is in the format {'question': 'answer', 'options': ['A', 'B', 'C', 'D']} for multiple-choice questions and {'question': 'answer'} for single-line questions. Please maintain the JSON format for easy compilation and do not output any extra words. Return a json object.
"""

def get_prompt(num_ques, user_specific_requests=""):
    prmpt = f"""
    Generate {str(num_ques)} questions and answers in JSON object format from the given context, which is raw scraped data from a PDF. questions should match with the document language. The output should include both multiple-choice and normal questions and answers. The format for multiple-choice questions should include the question followed by four options, with the correct answer indicated. The format for normal questions should simply have the question followed by the answer. Ensure all data is in the format {{'question':'question', 'answer':'answer', 'options': ['A', 'B', 'C', 'D']}} for multiple-choice questions and {{'question': 'question', 'answer':'answer'}} for single-line questions. Please maintain the JSON format and return a json object for easy compilation and do not output any extra words. Also Please keep in mind the user request while generating if there is any. Also your output should be in the users and documents language
    {"User Request: "+user_specific_requests if len(user_specific_requests)>0 else ""}
    """
    return prmpt