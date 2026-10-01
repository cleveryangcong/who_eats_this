"""Build the game pictures and data/rounds.json from originals/ and data/answers.json.

Run after changing a name, a text or a box: python3 tools/build_rounds.py

Two kinds of rounds:
  who  - the player guesses a person (four names).
  what - the player guesses the food or drink (four texts).
How the question picture is made from the original:
  crop  - only the first box is shown (food without the person).
  cover - the boxes are hidden behind a dark "?" card.
  blur  - the boxes are blurred (name tags, a face).
  plain - the picture is shown as it is.
Boxes are (left, top, right, bottom) as fractions of the picture.
The person comes from data/answers.json; a round whose picture is set to "skip" there is left out.
"""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ORIGINALS = ROOT / "originals"
QUESTION = ROOT / "photos" / "question"
REVEAL = ROOT / "photos" / "reveal"

BREAKFAST = "Whose breakfast is this?"

# Optional keys: question, solution, group (no two options of the same group),
# decoys (fixed wrong answers), reveal (a different picture shown after the answer).
ROUNDS = [
    # Sina
    dict(file="2026-08-28_12-25-34.jpg", kind="what", make="cover", group="mozzarella",
         answer="Three plain mozzarella balls, nothing else", boxes=[(0.30, 0.61, 0.80, 0.90)]),
    dict(file="2026-08-31_13-51-45.jpg", kind="what", make="cover", group="turkey",
         answer="Sliced turkey breast straight from the pack, no bread",
         boxes=[(0.12, 0.18, 0.42, 0.40), (0.22, 0.74, 0.72, 1.0)]),
    dict(file="2026-09-01_13-21-13.jpg", kind="who", make="crop", group="mozzarella",
         answer="Plain mozzarella balls, again", boxes=[(0.15, 0.56, 0.72, 0.80)]),
    dict(file="2026-09-09_11-28-26.jpg", kind="what", make="cover", group="doner",
         answer="A Dürüm, standing upright like a trophy", boxes=[(0.10, 0.48, 0.42, 0.90)]),
    dict(file="2026-09-09_18-10-51.jpg", kind="what", make="cover", group="skyr",
         answer="A big bowl of Skyr with blueberries", boxes=[(0.0, 0.66, 0.62, 1.0)]),
    dict(file="2026-09-11_11-03-09.jpg", kind="who", make="crop", group="harzer",
         answer="Harzer Käse, plain, in the courtyard", boxes=[(0.28, 0.54, 0.68, 0.74)]),
    dict(file="2026-09-14_12-43-58.jpg", kind="what", make="cover", group="rice",
         answer="Meat with black rice, and she left all the rice", boxes=[(0.12, 0.62, 0.84, 0.92)]),
    # Fritz
    dict(file="2026-09-02_20-03-00.jpg", kind="what", make="cover", group="steak",
         answer="A steak fried on the office hot plate", boxes=[(0.0, 0.66, 0.46, 0.88)]),
    dict(file="2026-09-07_13-08-54.jpg", kind="what", make="cover", group="broccoli",
         answer="A pan of steamed broccoli, nothing else", boxes=[(0.62, 0.80, 1.0, 1.0)]),
    dict(file="2026-09-08_12-45-21.jpg", kind="who", make="crop", group="doner",
         answer="A fully loaded Döner", boxes=[(0.12, 0.70, 0.72, 1.0)]),
    dict(file="2026-09-09_15-51-33.jpg", kind="who", make="crop", group="chicken",
         answer="Chicken breast from the office pan", boxes=[(0.56, 0.66, 1.0, 0.88)]),
    dict(file="2026-09-11_15-00-09.jpg", kind="what", make="cover", group="salmon",
         answer="Air-fried salmon, eaten out of the baking paper",
         boxes=[(0.36, 0.68, 1.0, 1.0), (0.48, 0.50, 0.74, 0.62)]),
    dict(file="2026-09-17_12-34-27.jpg", kind="who", make="crop", group="doner",
         answer="The last bite of a Döner, wrapper already empty", boxes=[(0.28, 0.38, 0.84, 0.60)]),
    dict(file="2026-09-23_18-39-01.jpg", kind="what", make="cover", group="schnitzel",
         answer="Homemade Schnitzel from the office pan", boxes=[(0.30, 0.66, 0.94, 1.0)]),
    # Everyone else
    dict(file="2026-09-04_14-56-38.jpg", kind="who", make="crop", group="porridge",
         answer="Porridge straight from the Tupperware", boxes=[(0.28, 0.76, 0.68, 1.0)]),
    dict(file="2026-09-15_14-41-14.jpg", kind="who", make="crop", group="rolls",
         answer="Two fully loaded ham and cheese rolls", boxes=[(0.18, 0.46, 0.78, 0.72)]),
    dict(file="2026-09-22_13-05-20.jpg", kind="who", make="crop", group="wrap",
         answer="A falling-apart wrap with lettuce and tomato", boxes=[(0.36, 0.52, 0.94, 0.82)]),
    dict(file="2026-09-22_13-13-18.jpg", kind="what", make="cover", group="salad",
         answer="A big bowl of microwaved iceberg lettuce, nothing else", boxes=[(0.30, 0.36, 0.76, 0.58)]),
    dict(file="2026-09-22_21-29-09.jpg", kind="who", make="crop", group="cake",
         answer="A homemade almond cream cake", boxes=[(0.02, 0.18, 1.0, 0.82)]),
    dict(file="suit_burger.jpg", kind="what", make="cover", group="burger",
         answer="A plant-based Whopper from Burger King", boxes=[(0.15, 0.66, 0.46, 0.80)],
         decoys=["A vegan Döner with extra onions", "A tofu sandwich from the Mensa", "A soy Schnitzel in a Semmel"]),
    # Breakfasts, drinks and other mysteries
    dict(file="desk_red_bull.jpg", kind="who", make="blur", question=BREAKFAST,
         answer="Two Red Bulls, a Coke Light and a shaker", boxes=[(0.27, 0.76, 0.62, 0.88)]),
    dict(file="desk_pepsi.jpg", kind="who", make="blur", question=BREAKFAST,
         answer="A big bottle of Pepsi Zero and chewing gum",
         boxes=[(0.50, 0.62, 0.85, 0.69), (0.0, 0.085, 0.18, 0.15), (0.68, 0.035, 0.89, 0.105), (0.50, 0.05, 0.61, 0.12)]),
    dict(file="five_am_before.jpg", kind="what", make="cover", reveal="five_am_after.jpg",
         question="What are these two maniacs drinking at 5 am in the morning?",
         answer="Red Bull", solution="Red Bull. At 5 am.", boxes=[(0.31, 0.60, 0.61, 0.87)],
         decoys=["Chamomile tea", "Jägermeister shots", "Warm beer from the leftover crate"]),
    dict(file="six_am_bottle.jpg", kind="what", make="cover",
         question="What is he drinking at 6 am in the morning, with no place to go but to bed afterwards?",
         answer="A beer", solution="A beer. At 6 am. Then bed.", boxes=[(0.21, 0.42, 0.42, 0.86)],
         decoys=["Orange juice, like an adult", "A coffee to start the day", "A glass of milk"]),
    dict(file="five_glasses.jpg", kind="who", make="plain", reveal="five_glasses_after.jpg",
         question="Who are these beautiful five apes waiting for?", solution="They are waiting for {person}."),
    dict(file="tv_before.jpg", kind="who", make="plain", reveal="tv_after.jpg",
         question="Who is waiting behind this TV?", solution="It is {person}."),
    dict(file="burger_king.jpg", kind="who", make="blur",
         question="Who is ordering something at Burger King?", solution="It is {person}.",
         boxes=[(0.41, 0.34, 0.53, 0.43)]),
]

