import os
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables to store the lists
BLOCKLIST = set()
ALLOWLIST = set()
META = {}

# Get the directory of the current file (app/main.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_lists():
    global BLOCKLIST, ALLOWLIST, META
    try:
        meta_path = os.path.join(BASE_DIR, 'meta.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                META = json.load(f)
            
            block_file = META.get('blocklist', {}).get('name')
            allow_file = META.get('allowlist', {}).get('name')

            if block_file:
                block_path = os.path.join(BASE_DIR, block_file)
                if os.path.exists(block_path):
                    print(f"Loading blocklist: {block_path}")
                    with open(block_path, 'r') as f:
                        BLOCKLIST = set(line.strip().lower() for line in f if line.strip())
            
            if allow_file:
                allow_path = os.path.join(BASE_DIR, allow_file)
                if os.path.exists(allow_path):
                    print(f"Loading allowlist: {allow_path}")
                    with open(allow_path, 'r') as f:
                        ALLOWLIST = set(line.strip().lower() for line in f if line.strip())
            
            print(f"Loaded {len(BLOCKLIST)} blocked domains and {len(ALLOWLIST)} allowed domains.")
        else:
            print(f"meta.json not found at {meta_path}")
    except Exception as e:
        print(f"Error loading lists: {e}")

# Load lists on startup
load_lists()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search():
    domain = request.args.get('domain', '').strip().lower()
    if not domain:
        return jsonify({"error": "No domain provided"}), 400

    is_blocked = domain in BLOCKLIST
    is_allowed = domain in ALLOWLIST
    
    if not is_blocked:
        parts = domain.split('.')
        for i in range(1, len(parts) - 1):
            parent = '.'.join(parts[i:])
            if parent in BLOCKLIST:
                is_blocked = True
                break

    result = {
        "domain": domain,
        "status": "blocked" if (is_blocked and not is_allowed) else "allowed",
        "reason": "Found in blocklist" if is_blocked else "Not found in blocklist",
        "is_explicitly_allowed": is_allowed
    }
    
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({
        "total_blocked": len(BLOCKLIST),
        "total_allowed": len(ALLOWLIST),
        "last_updated": META.get('blocklist', {}).get('updated_format', 'Unknown')
    })

# --- SEO Routes ---

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    """Simple XML sitemap."""
    pages = [
        {'loc': 'https://pornlocator.ecotron.co.in/', 'lastmod': time.strftime('%Y-%m-%d'), 'changefreq': 'daily', 'priority': '1.0'}
    ]
    xml = render_template('sitemap.xml', pages=pages)
    response = make_response(xml)
    response.headers["Content-Type"] = "application/xml"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
