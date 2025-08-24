# app.py — Chat-only UI, auto indexing & persistence (Gemini + LlamaIndex)
import os
import streamlit as st
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LlamaIndex core
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Settings,
    load_index_from_storage,
)
from llama_index.core.storage.storage_context import StorageContext

# Updated Gemini backends (non-deprecated)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

# ----------------- CONFIG -----------------
load_dotenv()

# Try to get API key from environment first, then from config
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    try:
        from config import GOOGLE_API_KEY
    except ImportError:
        pass

st.set_page_config(page_title="Welcome to Zyro", layout="wide")
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 900px;}
.stChatMessage { margin-bottom: .75rem; }
</style>
""", unsafe_allow_html=True)

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is not set. Add it to .env and restart.")
    st.stop()

# LLM + Embeddings (Updated Gemini)
Settings.llm = GoogleGenAI(model="gemini-1.5-flash", api_key=GOOGLE_API_KEY, temperature=0)
Settings.embed_model = GoogleGenAIEmbedding(model_name="text-embedding-004", api_key=GOOGLE_API_KEY)

# Absolute paths to avoid cwd quirks
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_DIR = os.path.join(BASE_DIR, "storage")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# ----------------- HELPERS -----------------
def get_pdf_paths() -> list[str]:
    """Return list of absolute PDF paths in DATA_DIR."""
    try:
        pdf_paths = []
        for f in os.listdir(DATA_DIR):
            if f.lower().endswith(".pdf"):
                full_path = os.path.join(DATA_DIR, f)
                if os.path.isfile(full_path):
                    pdf_paths.append(full_path)
        return pdf_paths
    except FileNotFoundError:
        logger.warning(f"Data directory {DATA_DIR} not found")
        return []
    except Exception as e:
        logger.error(f"Error reading data directory: {e}")
        return []

def save_uploaded_files(files) -> list[tuple[str, str]]:
    """Save uploaded PDFs to DATA_DIR; return list of (filename, full_path) tuples."""
    saved = []
    if not files:
        return saved
    
    for f in files:
        try:
            # Validate file type
            if not f.name.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {f.name}")
                continue
                
            # Check file size (50MB limit)
            file_size_mb = len(f.getbuffer()) / (1024 * 1024)
            if file_size_mb > 50:
                logger.warning(f"File {f.name} too large ({file_size_mb:.1f}MB), skipping")
                st.warning(f"File {f.name} too large ({file_size_mb:.1f}MB), max size is 50MB")
                continue
            
            # Save file
            dest = os.path.join(DATA_DIR, f.name)
            with open(dest, "wb") as out:
                out.write(f.getbuffer())
            saved.append((f.name, dest))  # Store (filename, full_path) tuple
            logger.info(f"Saved file: {f.name} ({file_size_mb:.1f}MB)")
            
        except Exception as e:
            logger.error(f"Error saving file {f.name}: {e}")
            st.error(f"Failed to save {f.name}: {e}")
    
    return saved

def build_and_persist_index():
    """(Re)build the vector index from PDFs and persist to disk. Returns index or None."""
    pdfs = get_pdf_paths()
    if not pdfs:
        logger.info("No PDFs found to index")
        return None
    
    try:
        # Use input_files to avoid SimpleDirectoryReader raising 'No files found'
        docs = SimpleDirectoryReader(input_files=pdfs, errors="ignore").load_data()
        if not docs:
            logger.warning("No documents loaded from PDFs")
            return None
        
        logger.info(f"Building index from {len(docs)} documents")
        index = VectorStoreIndex.from_documents(docs, show_progress=True)
        index.storage_context.persist(persist_dir=INDEX_DIR)
        logger.info("Index built and persisted successfully")
        return index
    except Exception as e:
        logger.error(f"Error building index: {e}")
        st.error(f"Failed to build index: {e}")
        return None

def load_index_if_exists():
    """Load a previously persisted index; return index or None."""
    try:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        index = load_index_from_storage(storage_context)
        logger.info("Index loaded from storage successfully")
        return index
    except FileNotFoundError:
        logger.info("No existing index found")
        return None
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return None

def ensure_index(auto_rebuild: bool = False):
    """
    Ensure we have a ready-to-use index.
    - If auto_rebuild=False: try load; if missing, return None.
    - If auto_rebuild=True: rebuild from PDFs and persist; return index or None.
    """
    if not auto_rebuild:
        return load_index_if_exists()
    return build_and_persist_index()

def set_query_engine_stream(index):
    """Create streaming query engine and stash in session state."""
    if index is not None:
        try:
            st.session_state.qe_stream = index.as_query_engine(streaming=True)
            logger.info("Query engine created successfully")
        except Exception as e:
            logger.error(f"Error creating query engine: {e}")
            st.error(f"Failed to create query engine: {e}")

# ----------------- SESSION STATE -----------------
# Only store assistant messages (answers) to keep UI answers-only
if "answers" not in st.session_state:
    st.session_state.answers = []
if "qe_stream" not in st.session_state:
    idx = ensure_index(auto_rebuild=False)  # Load if persisted
    if idx:
        set_query_engine_stream(idx)

# ----------------- SIDEBAR (upload only; indexing is automatic) -----------------
with st.sidebar:
    st.markdown("### 📄 Upload PDFs")
    files = st.file_uploader("Drop PDFs here", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if files:
        # Validate files before processing
        valid_files = [f for f in files if f.name.lower().endswith('.pdf')]
        if valid_files:
            saved = save_uploaded_files(valid_files)
            if saved:
                with st.spinner("Indexing…"):
                    idx = ensure_index(auto_rebuild=True)  # Auto rebuild & persist after upload
                    if idx:
                        set_query_engine_stream(idx)
                        # Show only filenames, not full paths
                        filenames = [filename for filename, _ in saved]
                        st.success(f"Indexed {len(saved)} file(s): {', '.join(filenames)}")
                    else:
                        st.warning("No valid PDFs found to index.")
            else:
                st.warning("No files were saved successfully.")
        else:
            st.warning("Please upload valid PDF files.")
    
    # Show currently uploaded files (by name only)
    st.markdown("### 📚 Current Files")
    current_files = get_pdf_paths()
    if current_files:
        # Extract just the filenames for display
        filenames = [os.path.basename(f) for f in current_files]
        for filename in filenames:
            st.text(f"• {filename}")
    else:
        st.text("No PDFs uploaded yet")
    
    if st.button("Clear answers", use_container_width=True):
        st.session_state.answers = []
        st.rerun()  # Fixed: using st.rerun() instead of deprecated st.experimental_rerun()

# ----------------- MAIN: CHAT (answers only) -----------------
st.title("Welcome to Zyro")  # Updated title

# Show previous assistant answers only
for text in st.session_state.answers:
    with st.chat_message("assistant"):
        st.markdown(text)

prompt = st.chat_input("Ask about your uploaded PDFs…")
if prompt:
    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""

        # Ensure query engine exists (maybe user typed before uploading)
        if "qe_stream" not in st.session_state:
            # Fixed: More efficient index loading logic
            idx = ensure_index(auto_rebuild=False)
            if not idx:
                idx = ensure_index(auto_rebuild=True)
            if idx:
                set_query_engine_stream(idx)

        if "qe_stream" in st.session_state:
            try:
                resp = st.session_state.qe_stream.query(prompt)
                # Fixed: Validate response before processing
                if hasattr(resp, 'response_gen') and resp.response_gen:
                    for token in resp.response_gen:
                        answer += token
                        placeholder.markdown(answer)
                else:
                    answer = "⚠️ No response generated from the model."
                    placeholder.markdown(answer)
            except Exception as e:
                logger.error(f"Error querying: {e}")
                answer = f"⚠️ Error: {e}"
                placeholder.markdown(answer)
        else:
            answer = "📚 **No PDFs uploaded yet!**\n\nPlease upload PDF files in the sidebar to start chatting with your documents."
            placeholder.markdown(answer)

    # Save only the assistant's answer
    st.session_state.answers.append(answer)
