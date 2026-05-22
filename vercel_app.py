from app import app
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.wrappers import Response
import sys
import json

# Configure app for proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def create_environ(request):
    """Create WSGI environment from request"""
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    headers = request.get('headers', {})
    body = request.get('body', '')
    query_string = ''
    
    # Extract query string from path if present
    if '?' in path:
        path, query_string = path.split('?', 1)
    
    # Create a stream-like object for wsgi.input
    from io import BytesIO
    if isinstance(body, str):
        body_stream = BytesIO(body.encode('utf-8'))
    elif isinstance(body, bytes):
        body_stream = BytesIO(body)
    else:
        body_stream = BytesIO(b'')
    
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'SERVER_NAME': 'vercel',
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': body_stream,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add headers
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    return environ

def handler(request):
    """Handle incoming requests for Vercel serverless function"""
    try:
        environ = create_environ(request)
        response_data = []
        
        def start_response(status, headers):
            response_data.append({
                'status': status,
                'headers': headers
            })
        
        # Get response from Flask app
        try:
            response_body = b''.join(app.wsgi_app(environ, start_response))
            response_info = response_data[0]
            
            # Check content type to determine if we should decode or use base64
            content_type = ''
            for header_name, header_value in response_info['headers']:
                if header_name.lower() == 'content-type':
                    content_type = header_value.lower()
                    break
            
            # Handle binary responses properly
            is_binary = not (content_type.startswith('text/') or 
                            'json' in content_type or 
                            'xml' in content_type or 
                            'javascript' in content_type or 
                            'html' in content_type)
            
            if is_binary:
                import base64
                return {
                    'statusCode': int(response_info['status'].split()[0]),
                    'headers': {k: v for k, v in response_info['headers']},
                    'body': base64.b64encode(response_body).decode('ascii'),
                    'isBase64Encoded': True
                }
            else:
                return {
                    'statusCode': int(response_info['status'].split()[0]),
                    'headers': {k: v for k, v in response_info['headers']},
                    'body': response_body.decode('utf-8')
                }
        except Exception as e:
            print(f"Database Error: {str(e)}", file=sys.stderr)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': str(e)
                }),
                'headers': {'Content-Type': 'application/json'}
            }
    except Exception as e:
        print(f"Server Error: {str(e)}", file=sys.stderr)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }),
            'headers': {'Content-Type': 'application/json'}
        }
