# How to run it
Run the following commands:

    poetry install

    docker run -p 8080:8080 -p 50051:50051 -d semitechnologies/weaviate:1.27.5

    poetry run streamlit run llamaindex_rag/app.py

# Configure your Python Interpreter 

If you encounter "Imports not resolved" errors in individual files, follow these steps to identify and set the interpreter path:

1. Identify the interpreter path by running the following command in your terminal:

        poetry env info --path
        
2. In VS Code, open the Command Palette by pressing Ctrl + Shift + P (or Cmd + Shift + P on macOS).
3. Type "Python: Select Interpreter" and select it from the list.

4. Choose "Enter Interpreter Path" and paste the path you obtained from the previous command.