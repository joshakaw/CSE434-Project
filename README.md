# HealthGuide (CSE 434: Gen AI)

How can we use generative AI to reduce wait times and allow practitioners to allocate resources _before_ patient arrival? Historically patients' conditions is only evaluated at the time-of-arrival to a hospital, which leads to a small amount of wait time as resources are allocated to treat the symptoms. In urgent situations like heart attack, uncontrollable bleeding, or high fever, every minute lost exponentially decreases the effectiveness of treatment. HealthGuide allows a patient to be evaluated before their arrival to the hospital (with the help of an app, connected to 911 centers, or a phone service) to give practitioners an early triage rating of arriving patients. Additionally, departments related to the incoming patient's condition are detected. This repository contains code for triage evaluation part.

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
