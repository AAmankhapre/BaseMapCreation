from flask import Flask, render_template, request, send_file, redirect, url_for
import matplotlib.pyplot as plt
import io
import os
import uuid
import prettymaps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/maps"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("location", "name of Place ")
        radius = float(request.form.get("radius", 0.75))
        circular = request.form.get("circular") == "on"
        preset = request.form.get("preset", "default")
        width = float(request.form.get("width", 8.27))
        height = float(request.form.get("height", 11.69))
        dpi = int(request.form.get("dpi", 100))

        # Colors
        colors = [request.form.get(f"color_{i}") for i in range(1, int(request.form.get("num_colors", 2)) + 1)]

        # Layers
        layers = {}
        for layer in ['building', 'streets', 'waterway', 'water', 'sea', 'forest', 'green', 'rock', 'beach', 'parking']:
            if request.form.get(layer):
                layers[layer] = {}

        # Plot and save to file
        fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
        prettymaps.plot(
            query=query,
            radius=radius * 1000,
            circle=circular,
            layers=layers,
            style={"building": {"palette": colors}},
            figsize=(width, height),
            preset=preset,
            show=False,
            ax=ax,
        )

        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        plt.savefig(filepath, format="png", bbox_inches="tight", dpi=dpi)
        plt.close(fig)

        return redirect(url_for("result", filename=filename))

    presets = prettymaps.presets().to_dict()
    preset_options = list(presets["preset"].values())
    return render_template("index.html", presets=preset_options)

@app.route("/result")
def result():
    filename = request.args.get("filename")
    return render_template("result.html", image_url=url_for("static", filename=f"maps/{filename}"), filename=filename)

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                     as_attachment=True,
                     download_name="basemap.png",
                     mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
