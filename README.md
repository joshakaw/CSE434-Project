# CSE434-Project2

# Project Structure
The project is separated into a Backend (which uses Python & Flask) and a
Frontend (which uses Angular).

# Building & Running

First, to build the Angular project into the `dist` folder, run
`ng build` in `/Frontend`.

Next, to run the server (which references the built `dist` folder),
run `python app.py` or use your virtual Python environment in `/Backend`.

This process compiles the Angular project into native HTML and JS files, which the Flask server can reference, so that there is no requirement to host a frontend server or build sites real-time.

# Angular Live Dev Server
To use the Angular live development server, run `ng serve` from the
`Frontend` directory. This updates real-time as you edit the files, as an alternative to manually building every time.