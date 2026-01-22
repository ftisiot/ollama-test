#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
import re
from html.parser import HTMLParser

OLLAMA_URL = "http://localhost:11434"

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = ['script', 'style', 'meta', 'link', 'head']
        self.in_skip = False
        
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.in_skip = True
            
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.in_skip = False
        elif tag in ['p', 'div', 'br', 'li']:
            self.text.append('\n')
            
    def handle_data(self, data):
        if not self.in_skip:
            self.text.append(data)
    
    def get_text(self):
        return ' '.join(self.text).strip()

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Web search endpoint
        if self.path.startswith('/search?'):
            try:
                parsed_path = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed_path.query)
                query = params.get('q', [None])[0]
                
                if not query:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Query parameter required'}).encode())
                    return
                
                results = self._search_web(query)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'query': query, 'results': results}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        # Web browsing endpoint
        elif self.path.startswith('/browse?'):
            try:
                parsed_path = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed_path.query)
                url = params.get('url', [None])[0]
                
                if not url:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'URL parameter required'}).encode())
                    return
                
                # Add http:// if no scheme
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Fetch the webpage
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode('utf-8', errors='ignore')
                    
                    # Extract text from HTML
                    parser = HTMLTextExtractor()
                    parser.feed(html_content)
                    text_content = parser.get_text()
                    
                    # Limit content length
                    if len(text_content) > 5000:
                        text_content = text_content[:5000] + "... [content truncated]"
                    
                    result = {
                        'url': url,
                        'title': self._extract_title(html_content),
                        'content': text_content
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        # Proxy API requests to Ollama
        elif self.path.startswith('/api/'):
            try:
                url = f"{OLLAMA_URL}{self.path}"
                with urllib.request.urlopen(url) as response:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            # Serve static files
            super().do_GET()
    
    def _extract_title(self, html):
        """Extract title from HTML"""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return "No title found"
    
    def _search_web(self, query, max_results=3):
        """Search the web using DuckDuckGo HTML search"""
        try:
            # Use DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(search_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
                # Extract search results - try multiple patterns
                results = []
                
                # Pattern 1: Modern DuckDuckGo structure
                patterns = [
                    r'<a class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
                    r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*result__a[^"]*"[^>]*>([^<]+)</a>',
                ]
                
                matches = []
                for pattern in patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        break
                
                # If no matches, try simpler pattern
                if not matches:
                    # Look for any links with href
                    link_pattern = r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
                    all_links = re.findall(link_pattern, html_content, re.IGNORECASE)
                    # Filter out common non-result links
                    matches = [(url, title) for url, title in all_links 
                              if not any(skip in url.lower() for skip in ['duckduckgo.com', 'javascript:', 'mailto:', '#'])]
                
                for i, (url, title) in enumerate(matches[:max_results]):
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif not url.startswith(('http://', 'https://')):
                        continue
                    
                    # Clean title
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    
                    # Fetch and extract content from the result page
                    try:
                        page_req = urllib.request.Request(url)
                        page_req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                        with urllib.request.urlopen(page_req, timeout=8) as page_response:
                            page_html = page_response.read().decode('utf-8', errors='ignore')
                            parser = HTMLTextExtractor()
                            parser.feed(page_html)
                            content = parser.get_text()
                            
                            if len(content) > 2000:
                                content = content[:2000] + "... [truncated]"
                            
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': content
                            })
                    except Exception as e:
                        # If we can't fetch the page, just include the title and URL
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': f'Content unavailable (Error: {str(e)[:50]})'
                        })
                
                # If no results, return a helpful message
                if not results:
                    return [{'error': 'No search results found. Try a different query.'}]
                
                return results
        except Exception as e:
            return [{'error': f'Search failed: {str(e)}'}]
    
    def do_POST(self):
        # Proxy API requests to Ollama
        if self.path.startswith('/api/'):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                url = f"{OLLAMA_URL}{self.path}"
                req = urllib.request.Request(url, data=post_data, method='POST')
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req) as response:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8080
    os.chdir('/app')
    
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Web server with proxy running on port {PORT}")
        httpd.serve_forever()
