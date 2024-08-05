# share notebooks using nbss-upload

import os
import sys
import json
from poldracklab.utils.run_shell_cmd import run_shell_cmd
import hashlib

if __name__ == "__main__":

    notebook_dir = 'notebooks'
    notebooks_to_share = [
        'data_setup_haxby.ipynb',
        'decoding_haxby.ipynb'
    ]

    infofile = 'notebook_sharing.json'
    if os.path.exists(infofile):
        with open(infofile, 'r') as f:
            info = json.load(f)
    else:
        info = {}

    # Upload all notebooks
    for notebook in notebooks_to_share:
        nbfile = os.path.join(notebook_dir, notebook)
        hash = hashlib.md5(open(nbfile,'rb').read()).hexdigest()
        if notebook in info and 'hash' in info[notebook]:
            if info[notebook]['hash'] == hash:
                print("Current version of notebook %s already uploaded" % notebook)
                continue
        print("Uploading %s" % notebook)
        info[notebook] = {
            'url': run_shell_cmd(f"nbss-upload {nbfile}")[0][0],
            'hash': hash
        }

    with open(infofile, 'w') as f:
            json.dump(info, f)

    with open('README.md', 'w') as f:
        f.write("""
### Materials for Russ's lectures at the 2024 Summer School on AI in Cognitive Neuroscience.
#### Haxby data setup and decoding notebooks:\n  
""")

        for notebook in notebooks_to_share:
            f.write(f"* [{notebook}]({info[notebook]['url']}) \n")

    print("Pushing README.md to GitHub")
    run_shell_cmd("git add README.md")
    run_shell_cmd("git commit -m 'update README.md'")
    run_shell_cmd("git push")