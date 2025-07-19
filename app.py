import os
import re
import logging
import pymongo
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This line must be at the top, right after imports
load_dotenv()

# --- Phase 1: Original Imports ---
# Pre-load everything once
from retrieve import search_faqs
from model import generate_answer

# --- Flask App Initialization ---
app = Flask(__name__, template_folder="templates", static_folder="static")

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# --- Phase 2: MongoDB Database Connection ---
# Now, this will correctly load the updated URI from your .env file
MONGO_URI = os.environ.get("MONGO_URI")

# --- ADDED FOR DEBUGGING ---
# This will print the exact URI your app is trying to use.
logger.info(f"Attempting to connect with MONGO_URI: '{MONGO_URI}'")
# --- END DEBUGGING ADDITION ---

client = None
db = None
gst_collection = None

# Establish connection only if MONGO_URI is set
if MONGO_URI:
    try:
        # Added a serverSelectionTimeoutMS to fail faster if connection is bad
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        
        # PyMongo automatically gets the database from the URI.
        # If no database is in the URI, we connect to it after.
        db = client.get_database()
        if db.name == 'admin': # Default if no db in URI
            db = client['tax_data']

        gst_collection = db['gst_recoords']  # Fixed: was 'gst_records', now 'gst_recoords'
        logger.info(f"✅ Successfully connected to MongoDB! Using database: '{db.name}'")
    except pymongo.errors.ConnectionFailure as e:
        logger.exception(f"❌ Could not connect to MongoDB: {e}")
        gst_collection = None # Ensure collection is None if connection fails
    except Exception as e:
        logger.exception(f"❌ An error occurred during MongoDB setup: {e}")
        gst_collection = None
else:
    logger.warning("⚠️ MONGO_URI not set. GSTIN search is disabled.")


# --- Phase 2: Helper Functions for GSTIN Lookup ---
def find_gstin_in_message(message):
    """Uses regex to find a 15-character GSTIN in a string."""
    # Removed word boundaries (\b) for broader matching.
    gstin_pattern = r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})'
    match = re.search(gstin_pattern, message.upper())
    if match:
        return match.group(0)
    return None

def get_gst_details_from_db(gstin):
    """Queries the MongoDB collection for a given GSTIN and formats the response."""
    if gst_collection is None:
        logger.error("DB search called but gst_collection is None.")
        return "Database connection is not available.", []

    try:
        # --- NEW DEBUGGING CODE ---
        # Let's see if the collection has any documents at all.
        doc_count = gst_collection.count_documents({})
        logger.info(f"Total documents in 'gst_recoords' collection: {doc_count}")
        if doc_count > 0:
            # Let's look at the first document to check its structure.
            sample_doc = gst_collection.find_one({})
            logger.info(f"Sample document from collection: {sample_doc}")
        # --- END NEW DEBUGGING CODE ---

        logger.info(f"Attempting to find document with GSTIN: '{gstin}'")
        # Use direct match instead of regex for better reliability and performance
        record = gst_collection.find_one({"gstin": gstin})
        logger.info(f"MongoDB find_one result (direct match): {record}") # Log the result

        if record:
            # Format a user-friendly response from the database record
            address = record.get('address', {})
            answer = (
                f"🔍 Information for GSTIN: {record.get('gstin', 'N/A')}\n\n"
                f"- Legal Name: {record.get('legal_name', 'N/A')}\n"
                f"- Trade Name: {record.get('trade_name', 'N/A')}\n"
                f"- Status: {record.get('status', 'N/A')}\n"
                f"- Taxpayer Type: {record.get('taxpayer_type', 'N/A')}\n"
                f"- Registration Date: {record.get('registration_date', 'N/A')}\n"
                f"- Address: {address.get('street', '')}, {address.get('city', '')}, {address.get('state', '')} - {address.get('pincode', '')}"
            )
            # For GSTIN lookups, we can return an empty sources list
            return answer, []
        else:
            # If the GSTIN is not found in the database
            answer = f"❌ No record found for GSTIN: {gstin}. Please verify the number."
            return answer, []
    except Exception as e:
        logger.exception(f"An error occurred while querying database: {e}")
        return "An error occurred while searching the database.", []


# --- Flask Routes ---
@app.route("/healthz")
def healthz():
    return "OK", 200

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        logger.exception("Error rendering index.html")
        return "Internal Server Error", 500

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    q = data.get("question", "").strip()
    logger.info("Question: %s", q)

    # --- Phase 2 Logic Integration ---
    # First, check if the query contains a GSTIN
    gstin = find_gstin_in_message(q)
    if gstin and gst_collection is not None:
        logger.info(f"GSTIN detected: {gstin}. Querying database.")
        answer, sources = get_gst_details_from_db(gstin)
        return jsonify(answer=answer, sources=sources)

    # --- Enhanced Phase 1 Logic (FAQ Search) ---
    # If no GSTIN is found, proceed with enhanced FAQ search
    logger.info("No GSTIN found. Proceeding with enhanced FAQ search.")
    
    try:
        # Use enhanced search with more results for better accuracy
        contexts = search_faqs(q, k=5)  # Increased from 3 to 5 for better context
        
        if not contexts:
            answer = "I couldn't find relevant information for your query. This chatbot supports GST/Income-Tax queries and GSTIN lookups."
            sources = []
        elif contexts[0]["score"] > 1.2:  # Adjusted threshold for better filtering
            # Check if it's a partial match that might still be useful
            if contexts[0]["score"] < 1.5 and any(word in contexts[0]["question"].lower() for word in q.lower().split()):
                # Provide the best available answer with a disclaimer
                raw = generate_answer(q, contexts[:3])
                cleaned = re.sub(r"\s*\([^)]+\)\s*$", "", raw).strip()
                answer = f"Based on available information:\n\n{cleaned}"
                answer = answer.replace(": -", ":\n\n- ")
                
                srcs = []
                for c in contexts[:3]:
                    s = c["source"]
                    srcs.extend(s if isinstance(s, list) else [s])
                sources = sorted(set(srcs))
            else:
                answer = "This chatbot supports only GST/Income-Tax queries and GSTIN lookups. Please rephrase your question or ask about specific GST/Income Tax topics."
                sources = []
        else:
            # Generate enhanced answer with better context
            raw = generate_answer(q, contexts[:3])  # Use top 3 most relevant
            cleaned = re.sub(r"\s*\([^)]+\)\s*$", "", raw).strip()
            answer = cleaned.replace(": -", ":\n\n- ")
            
            # Extract sources from all used contexts
            srcs = []
            for c in contexts[:3]:
                s = c["source"]
                srcs.extend(s if isinstance(s, list) else [s])
            sources = sorted(set(srcs))
            
            # Add confidence indicator for very good matches
            if contexts[0]["score"] < 0.5:
                logger.info(f"High confidence answer (score: {contexts[0]['score']:.3f})")
            elif contexts[0]["score"] > 0.8:
                logger.info(f"Lower confidence answer (score: {contexts[0]['score']:.3f})")

    except Exception as e:
        logger.exception(f"Error during FAQ search: {e}")
        answer = "I encountered an error while searching for information. Please try rephrasing your question."
        sources = []

    return jsonify(answer=answer, sources=sources)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
