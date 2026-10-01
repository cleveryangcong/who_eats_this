# Who eats this?

A small guessing game for the CDTM Fall 2026 class: you either see only the food and guess who eats it, or you see the person with the food covered and guess what it is. After each answer the full photo is shown.

## Folders

- `photos/question/` — what the player sees first: a food-only crop, or the photo with the food covered.
- `photos/reveal/` — the full photo shown after the answer.
- `originals/` — source pictures for the two folders above. Ignored by git.
- `data/` — `people.json` (class list), `answers.json` (photo → person), `rounds.json` (built, do not edit).
- `tools/` — the local page for matching photos to people, and the script that builds the questions.

## Match photos to people

```
python3 tools/label_server.py
```

Open http://localhost:8765/label and pick a name under each photo. Every change is saved to `data/answers.json`. Photos without a name, or set to "Leave out of the game", are not shown in the game. The game itself runs at http://localhost:8765/.

## Build the questions

```
python3 tools/build_rounds.py
```

The kind of question, the food label and the food box of each photo are set at the top of `tools/build_rounds.py`. Run it again after any change there or in `answers.json`.

## Good to know

- No names, no ranking, nothing is stored: each player just sees their own score at the end.
- The answers sit in `data/rounds.json`, so anyone who looks at the page source can cheat. Fine for a fun game.
- Hosting: GitHub Pages from the `main` branch, root folder.
