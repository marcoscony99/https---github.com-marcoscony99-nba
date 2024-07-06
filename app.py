from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')  # Usar o backend 'Agg' para ambientes sem GUI
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import os
from io import BytesIO
import base64

app = Flask(__name__)

def plot_basketball_court(player_name, year, shot_type):
    width = 50
    height = 94 / 2
    key_height = 19
    inner_key_width = 12
    outer_key_width = 16
    backboard_width = 6
    backboard_offset = 4
    neck_length = 0.5
    hoop_radius = 0.75
    hoop_center_y = backboard_offset + neck_length + hoop_radius
    three_point_radius = 23.75
    three_point_side_radius = 22
    three_point_side_height = 14

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot([-width / 2, width / 2, width / 2, -width / 2, -width / 2], [0, 0, height, height, 0], color='black')

    ax.plot([-outer_key_width / 2, -outer_key_width / 2, outer_key_width / 2, outer_key_width / 2], [0, key_height, key_height, 0], color='black')
    ax.plot([-inner_key_width / 2, -inner_key_width / 2, inner_key_width / 2, inner_key_width / 2], [0, key_height, key_height, 0], color='black')

    ax.plot([-backboard_width / 2, backboard_width / 2], [backboard_offset, backboard_offset], color='black')

    hoop = patches.Circle((0, hoop_center_y), hoop_radius, fill=False, color='black')
    ax.add_patch(hoop)

    restricted_area = patches.Arc((0, hoop_center_y), 8, 8, theta1=0, theta2=180, color='black')
    ax.add_patch(restricted_area)

    free_throw_circle_top = patches.Arc((0, key_height), inner_key_width, inner_key_width, theta1=0, theta2=180, color='black')
    free_throw_circle_bottom = patches.Arc((0, key_height), inner_key_width, inner_key_width, theta1=180, theta2=360, color='black', linestyle='dashed')
    ax.add_patch(free_throw_circle_top)
    ax.add_patch(free_throw_circle_bottom)

    three_point_circle = patches.Arc((0, hoop_center_y), three_point_radius * 2, three_point_radius * 2, theta1=0, theta2=180, color='black')
    ax.add_patch(three_point_circle)
    ax.plot([-three_point_side_radius, -three_point_side_radius], [0, three_point_side_height], color='black')
    ax.plot([three_point_side_radius, three_point_side_radius], [0, three_point_side_height], color='black')

    ax.set_xlim(-width / 2, width / 2)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.set_title(f'{shot_type} do {player_name} ({year})', fontsize=14)

    return fig

def plot_player_shots(player_name, shot_type, df, fig):
    player_shots = df.loc[(df['PLAYER_NAME'] == player_name) & (df['SHOT_TYPE'] == shot_type)]
    made_shots = player_shots[player_shots['SHOT_MADE']]
    missed_shots = player_shots[~player_shots['SHOT_MADE']]
    total_made = len(made_shots)
    total_missed = len(missed_shots)

    total_shots = total_made + total_missed
    if total_shots > 0:
        shooting_percentage = total_made / total_shots * 100
    else:
        shooting_percentage = 0

    ax = fig.gca()
    ax.scatter(made_shots['LOC_X'], made_shots['LOC_Y'], color='green', marker='o')
    ax.scatter(missed_shots['LOC_X'], missed_shots['LOC_Y'], color='red', marker='x')

    stats_str = f"Total de arremessos: {total_shots}\nAcertos: {total_made} ({shooting_percentage:.1f}%)\nErros: {total_missed}"
    ax.text(1.05, 0.95, stats_str, transform=ax.transAxes, horizontalalignment='left', verticalalignment='top', fontsize=10)

    image_stream = BytesIO()
    fig.savefig(image_stream, format='png')
    image_stream.seek(0)

    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    plt.close(fig)

    return image_base64

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player_name = request.form.get("player_name")
        year = int(request.form.get("year"))
        shot_type = request.form.get("shot_type")

        csv_filename = f'static/NBA_{year}_Shots.csv'
        df = pd.read_csv(csv_filename)

        fig = plot_basketball_court(player_name, year, shot_type)
        image_base64 = plot_player_shots(player_name, shot_type, df, fig)

        return render_template("index.html", player_name=player_name, year=year, shot_type=shot_type, image_base64=image_base64)

    return render_template("index.html")

if __name__ == "__main__":
    if not os.path.exists('static/images'):
        os.makedirs('static/images')
    app.run(debug=True)
