"""
This file allows you to do a quick test against the files you imported. Be sure to reindex the database every time you
add new files

To reindex database, run this inside your venv
python -c "from rag import initialize_index; initialize_index('docs', reindex=True)"
"""

from local_llm.rag import rag_query

print(rag_query("How do I enumerate shares with spider_plus?", n_results=2))
