import os
import json
from flask import render_template
from flask import Flask

from functions import create_html_columns, create_html_from_json_element

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


app = Flask("Hardest Climbs", template_folder=THIS_FOLDER)

with open(os.path.join(THIS_FOLDER, 'data/lead.json'), "r") as f:
    lead_data = json.load(f)

with open(os.path.join(THIS_FOLDER, 'data/boulder.json'), "r") as f:
    boulder_data = json.load(f)


@app.route('/')
def index():
    climbs = []
    for i, (l, b) in enumerate(zip(lead_data[0:3], boulder_data[0:3])):
        if i % 2 == 0:
            climbs.append(create_html_from_json_element(l, category="sport"))
            climbs.append(create_html_from_json_element(b, category="bouldering"))
        else:
            climbs.append(create_html_from_json_element(l, category="sport", bg="dark"))
            climbs.append(create_html_from_json_element(b, category="bouldering", bg="dark"))


    return render_template('index.html', climbs="".join(climbs))


@app.route('/sport')
def sport():
    climbs = create_html_columns(x=lead_data, category="sport")

    # TODO Fix template
    return render_template('generic.html', title="Sport Climbing", climbs=climbs)


@app.route("/bouldering")
def bouldering():
    climbs = create_html_columns(x=boulder_data, category="bouldering")

    # TODO Fix template
    return render_template('generic.html', title="Bouldering", climbs=climbs)


@app.route("/sport/<climber>")
def sport_climber(climber):
    # TODO More elegant solution would require better data system than JSON/dict
    fa_data = [x for x in lead_data if climber in x["fa"].lower()]
    repeat_data = [x for x in lead_data if any(climber in y.lower() for y in x["repeat"])]
    climbs = create_html_columns(x=fa_data + repeat_data, category="sport")

    # TODO Fix template
    return render_template('generic.html', title=f"Sport Climbing: {climber.capitalize()}", climbs=climbs)


@app.route("/bouldering/<climber>")
def bouldering_climber(climber):
    # TODO More elegant solution would require better data system than JSON/dict
    fa_data = [x for x in boulder_data if climber in x["fa"].lower()]
    repeat_data = [x for x in boulder_data if any(climber in y.lower() for y in x["repeat"])]
    climbs = create_html_columns(x=fa_data + repeat_data, category="bouldering")

    # TODO Fix template
    return render_template('generic.html', title=f"Bouldering: {climber.capitalize()}", climbs=climbs)
