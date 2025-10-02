Local RAG LLM Template

    A lightweight template for running a local LLM with Retrieval-Augmented Generation (RAG). Check out this video 
    made by IBM if you want a clear visualization of RAG: https://www.youtube.com/watch?v=T-D1OfcDW1M

Features

    🔎 Index your own notes, cheat sheets, or datasets into a local vector database. The LLM will reference the document(s)
    you provide and then use its own training to formulate a response. The better your document is organized, the quicker it
    can be indexed. See the example provided.
    
    💬 Query them with an LLM of your choice (via Ollama). If you are unsure what model you want to use, check out one of 
    my other repos: https://github.com/Spectral-Knight-Ops/local-llm-evaluator
    
    🖥️ Use a simple web UI for interactive chat that can be accessed locally or remotely.
    
    ✅ Ideal for building private assistants powered by your own knowledge — for cybersecurity, coding, research, datasets, etc.

Usage
    
    # 1. Clone the repo
    git clone https://github.com/Spectral-Knight-Ops/local-llm-with-rag-template
    
    # 2. Create and activate a virtual environment
    python -m venv .venv
    # On Linux/MacOS
    source .venv/bin/activate
    # On Windows (PowerShell)
    .venv\Scripts\activate.bat
    
    # 3. Install dependencies
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt

    # 4. Add documents to /docs/ directory (Only supports .txt right now)

    # 5. Build database index (chroma_db should populate. This needs ran every time you add/delete files)
    python -c "from rag import initialize_index; initialize_index('docs', reindex=True)"

    # 6. Run the API server
    uvicorn api:app --reload

    # 7. Run the web UI
    streamlit run chat_ui.py

    # 8. Test connectivity with something simple like "Hello". If you get an error, most likely step #6 did not work
    
Future goals for project

    1. Better document support for additional file types
    2. Provide prebuilt docker container for easy setup and consistent environments
    3. Add support for internet RAG
    4. Optimize code. Code works as is, but could use some love 

License
    
    This project is licensed under the MIT License – see the LICENSE file for details.

Contributing

    Contributions are welcome!