from flask import Flask, request, Response, session, make_response
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session

# Define your custom headers here
custom_headers = {
    'Device_id': '2093326957',
    'Origin': 'https://www.pipiads.com',
    'Referer': 'https://www.pipiads.com/ad-search',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    # Add other custom headers as needed
}

@app.route('/set-cookie')
def set_cookie():
    # Set the PP-userInfo cookie with a test value
    resp = make_response("Cookie 'PP-userInfo' is set")
    resp.set_cookie('PP-userInfo', '{%22access_token%22:%22NjU2YTA2MWQwY2YwYjI2ZmIzYWY3NjVkLTE3MDMxMDgxMDI=%22%2C%22vip_deadline%22:null%2C%22expires%22:1705700102%2C%22level%22:%22FREE%22%2C%22discount_code%22:null%2C%22timezone_offset%22:-60%2C%22_id%22:%22656a061d0cf0b26fb3af765d%22%2C%22time_zone_id%22:%22Europe/Copenhagen%22%2C%22language_setting%22:%22en%22%2C%22email%22:%22alminde@skiff.com%22%2C%22username%22:%22alminde@skiff.com%22}', httponly=True)
    return resp

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Check if the path contains the blocked substrings
    blocked_paths = ["v1/api/member/info", "v1/api/member/uxsage"]
    if any(blocked_path in path for blocked_path in blocked_paths):
        return Response("Access to this resource is forbidden", status=403)

    # Check for the 'PP-userInfo' cookie and save it in session if it's present
    if 'PP-userInfo' in request.cookies:
        session['PP-userInfo'] = request.cookies['PP-userInfo']

    # Retrieve 'PP-userInfo' from session if it's not in the request cookies
    cookies = {}
    if 'PP-userInfo' in session:
        cookies['PP-userInfo'] = session['PP-userInfo']

    # URL to proxy
    url = 'https://pipiads.com/' + path

    # Merge incoming request headers with custom headers
    headers = {**request.headers, **custom_headers}
    # Remove host header as it's not needed for the forwarded request
    headers.pop('Host', None)

    # Forward the request and get the response

    # Add debug logging to inspect headers
    app.logger.debug(f"Final headers being sent: {headers}")

    # Forward the request and get the response
    method = request.method
    if method == 'POST':
        resp = requests.post(url, headers=headers, cookies=cookies, data=request.data)
    elif method == 'PUT':
        resp = requests.put(url, headers=headers, cookies=cookies, data=request.data)
    elif method == 'DELETE':
        resp = requests.delete(url, headers=headers, cookies=cookies)
    else:
        resp = requests.get(url, headers=headers, cookies=cookies)
    # Exclude certain headers from the response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)

    # Add cookie to the response if it's in the session
    if 'PP-userInfo' in session:
        response.set_cookie('PP-userInfo', session['PP-userInfo'])

    return response

if __name__ == '__main__':
    app.run(debug=True)
