import os
import json
import git
import pandas as pd
from flask import render_template
from flask import Flask, request

from src.update import update
from src.utils import json_to_dataframe


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


app = Flask("Hardest Climbs", template_folder=THIS_FOLDER + "/templates")

with open(os.path.join(THIS_FOLDER, 'data/lead.json'), "r", encoding='utf-8') as f:
    lead_data = json.load(f)

with open(os.path.join(THIS_FOLDER, 'data/boulder.json'), "r", encoding='utf-8') as f:
    boulder_data = json.load(f)


lead = json_to_dataframe(json_data=lead_data)
boulder = json_to_dataframe(json_data=boulder_data)
data = pd.concat([lead, boulder])
data = data.sort_values(
    by=["style", "rank", "name", "last_name"],
    ascending=False,
)


@app.route('/')
def index():
    unique_climbs = data[data["is_fa"]]

    climbs = pd.concat([
        unique_climbs[unique_climbs["style"] == "sport"][0:1],
        unique_climbs[unique_climbs["style"] == "bouldering"][0:1],
        unique_climbs[unique_climbs["style"] == "sport"][1:2],
        unique_climbs[unique_climbs["style"] == "bouldering"][1:2],
        unique_climbs[unique_climbs["style"] == "sport"][2:3],
        unique_climbs[unique_climbs["style"] == "bouldering"][2:3],
    ])

    return render_template('index.html', climbs=climbs)


@app.route('/sport')
def sport():
    climbs = data[(data["is_fa"]) & (data["style"] == "sport")]

    return render_template(
        'generic.html',
        title="Sport Climbing",
        category="sport",
        climbs=climbs
    )


@app.route("/bouldering")
def bouldering():
    climbs = data[(data["is_fa"]) & (data["style"] == "bouldering")]

    return render_template(
        'generic.html',
        title="Bouldering",
        category="bouldering",
        climbs=climbs
    )


@app.route("/sport/climber/<climber>")
def sport_climber(climber):
    climbs = data[(data["climber_key"] == climber) & (data["style"] == "sport")]

    if climbs.shape[0] > 0:
        return render_template(
            'generic.html',
            title=f"Sport Climbing: {climber.replace('+', ' ').title()}",
            category="sport",
            climbs=climbs,
        )
    else:
        return "Climber not found", 404
    

@app.route("/sport/route/<route>")
def sport_route(route):
    climbs = data[(data["route_key"] == route) & (data["style"] == "sport") & (data["is_fa"])]

    if climbs.shape[0] > 0:
        return render_template(
            'single.html',
            title="",
            category="sport",
            climbs=climbs.iloc[0],
        )
    else:
        return "Route not found", 404


@app.route("/bouldering/climber/<climber>")
def bouldering_climber(climber):
    climbs = data[(data["climber_key"] == climber) & (data["style"] == "bouldering")]

    if climbs.shape[0] > 0:
        return render_template(
            'generic.html',
            title=f"Bouldering: {climber.replace('+', ' ').title()}",
            category="bouldering",
            climbs=climbs
        )
    else:
        return "Climber not found", 404
    

@app.route("/bouldering/problem/<problem>")
def bouldering_route(problem):
    climbs = data[(data["route_key"] == problem) & (data["style"] == "bouldering") & (data["is_fa"])]

    if climbs.shape[0] > 0:
        return render_template(
            'single.html',
            title="",
            category="bouldering",
            climbs=climbs.iloc[0],
        )
    else:
        return "Boulder not found", 404


@app.route("/update", methods=["POST"])
def webhook():
    if request.method == "POST":
        repo = git.Repo("~/mysite")
        origin = repo.remotes.origin
        origin.pull()
        
        update()
        
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


# helper template filters ----

@app.template_filter('bg_alternate')
def bg_alternate(index):
    return "secondary" if index % 2 == 0 else "dark"


@app.template_filter('climber_first_name')
def climber_first_name(name):
    return " ".join(name.split(" ")[0:-1])


@app.template_filter('climber_last_name')
def climber_last_name(name):
    return name.split(" ")[-1]
