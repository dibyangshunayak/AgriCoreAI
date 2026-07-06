# =====================================================================
# FILE: backend/app/services/rag_service.py
# DESCRIPTION: RAG Service for AgriCore AI. Integrates with ChromaDB for 
#              vector searches and includes a robust SQLite fallback.
# =====================================================================

import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Resolve DB path
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
RAG_DB_PATH = DB_DIR / "agri_knowledge.db"

# Sample agricultural knowledge for local SQLite semantic fallback
KNOWLEDGE_BASE = [
    {
        "query": "rice cultivation water paddy requirement irrigation",
        "content": "🌿 **Rice Irrigation Guideline**:\nPaddy crops require significant water, typically 1200–1500 mm per season. Standing water of 2–5 cm should be maintained during transplanting and tillering stages. Drain water 10-15 days before harvest."
    },
    {
        "query": "crop rotation legumes nitrogen soil fertility",
        "content": "🔄 **Crop Rotation Strategy**:\nRotate high-nitrogen demands (e.g., maize, rice) with nitrogen-fixing leguminous crops (e.g., soybeans, pulses, clover). This breaks pest cycles, improves soil structure, and enhances natural organic nitrogen."
    },
    {
        "query": "soil fertility nitrogen organic matter fertilizers improve NPK",
        "content": "🌱 **Soil Fertility Guide**:\n1. Apply compost or organic manure to boost organic carbon.\n2. Use biofertilizers containing Azotobacter or Rhizobium.\n3. Balance chemical fertilizer applications based on a soil test (standard NPK ratio)."
    },
    {
        "query": "mango cultivation planting grafting pruning scale anthracnose",
        "content": "🥭 **Mango Cultivation Guide**:\nMangoes thrive in deep, well-drained loamy soils (pH 5.5-7.5). Prune crowded branches after harvest to improve sunlight penetration. Monitor for Anthracnose (fungal spots) during damp periods."
    },
    {
        "query": "tomato watering blight leaves spots wilt disease",
        "content": "🍅 **Tomato Cultivation & Protection**:\nWater tomatoes deeply at the base to avoid wet foliage (which triggers leaf spot diseases/blight). Implement crop rotation and maintain balanced watering to avoid blossom end rot."
    }
]


def init_rag_fallback_db():
    """Initializes the local fallback SQLite knowledge database."""
    try:
        conn = sqlite3.connect(str(RAG_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keywords TEXT,
                content TEXT
            )
        """)
        # Populate if empty
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        if cursor.fetchone()[0] == 0:
            for item in KNOWLEDGE_BASE:
                cursor.execute("INSERT INTO knowledge (keywords, content) VALUES (?, ?)", (item["query"], item["content"]))
            conn.commit()
        conn.close()
        logger.info("SQLite RAG Fallback database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite RAG fallback: {e}", exc_info=True)


# Run RAG fallback DB initialization
init_rag_fallback_db()


class RAGService:
    """
    RAG service wrapper. Connects to ChromaDB if available; otherwise, falls back
    to a keyword-based SQLite lookup over agricultural knowledge segments.
    """
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.use_fallback = True

        try:
            import chromadb
            # If chromadb imports successfully, set up client
            self.chroma_client = chromadb.PersistentClient(path=str(DB_DIR / "chroma_db"))
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection("agri_knowledge")
            self.use_fallback = False
            logger.info("ChromaDB Client initialized successfully.")
        except ImportError:
            logger.warning("ChromaDB package is not installed. Falling back to local SQLite RAG search.")
        except Exception as e:
            logger.error(f"ChromaDB failed to initialize: {e}. Using SQLite fallback.", exc_info=True)

    def retrieve_context(self, query: str, limit: int = 3) -> str:
        """
        Retrieves matching agricultural context for a given query.
        """
        if not query:
            return ""

        logger.info(f"RAG retrieving context for query: '{query}'")

        if not self.use_fallback and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                documents = results.get("documents", [])
                if documents and documents[0]:
                    combined = "\n\n".join(documents[0])
                    logger.info("Successfully retrieved context from ChromaDB.")
                    return combined
            except Exception as e:
                logger.error(f"ChromaDB query failed: {e}. Falling back to SQLite search.", exc_info=True)

        return self._fallback_search(query, limit)

    def _fallback_search(self, query: str, limit: int) -> str:
        """Performs simple keyword matching over the local SQLite knowledge DB."""
        try:
            words = [w.strip().lower() for w in query.split() if len(w) > 3]
            if not words:
                words = [query.lower().strip()]

            conn = sqlite3.connect(str(RAG_DB_PATH))
            cursor = conn.cursor()

            # Rank items based on keyword matches
            cursor.execute("SELECT keywords, content FROM knowledge")
            rows = cursor.fetchall()
            conn.close()

            scored_results = []
            for keywords, content in rows:
                score = sum(1 for word in words if word in keywords.lower())
                if score > 0:
                    scored_results.append((score, content))

            # Sort by score descending
            scored_results.sort(key=lambda x: x[0], reverse=True)
            top_matches = [content for score, content in scored_results[:limit]]

            if top_matches:
                logger.info(f"SQLite RAG match found {len(top_matches)} documents.")
                return "\n\n".join(top_matches)
                
        except Exception as e:
            logger.error(f"RAG fallback search failed: {e}", exc_info=True)

        return ""
