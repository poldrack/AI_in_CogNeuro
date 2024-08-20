create:
	$ micromamba create -f env.yml
	micromamba aineuro xai pip install -r requirements.txt

share-notebooks:
	python scripts/share_notebooks.py


render-talk:
	-git rm -rf docs/talk/*
	cd talk-AIAssistedCoding && quarto render talk.qmd

push-talk:
	-git add docs/talk/*
	-git add docs/talk/images/*
	-git add talk/talk.qmd
	-git add talk/images/*
	git commit -a -m"updating changed files"
	git push origin main

