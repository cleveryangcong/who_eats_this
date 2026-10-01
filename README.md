# Who eats this?

A small guessing game for the CDTM Fall 2026 class: you see a meal with the face blurred and pick which classmate is eating or cooking it.

## Folders

- `photos/` — the blurred pictures shown in the game (public).
- `originals/` — the same pictures without blur, only for matching names. Ignored by git, never uploaded.
- `data/` — `people.json` (class list) and `answers.json` (photo → person).
- `tools/` — the local page for matching photos to people.

## Match photos to people

```
python3 tools/label_server.py
```

Open http://localhost:8765/label and pick a name under each photo. Every change is saved to `data/answers.json`. Photos without a name, or set to "Leave out of the game", are not shown in the game. The game itself runs at http://localhost:8765/.

## Shared ranking (Supabase)

Create a free project on supabase.com, open the SQL editor and run:

```sql
create table scores (
  id bigint generated always as identity primary key,
  name text not null check (char_length(name) between 1 and 24),
  score int not null check (score >= 0),
  total int not null check (total > 0 and score <= total),
  seconds int not null check (seconds >= 0),
  created_at timestamptz not null default now()
);
alter table scores enable row level security;
create policy "anyone can read scores" on scores for select to anon using (true);
create policy "anyone can add a score" on scores for insert to anon with check (true);
```

Then put the project URL and the anon (publishable) key into `config.js`. With both empty the game works without a ranking.

## Good to know

- The first run on a device counts for the ranking; later runs are practice.
- The answers sit in `data/answers.json`, so anyone who looks at the page source can cheat. Fine for a fun game.
- Hosting: GitHub Pages from the `main` branch, root folder.
