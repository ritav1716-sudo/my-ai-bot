from flask import Flask, request, jsonify
import google.generativeai as genai
from openai import OpenAI

app = Flask(__name__)

# Apni API Keys yahan dalein
GEMINI_API_KEY = "YAHAN_GEMINI_KEY_DALO"
OPENAI_API_KEY = "YAHAN_GPT_KEY_DALO"

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-pro")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

BRAIN_PROMPT = """
Tum user ke personal executive AI assistant ho.
Tumhara bolne ka dhang ekdam soft, polite, natural aur sharp hona chahiye.
Hamesha concise (chote aur to-the-point) sentences bolo taaki voice output realistic lage.
"""

STOP_WORDS = ["bye", "byy", "thank you", "phir milenge", "stop", "shukriya", "alvida"]

@app.route('/ask', methods=['POST'])
def process_command():
    data = request.get_json(force=True)
    user_query = data.get("text", "").strip()

    if not user_query:
        return jsonify({"reply": "Dost, mujhe aawaz nahi aayi. Dobara kahiye?", "action": "CONTINUE"})

    if any(word in user_query.lower() for word in STOP_WORDS):
        return jsonify({
            "reply": "Theek hai dost, apna khayal rakhna. Session close kar raha hoon, bye!",
            "action": "STOP"
        })

    if "dono" in user_query.lower() or "compare" in user_query.lower():
        try:
            gem_res = gemini_model.generate_content(f"{BRAIN_PROMPT}\nUser: {user_query}").text
            gpt_res = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": BRAIN_PROMPT},
                    {"role": "user", "content": user_query}
                ]
            ).choices[0].message.content

            conclusion_prompt = f"""
            User Query: {user_query}
            Gemini Answer: {gem_res}
            ChatGPT Answer: {gpt_res}
            In dono answers ko analyze karke ek clear, unified, single professional response do.
            """
            final_output = gemini_model.generate_content(conclusion_prompt).text
            return jsonify({"reply": final_output, "action": "CONTINUE"})
        except Exception as e:
            return jsonify({"reply": f"Processing error: {str(e)}", "action": "CONTINUE"})

    try:
        reply = gemini_model.generate_content(f"{BRAIN_PROMPT}\nUser: {user_query}").text
        return jsonify({"reply": reply, "action": "CONTINUE"})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}", "action": "CONTINUE"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

