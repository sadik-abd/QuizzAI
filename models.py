from llms import ClaudeModel, MixtralModel
from doc_reader import load_pdf, load_pdf_ocr
import json
import prompts

class QuizzGenModel:
    def __init__(self) -> None:
        self.claude_model = ClaudeModel()  # Using the ClaudeModel for generating questions and answers.
        self.mixtral = MixtralModel("")

    def generate(self, pdf_path: str,num_ques : int,user_req="",ocr_scan=False,lang="english"):
        if lang.lower() != "german":
            # First, extract text from the PDF.
            texts = load_pdf(pdf_path)  # Assuming the PDF contains mostly text.
            if ocr_scan:  # If text extraction failed, fall back to OCR.
                texts = load_pdf_ocr(pdf_path)
            
            # Combine all text pieces into one string for context.
            context = "\n######### New Page starts #############\n".join(texts)
            # Use the ClaudeModel to generate questions and answers.
            primary_prompt = prompts.get_prompt(num_ques,user_req) + "\n" + context
            response = self.claude_model.predict(primary_prompt)
            outp = ""
            # Format the ClaudeModel response into JSON.
            # Assuming response.content contains the questions and answers in the desired format.
            try:
                # Attempt to parse the string into JSON directly, since Claude's responses should align with our needs.
                outp = response.content[0].text
                qna_json = json.loads(outp)
            except json.JSONDecodeError:
                # If there's a problem with parsing, log or handle it accordingly.
                try:
                    outp = self.mixtral.get_completion("validate this to a perfect json. do things like adding commas to places, etc... dont say a extra word. "+outp)
                    print(outp)
                    qna_json = {"data":json.loads(outp.encode("utf-8")), "costing":""}
                except json.JSONDecodeError:
                    qna_json = {"message":"Something went wrong please try again"}

            return qna_json
        else:
            # First, extract text from the PDF.
            texts = load_pdf(pdf_path)  # Assuming the PDF contains mostly text.
            if ocr_scan:  # If text extraction failed, fall back to OCR.
                texts = load_pdf_ocr(pdf_path)
            
            # Combine all text pieces into one string for context.
            context = "\n######### New Page starts #############\n"
            for text in texts:
                outp = self.mixtral.get_completion("translate the following text into english. \n"+text)
                context += outp
                context += "\n######### New Page starts #############\n"
            # Use the ClaudeModel to generate questions and answers.
            user_rq = self.mixtral.get_completion("translate the following text into english. \n"+user_req)
            primary_prompt = prompts.get_prompt(num_ques,user_rq) + "\n" + context
            response = self.claude_model.predict(primary_prompt)
            outp = ""
            # Format the ClaudeModel response into JSON.
            # Assuming response.content contains the questions and answers in the desired format.
            try:
                # Attempt to parse the string into JSON directly, since Claude's responses should align with our needs.
                outp = response.content[0].text
                outp = self.mixtral.get_completion("translate the following text into German. \n"+outp)
                qna_json = json.loads(outp)
            except json.JSONDecodeError:
                # If there's a problem with parsing, log or handle it accordingly.
                try:
                    outp = self.mixtral.get_completion("validate this to a perfect json. do things like adding commas to places, etc... dont say a extra word. "+outp)
                    print(outp)
                    qna_json = {"data":json.loads(outp.encode("utf-8")), "costing":""}
                except json.JSONDecodeError:
                    qna_json = {"message":"Something went wrong please try again"}

            return qna_json

    def feedback_qna(self, qn_inp, hist, lang = "english"):
        if lang.lower() != "german":
            prmpt = f"""
            User Gave These answers to your generated qna. Give a feedback on these. Also Give a score for each question
            User Answers: {qn_inp}
            """
            response = self.claude_model.predict(prmpt,hist)
            return {"data":response, "costing":""}
        else:
            prmpt = f"""
            User Gave These answers to your generated qna. Give a feedback on these. Give feedback in german. Also Give a score for each question
            User Answers: {qn_inp}
            """
            response = self.mixtral.predict(prmpt,hist)
            return {"data":response, "costing":""}
