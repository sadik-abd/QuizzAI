from flask import Flask, request, jsonify
from flask_cors import CORS
from models import QuizzGenModel
import os

app = Flask(__name__)
model = QuizzGenModel()
CORS(app)

@app.route("/generate", methods=['POST'])
def gen_message():
    try:
        # Retrieve data from the form
        num_questions = int(request.form["num_questions"])  # Make sure this matches your form's field
        user_prompt = request.form.get("prompt", "")  # Use .get for optional fields with default values
        ocr_scan = request.form.get("ocr_scan", False)
        lang = request.form.get("language", "english")
        doc_type = request.form["doc_type"]
        
        # Save the main document
        main_doc = request.files["doc"]
        saved_path = os.path.join("./docs", main_doc.filename)  # Define your save directory
        main_doc.save(saved_path)
        
        # Generate the output using the model
        output = model.generate(saved_path, num_questions, user_req=user_prompt,ocr_scan=ocr_scan,lang=lang)

        # Create a response
        response = output
        return jsonify(response), 200  # Sending back the JSON response

    except Exception as e:
        # Handle errors
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/gen_feedback", methods=['POST'])
def gen_feedback():
    # Check if the request contains JSON data
    if request.is_json:
        # Get the JSON data
        data = request.get_json()

        # Process the data, for example, print it
        outp = model.feedback_qna(data["user_answers"],data["history"],data["language"])
        # Respond back with the processed data or a success message
        return jsonify({"message": "Model Feedback is given", "output": outp}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400



if __name__ == "__main__":
    app.run(debug=True)  # Remember to turn off debug mode in production
