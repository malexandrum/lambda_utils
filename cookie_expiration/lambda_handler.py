import json
from http.cookies import SimpleCookie
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # Get headers from the request
    headers = event.get('headers', {})

    # Extract cookies from the request if any
    cookie_header = headers.get('cookie', '')

    # Check if our specific cookie is present
    has_cookie = 'mycookie' in cookie_header
    print(f'has_cookie: {has_cookie}, cookie_header: {cookie_header}, event: {event}')

    # Set the cookie with an expiration time of 10 seconds if it is not present
    if not has_cookie and event.get('requestContext', {}).get('http', {}).get('path', None) == '/':
        expiration_time = (datetime.utcnow() + timedelta(seconds=5)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        set_cookie_header = f"mycookie=testvalue; Expires={expiration_time}; Path=/; HttpOnly"
    else:
        set_cookie_header = ""
        expiration_time = None

    # HTML & JavaScript response
    html_content = f"""
    <html>
    <body>
        <h1>Cookie Expiration Test</h1>
        <p>On page load, a short lived cookie is being set, expiring on <b>{expiration_time}</b></p>
        <p>Sending 10 requests proving that when cookie expires it is no longer being sent</p>
        <p>In Chromium, opening Dev Tools you can actually see the cookie disapearing after 5s</p>
        <p style="display: none;">Has cookie: {has_cookie}</p>
        <ul id="resultList"></ul>
        <button id="testCookieBtn">Send a request</button>
        <script>
            async function testCookie(event, _, c) {{
                    let response = await fetch(window.location.href + '/' + Math.random(), {{credentials: 'include'}});
                    let text = await response.text();
                    let listItem = document.createElement('li');
                    listItem.innerHTML = (new Date()).toUTCString() + ": " + (text.includes(atob('SGFzIGNvb2tpZTogVHJ1ZQ==')) ? "Cookie sent" : "Cookie NOT sent");
                    document.getElementById("resultList").appendChild(listItem);
                    if (c < 10) {{
                        setTimeout(() => {{testCookie(null, null, c+1)}}, 1000)
                    }}
            }}
            testCookie(null, null, 0);
            document.getElementById("testCookieBtn").addEventListener('click', testCookie);
        </script>
    </body>
    </html>
    """

    # Response with headers, including the set-cookie header if applicable
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Set-Cookie': set_cookie_header if not has_cookie else '',
        },
        'body': html_content
    }
