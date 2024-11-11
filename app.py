from flask import Flask, request, jsonify, render_template
from scraper import DetikScraper

app = Flask(__name__)
scraper = DetikScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_detik():
    """
    Flask endpoint for searching detik.com
    Query parameters:
    - q: search query (required)
    - pages: number of pages to scrape (optional, default=3)
    """
    query = request.args.get('q')
    pages = request.args.get('pages', default=3, type=int)

    if not query:
        return jsonify({
            "status": "error",
            "message": "Search query is required"
        }), 400

    if pages < 1 or pages > 10:
        return jsonify({
            "status": "error",
            "message": "Pages must be between 1 and 10"
        }), 400

    results, error = scraper.search(query, max_pages=pages)
    
    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 500

    return jsonify({
        "status": "success",
        "query": query,
        "total_results": len(results),
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=True)