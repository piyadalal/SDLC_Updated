from google.cloud import aiplatform
from vertexai.language_models import ChatModel

def main():
    # 🔧 Initialize Vertex AI with your project and region
    aiplatform.init(
        project="uk-labs-hackathon-1-0625-dev",  # ✅ Your actual GCP project ID
        location="europe-west3"                  # ✅ Frankfurt (Germany)
    )

    # 💬 Load Gemini 1.5 Pro model
    chat_model = ChatModel.from_pretrained("gemini-1.5-pro-preview")

    # 💬 Start a chat session
    chat = chat_model.start_chat()

    # 📝 Your business requirement
    requirement = """
    As a user, I want to reset my password via email OTP so that I can regain access securely.
    """

    # 🧠 Ask Gemini to generate user stories
    prompt = f"Convert the following requirement into detailed Agile user stories:\n\n{requirement}"
    response = chat.send_message(prompt)

    # 📄 Print the result
    print("\nGenerated User Stories:")
    print(response.text)

if __name__ == "__main__":
    main()
