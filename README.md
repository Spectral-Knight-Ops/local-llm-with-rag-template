Local RAG LLM Template

    ⚠️ This project is experimental — use responsibly and only on systems you own or are authorized to test.

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
    cd local-llm-with-rag-template
    
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

    # 5. In rag.py, locate the rag_query function. In the prompt declaration section, adjust this for how you intend to
        # to use the LLM. This prompt gets fed to the LLM in the backend due to RAG and helps the LLM understand what
        # exactly you want
        # Also in rag.py, change the model to the model you want.
        # EX: def rag_query(query: str, n_results: int = 3, model: str = "llava-llama3:latest") -> 
        # def rag_query(query: str, n_results: int = 3, model: str = "<your_model>")
        # **Make sure you installed ollama and did a pull for the desired model. If you are unsure what model you want
        # to use, check out one of my other repos: https://github.com/Spectral-Knight-Ops/local-llm-evaluator

    # 6. Build database index (chroma_db should populate. This needs ran every time you add/delete files)
    cd local_llm
    python -c "from rag import initialize_index; initialize_index('../docs', reindex=True)"

    # 7. Run the API server (Run it from project root local-llm-with-rag-template)
    cd .. 
    uvicorn local_llm.api:app --reload

    # 8. Run the web UI (Open a new terminal and run this from \local-llm-with-rag-template\local_llm\)
    # Technically, you could send POST requests at the api and it'll work, but this is much nicer...
    streamlit run chat_ui.py

    # 9. The web UI should automatically open Test connectivity with something simple like "Hello". 
        # If you get an error, most likely step #6 did not work

    # In the terminal tab you ran the streamlit command, you will see a network URL. This is cool if you want to run 
        # the LLM on a server on your network. I have a Mac Mini M4 Pro with 24GB unified memory that works extremely well.
        # To connect remotely, open up a browser and browse to the URL provided
    
Future goals for project

    1. Better document support for additional file types
    2. Provide prebuilt docker container for easy setup and consistent environments
    3. Add support for internet RAG
    4. Optimize code. Code works as is, but could use some love 
    5. Provide examples for better document tagging/import to optimize RAG
    6. Add a RAG toggle so the model can operate normally and not refer to your docs when not needed

License
    
    This project is licensed under the MIT License – see the LICENSE file for details.

Contributing

    Contributions are welcome!