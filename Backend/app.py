from flask import Flask, send_from_directory

app = Flask(
    __name__, static_folder="../Frontend/dist/Frontend/browser", static_url_path="",
)

print(app.static_folder)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# The static_url_path='' ensures files are served from the root URL


# Root url is Angular app
@app.route("/")
def serve_angular_app():
    return send_from_directory(app.static_folder, "index.html")

# Serve other files (like .js/.css)
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


# Our project APIs
@app.route("/api/data")
def get_data():
    return {"message": "Hello from Flask API"}

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)