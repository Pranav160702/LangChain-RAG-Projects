import requests
import json
import gradio as gr

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json'
}

history = []

def generate_response(prompt):
    history.append(prompt)
    final_prompt = "\n".join(history)
    
    data = {
        "model": "coder",
        "prompt": final_prompt,
        "sstream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an error for HTTP error responses

        # Print raw response for debugging
        print("Raw response:", response.text)
        
        combined_response = []
        for line in response.text.splitlines():
            try:
                response_json = json.loads(line)  # Parse each line as JSON
                if response_json.get('done'):
                    combined_response.append(response_json.get('response', ''))
                    break  # Stop processing if done is True
                else:
                    combined_response.append(response_json.get('response', ''))
            except json.JSONDecodeError:
                continue  # Skip any lines that are not valid JSON

        return ''.join(combined_response)
        
    except requests.RequestException as e:
        return f"Request Error: {str(e)}"

interface = gr.Interface(
    fn=generate_response,
    inputs=gr.Textbox(lines=4, placeholder="Enter your prompt"),
    outputs='text'
)

interface.launch()
