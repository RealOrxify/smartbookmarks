from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Storage configuration for Vercel compatibility
# On Vercel, use /tmp (ephemeral) or a database for persistence
# For production, consider using Vercel Postgres, Vercel KV, or another database
VERCEL = os.environ.get('VERCEL') == '1'
BOOKMARKS_FILE = '/tmp/bookmarks.json' if VERCEL else 'bookmarks.json'

def load_bookmarks():
    """Load bookmarks from file or return empty list"""
    if os.path.exists(BOOKMARKS_FILE):
        try:
            with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_bookmarks(bookmarks):
    """Save bookmarks to file"""
    # Ensure directory exists if needed (for /tmp, it already exists)
    dir_path = os.path.dirname(BOOKMARKS_FILE)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """Get all bookmarks"""
    return jsonify(load_bookmarks())

@app.route('/api/bookmarks', methods=['POST'])
def add_bookmark():
    """Add a new bookmark"""
    data = request.json
    bookmarks = load_bookmarks()
    
    new_bookmark = {
        'id': str(datetime.now().timestamp()),
        'title': data.get('title', ''),
        'url': data.get('url', ''),
        'description': data.get('description', ''),
        'tags': data.get('tags', []),
        'created': datetime.now().isoformat()
    }
    
    bookmarks.append(new_bookmark)
    save_bookmarks(bookmarks)
    return jsonify(new_bookmark), 201

@app.route('/api/bookmarks/<bookmark_id>', methods=['PUT'])
def update_bookmark(bookmark_id):
    """Update a bookmark"""
    data = request.json
    bookmarks = load_bookmarks()
    
    for bookmark in bookmarks:
        if bookmark['id'] == bookmark_id:
            bookmark['title'] = data.get('title', bookmark['title'])
            bookmark['url'] = data.get('url', bookmark['url'])
            bookmark['description'] = data.get('description', bookmark.get('description', ''))
            bookmark['tags'] = data.get('tags', bookmark.get('tags', []))
            save_bookmarks(bookmarks)
            return jsonify(bookmark)
    
    return jsonify({'error': 'Bookmark not found'}), 404

@app.route('/api/bookmarks/<bookmark_id>', methods=['DELETE'])
def delete_bookmark(bookmark_id):
    """Delete a bookmark"""
    bookmarks = load_bookmarks()
    bookmarks = [b for b in bookmarks if b['id'] != bookmark_id]
    save_bookmarks(bookmarks)
    return jsonify({'success': True})

@app.route('/api/export', methods=['GET'])
def export_bookmarks():
    """Export bookmarks as standalone HTML page with glassmorphism design"""
    bookmarks = load_bookmarks()
    
    # Generate HTML with embedded CSS and glassmorphism design
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Bookmarks</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            padding: 20px;
            overflow-x: hidden;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: white;
            font-size: 3rem;
            font-weight: 700;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            margin-bottom: 10px;
        }

        .header p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
        }

        .bookmarks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .bookmark-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 20px;
            transition: all 0.3s ease;
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .bookmark-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
            background: rgba(255, 255, 255, 0.15);
        }

        .bookmark-title {
            color: white;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 8px;
            word-wrap: break-word;
        }

        .bookmark-title a {
            color: white;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .bookmark-title a:hover {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: underline;
        }

        .bookmark-url {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9rem;
            margin-bottom: 10px;
            word-break: break-all;
        }

        .bookmark-description {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.95rem;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .bookmark-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }

        .tag {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: white;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: white;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .empty-state h2 {
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .empty-state p {
            font-size: 1.1rem;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }

            .bookmarks-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ My Bookmarks</h1>
            <p>Exported on ''' + datetime.now().strftime('%B %d, %Y at %I:%M %p') + '''</p>
        </div>
        <div class="bookmarks-grid">
'''
    
    if not bookmarks:
        html += '''
            <div class="empty-state">
                <h2>📚 No bookmarks</h2>
                <p>No bookmarks to display</p>
            </div>
'''
    else:
        # Escape HTML to prevent XSS
        def escape_html(text):
            return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
        
        for bookmark in bookmarks:
            title = bookmark.get('title', 'Untitled')
            url = bookmark.get('url', '#')
            description = bookmark.get('description', '')
            tags = bookmark.get('tags', [])
            
            html += f'''
            <div class="bookmark-card">
                <div class="bookmark-title">
                    <a href="{escape_html(url)}" target="_blank" rel="noopener noreferrer">
                        {escape_html(title)}
                    </a>
                </div>
                <div class="bookmark-url">{escape_html(url)}</div>
'''
            if description:
                html += f'                <div class="bookmark-description">{escape_html(description)}</div>\n'
            
            if tags:
                html += '                <div class="bookmark-tags">\n'
                for tag in tags:
                    html += f'                    <span class="tag">{escape_html(tag)}</span>\n'
                html += '                </div>\n'
            
            html += '            </div>\n'
    
    html += '''        </div>
    </div>
</body>
</html>'''
    
    from flask import Response
    return Response(
        html,
        mimetype='text/html',
        headers={'Content-Disposition': 'attachment; filename=my-bookmarks.html'}
    )

@app.route('/api/export/netscape', methods=['GET'])
def export_bookmarks_netscape():
    """Export bookmarks as HTML (Netscape bookmark format for browser import)"""
    bookmarks = load_bookmarks()
    
    html = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
'''
    
    for bookmark in bookmarks:
        title = bookmark.get('title', 'Untitled')
        url = bookmark.get('url', '#')
        description = bookmark.get('description', '')
        add_date = int(datetime.fromisoformat(bookmark.get('created', datetime.now().isoformat())).timestamp())
        
        html += f'    <DT><A HREF="{url}" ADD_DATE="{add_date}">{title}</A>\n'
        if description:
            html += f'    <DD>{description}\n'
    
    html += '</DL><p>'
    
    from flask import Response
    return Response(
        html,
        mimetype='text/html',
        headers={'Content-Disposition': 'attachment; filename=bookmarks-netscape.html'}
    )