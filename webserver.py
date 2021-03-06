#!/usr/bin/env python3
# coding=utf-8
import argparse
import flask
import re
import os

# Global variables
SECURE = False
SUPPORTED_ERROR_CODES = {428, 429, 400, 401, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                         422, 431, 500, 501, 502, 503, 504, 505}
root = "notes"

# App variables
app = flask.Flask(__name__)


def page_error(error):
    text = "Please try again"
    return flask.render_template('index.html', page_name=str(error), text=text, title="T-Notes:Error")


for code in SUPPORTED_ERROR_CODES:
    app.register_error_handler(code, page_error)


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return flask.redirect('/' + root)


def directory(subdirs=None, files=None, pwd=None, previous=None):
    """Render a directory page"""
    # Every time you open a directory, update the routes
    route_tree(root)
    previous = re.sub(r'[^/]*/$', '', pwd)
    return flask.render_template('directory.html', title="T-Notes:directory", subdirs=subdirs, pwd=pwd, previous=previous,
                                 files=files, page_name=pwd)


def page(pwd=None, file_name=None):
    """Render a leaf"""
    route_tree(root)
    file_path = pwd[1:] + file_name
    text = ""
    with open(file_path,'r') as text_file:
        text += text_file.read()

    return flask.render_template('page.html', page_name=file_name, title="T-Notes:index", previous=pwd, text=text)


def route_tree(rootDir=root):
    """Make a page for each file in the notes tree, if it is a directory, then list out files"""
    previous = ""
    for dirName, subdirList, fileList in os.walk(rootDir):
        route = "/" + dirName + "/"
        app.add_url_rule(rule=route, view_func=directory,
                         defaults={"subdirs": subdirList, "files": fileList, "pwd": route, "previous": previous})
        previous = route
        for fname in fileList:
            file_route = route + fname
            app.add_url_rule(rule=file_route, view_func=page, defaults={"pwd": previous, "file_name": fname})

    pass


route_tree(root)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='The host name or ip address to run on', type=str, default='0.0.0.0')
    parser.add_argument('--port', help='The port number the web server will use', type=int, default=5000)
    parser.add_argument('--cert', help='The SSL certificate', type=str)
    parser.add_argument('--key', help='The SSL private key', type=str)
    parser.add_argument('-d', '--debug', help='Enable debugging mode', action="store_true")
    parser.add_argument('-v', '--verbose', help='Enable verbose mode', action="store_true")
    args = parser.parse_args()

    # Use SSL if keys were supplied
    global SECURE
    SECURE = bool(args.key) and bool(args.cert)

    # Display basic info based on command line arguments
    if args.verbose: print("Verbose mode activated")
    if args.debug: print("Debug mode activated")
    if bool(args.cert) != bool(args.key):
        print("ERROR! --cert and --key must be used together")
        exit(1)
    if args.verbose or args.debug:
        if SECURE:
            print("Using HTTPS on port %d" % args.port)
        else:
            print("Using HTTP on port %d" % args.port)
    if SECURE:
        try:
            context = (args.cert, args.key)
            if args.debug:
                app.run(port=args.port, debug=True, ssl_context=context, host=args.host)
            else:
                app.run(port=args.port, debug=False, ssl_context=context, host=args.host)
        except Exception as e:
            if args.debug:
                print(e)
                exit(2)
            else:
                print("ERROR! Invalid certificate ,key, or host")
                print("Use --debug for more info")
                exit(2)
    else:
        app.run(port=args.port, debug=args.debug, host=args.host)
