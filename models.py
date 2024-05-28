from llms import ClaudeModel, MixtralModel
from doc_reader import load_pdf, load_pdf_ocr
import json
import prompts

class QuizzGenModel:
    def __init__(self) -> None:
        self.claude_model = ClaudeModel()  # Using the ClaudeModel for generating questions and answers.
        self.mixtral = MixtralModel("")

    def generate(self, pdf_path: str,num_ques : int,histpath="", user_req="",ocr_scan=False,lang="english"):
    
        # First, extract text from the PDF.
        history = {}
        texts = load_pdf(pdf_path)  # Assuming the PDF contains mostly text.
        if ocr_scan:  # If text extraction failed, fall back to OCR.
            texts = load_pdf_ocr(pdf_path)
        
        # Combine all text pieces into one string for context.
        context = "\n######### New Page starts #############\n".join(texts)
        # Use the ClaudeModel to generate questions and answers.
        primary_prompt = prompts.get_prompt(num_ques,user_req) + "\n" + context
        response = self.claude_model.predict(primary_prompt)
        outp = ""
        error_occured = False
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
                qna_json = {"data":json.loads(outp.encode("utf-8")), "costing":""}
            except json.JSONDecodeError:
                error_occured = True
                qna_json = {"message":"Something went wrong please try again","data":outp}
        if not error_occured:
            history["user"] = []
            history["user"].append({"role":"user","content":f"generate questions on this file {histpath}. and keep this things in mind while generating questions. {user_req}"})
            history["user"].append({"role":"assistant","content":json.dumps(qna_json)})
            json.dump(history,open(histpath,"w",encoding="utf-8"),indent=4)
        return qna_json

    def feedback_qna(self, qn_inp, hist, lang = "english"):
        ans = '\n'.join(qn_inp)
        if lang.lower() != "german":
            prmpt = f"""
            User Gave These answers to your generated qna. Give a feedback on these. Also Give a score for each question. return answer in json objects 
            User Answers: {ans}
            """
            response = self.claude_model.predict(prmpt,hist).content[0].text
            return {"data":response, "costing":""}
        else:
            prmpt = f"""
            User Gave These answers to your generated qna. Give a feedback on these. Give feedback in german. Also Give a score for each question. return answer in json objects 
            User Answers: {ans}
            """
            response = self.mixtral.predict(prmpt,hist)
            return {"data":response, "costing":""}
