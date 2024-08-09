# share notebooks using nbss-upload

import os
import sys
import json
from poldracklab.utils.run_shell_cmd import run_shell_cmd
import hashlib
import pandas as pd


if __name__ == "__main__":

    github_push = True
    notebook_dir = 'notebooks'
    notebooks_to_share = [
        'data_setup_haxby.ipynb',
        'decoding_haxby.ipynb',
        'cv_variability.ipynb',
        'perceptron.ipynb',
    ]

    infofile = 'notebook_sharing.json'
    if os.path.exists(infofile):
        with open(infofile, 'r') as f:
            info = json.load(f)
    else:
        info = {}
    link_html = []
    # Upload all notebooks
    for notebook in notebooks_to_share:
        nbfile = os.path.join(notebook_dir, notebook)
        hash = hashlib.md5(open(nbfile,'rb').read()).hexdigest()
        if notebook in info and 'hash' in info[notebook]:
            link_html.append(f'<a href="{info[notebook]['url']}">{notebook}</a><p>')
            if info[notebook]['hash'] == hash:
                print("Current version of notebook %s already uploaded" % notebook)
                continue
        print("Uploading %s" % notebook)
        info[notebook] = {
            'url': run_shell_cmd(f"nbss-upload {nbfile}")[0][0],
            'hash': hash
        }
        link_html.append(f'<a href="{info[notebook]['url']}">{notebook}</a><p>')

    with open(infofile, 'w') as f:
            json.dump(info, f)

    index_stub = open('docs/index.html.stub', 'r').read()
    index_stub = index_stub.replace('LINKOMATIC', '\n'.join(link_html))

    # add readings to the end of index.html
    readings = pd.read_csv('docs/readings.txt', 
                           encoding='latin-1',
                           sep='\t')

    readings_html = '<h2>Readings</h2>'

    categories = readings['Category'].unique()
    for cat in categories:
        readings_html += f'<h3>{cat}</h3>\n'
        for i, row in readings[readings['Category'] == cat].iterrows():
            readings_html += f'<p><a href="{row["URL"]}">{row["Label"]}</a></p>\n'
    index_stub += readings_html

    with open('docs/index.html', 'w') as f:
        f.write(index_stub)
    if github_push:
        print("Pushing index.html to GitHub")
        run_shell_cmd("git add docs/index.html")
        run_shell_cmd("git commit -m'update index.html'")
        run_shell_cmd("git push")