# Wrong food answers that nobody in the game actually ate.
DECOY_FOODS = [
    "Plain rice with ketchup", "Tuna straight from the can", "A whole cucumber, unpeeled", "A dry Butterbreze",
    "Instant ramen, eaten out of the pot", "Cold pizza from yesterday", "A protein shake and a banana",
    "A Leberkässemmel with too much mustard", "Toast with nothing on it", "A Currywurst from the Mensa",
    "Hummus with one sad carrot", "Kaiserschmarrn for one",
]


def pixels(im, box):
    w, h = im.size
    return (int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h))


def cover(im, box):
    x0, y0, x1, y1 = pixels(im, box)
    draw = ImageDraw.Draw(im)
    radius = min(x1 - x0, y1 - y0) // 8
    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=(35, 32, 27))
    size = int(min(x1 - x0, y1 - y0) * 0.6)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except OSError:
        font = ImageFont.load_default()
    draw.text(((x0 + x1) / 2, (y0 + y1) / 2), "?", fill=(246, 241, 231), font=font, anchor="mm")


def blur(im, box):
    region_box = pixels(im, box)
    region = im.crop(region_box)
    tiny = region.resize((max(1, region.width // 24), max(1, region.height // 24)), Image.BILINEAR)
    region = tiny.resize(region.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(region.size) / 12))
    im.paste(region, region_box[:2])


def question_picture(original, make, boxes):
    if make == "crop":
        picture = original.crop(pixels(original, boxes[0]))
        if picture.width < 900:
            picture = picture.resize((900, int(picture.height * 900 / picture.width)), Image.LANCZOS)
        return picture
    picture = original.copy()
    for box in boxes:
        if make == "cover":
            cover(picture, box)
        elif make == "blur":
            blur(picture, box)
    return picture


def main():
    answers = json.loads((ROOT / "data" / "answers.json").read_text())
    for folder in (QUESTION, REVEAL):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
    rounds = []
    for r in ROUNDS:
        file, kind = r["file"], r["kind"]
        person = answers.get(file, "")
        if person == "skip":
            continue
        if kind == "who" and not person:
            raise SystemExit(f"{file}: a 'who' round needs a person in data/answers.json")
        original = Image.open(ORIGINALS / file).convert("RGB")
        question_picture(original, r["make"], r.get("boxes", [])).save(QUESTION / file, quality=82)
        reveal = r.get("reveal", file)
        Image.open(ORIGINALS / reveal).convert("RGB").save(REVEAL / reveal, quality=82)

        first_name = person.split(" ")[0]
        if kind == "who":
            question = r.get("question", "Whose food is this?")
            default_solution = "{person}: " + r["answer"] + "." if "answer" in r else "{person}."
        else:
            question = r.get("question", f"What is {first_name} eating here?")
            default_solution = "{person}: " + r["answer"] + "." if person else r["answer"] + "."
        rounds.append({
            "file": file, "reveal": reveal, "kind": kind, "question": question,
            "answer": person if kind == "who" else r["answer"],
            "solution": r.get("solution", default_solution).format(person=person),
            "group": r.get("group", file), "decoys": r.get("decoys", []),
        })
    data = {"rounds": rounds, "decoyFoods": DECOY_FOODS}
    (ROOT / "data" / "rounds.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(rounds)} rounds built")


if __name__ == "__main__":
    main()
