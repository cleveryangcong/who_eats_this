"""Build the game pictures and data/rounds.json from originals/ and data/answers.json.

Run after changing a name, a food label or a box: python3 tools/build_rounds.py

Two kinds of rounds:
  who  - the player sees only the food (a crop) and guesses the person.
  what - the player sees the person with the food covered and guesses the food.
Boxes are (left, top, right, bottom) as fractions of the picture.
"""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ORIGINALS = ROOT / "originals"
QUESTION = ROOT / "photos" / "question"
REVEAL = ROOT / "photos" / "reveal"

# file: (kind, food label, food group, boxes). "who" uses the first box as the crop.
ROUNDS = {
    "2026-08-28_12-25-34.jpg": ("what", "Plain mozzarella balls", "mozzarella", [(0.30, 0.61, 0.80, 0.90)]),
    "2026-08-31_13-51-45.jpg": ("what", "Crisps with sliced turkey from the pack", "turkey", [(0.12, 0.18, 0.42, 0.40), (0.22, 0.74, 0.72, 1.0)]),
    "2026-09-01_13-21-13.jpg": ("who", "Plain mozzarella balls", "mozzarella", [(0.15, 0.56, 0.72, 0.80)]),
    "2026-09-02_20-03-00.jpg": ("what", "A steak, pan-fried", "steak", [(0.0, 0.66, 0.46, 0.88)]),
    "2026-09-04_14-56-38.jpg": ("who", "Porridge out of a plastic box", "porridge", [(0.28, 0.76, 0.68, 1.0)]),
    "2026-09-07_13-08-54.jpg": ("what", "Steamed broccoli, nothing else", "broccoli", [(0.62, 0.80, 1.0, 1.0)]),
    "2026-09-08_12-45-21.jpg": ("who", "Döner in bread", "doner", [(0.12, 0.70, 0.72, 1.0)]),
    "2026-09-09_11-28-26.jpg": ("what", "A wrap standing upright", "wrap", [(0.10, 0.48, 0.42, 0.90)]),
    "2026-09-09_15-51-33.jpg": ("who", "Chicken from the pan", "chicken", [(0.56, 0.66, 1.0, 0.88)]),
    "2026-09-09_18-10-51.jpg": ("what", "Skyr with blueberries", "skyr", [(0.0, 0.66, 0.62, 1.0)]),
    "2026-09-11_11-03-09.jpg": ("who", "A plate of white cheese", "mozzarella", [(0.28, 0.54, 0.68, 0.74)]),
    "2026-09-11_15-00-09.jpg": ("what", "Lasagne in baking paper", "lasagne", [(0.36, 0.68, 1.0, 1.0), (0.48, 0.50, 0.74, 0.62)]),
    "2026-09-11_20-34-23.jpg": ("what", "A burger", "burger", [(0.07, 0.54, 0.29, 0.73)]),
    "2026-09-14_12-43-58.jpg": ("what", "Noodles with yoghurt and tomato sauce", "noodles", [(0.12, 0.62, 0.84, 0.92)]),
    "2026-09-15_14-41-14.jpg": ("who", "Two ham and cheese rolls", "rolls", [(0.18, 0.46, 0.78, 0.72)]),
    "2026-09-17_12-34-27.jpg": ("who", "The last bite of a döner", "doner", [(0.28, 0.38, 0.84, 0.60)]),
    "2026-09-22_13-05-20.jpg": ("who", "Wrap with salad and tomato", "wrap", [(0.36, 0.52, 0.94, 0.82)]),
    "2026-09-22_13-13-18.jpg": ("what", "A big bowl of salad", "salad", [(0.30, 0.36, 0.76, 0.58)]),
    "2026-09-22_21-29-09.jpg": ("who", "Almond cream cake", "cake", [(0.02, 0.18, 1.0, 0.82)]),
    "2026-09-23_18-39-01.jpg": ("what", "Schnitzel", "schnitzel", [(0.30, 0.66, 0.94, 1.0)]),
}

# Wrong food answers that nobody in the game actually ate.
DECOY_FOODS = [
    "Plain rice with ketchup", "Tuna straight from the can", "A whole cucumber", "Butterbrezel",
    "Instant ramen", "Cold pizza from yesterday", "Protein shake and a banana", "Leberkässemmel",
    "Avocado toast", "Currywurst", "Hummus with carrots", "Kaiserschmarrn",
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


def main():
    answers = json.loads((ROOT / "data" / "answers.json").read_text())
    for folder in (QUESTION, REVEAL):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
    rounds = []
    for file, (kind, food, group, boxes) in ROUNDS.items():
        person = answers.get(file, "")
        if not person or person == "skip":
            continue
        original = Image.open(ORIGINALS / file).convert("RGB")
        original.save(REVEAL / file, quality=82)
        if kind == "who":
            question = original.crop(pixels(original, boxes[0]))
            if question.width < 900:
                scale = 900 / question.width
                question = question.resize((900, int(question.height * scale)), Image.LANCZOS)
        else:
            question = original.copy()
            for box in boxes:
                cover(question, box)
        question.save(QUESTION / file, quality=82)
        rounds.append({"file": file, "kind": kind, "person": person, "food": food, "group": group})
    data = {"rounds": rounds, "decoyFoods": DECOY_FOODS}
    (ROOT / "data" / "rounds.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(rounds)} rounds built")


if __name__ == "__main__":
    main()
