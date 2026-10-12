# Making a theme

A theme is ten poses of one character, each holding a blank card, turned into the
digit sprites 0-9.

## 1. Draw the sheet

The Mizuki sheet came from ChatGPT image generation with a prompt along these lines.
Attach a reference picture of your character and fill in the brackets.

```
Sprite sheet for a website visitor counter.

CHARACTER: [character name, from WORK], [hair colour and style], [eye colour], [outfit].
Use the attached reference ONLY for her appearance — ignore its pose, framing and background.
Draw her as a cute chibi: about 2 heads tall, big head, small body, full body, standing.

LAYOUT (most important):
- One landscape image, 1536 x 1024.
- EXACTLY 10 copies of her in a 5 x 2 grid (5 columns, 2 rows), each copy the same size.
- Nothing touches the image edges or another copy; clear empty space around each one.
- 10 different poses and expressions. Same outfit and colours in all 10.

THE CARD:
- In every pose she holds ONE flat square card in front of her chest,
  facing the viewer straight on — NOT tilted, NOT angled, NOT in perspective.
- The card is plain off-white with a thin dark outline.
- THE CARD IS COMPLETELY BLANK: NO numbers, NO letters, NO text, NO drawings on it.

STYLE: clean pixel art with crisp edges, soft pastel colours.
BACKGROUND: transparent PNG.
NO text anywhere in the image. No watermark, no signature.
```

Leave the cards blank: image models often get digits wrong, so the script writes them.

## 2. Turn it into a theme

```sh
pip install pillow numpy scipy
python3 scripts/make_theme.py path/to/sheet.png --name yourtheme \
    --font assets/fonts/PressStart2P-Regular.ttf --digit-scale 0.62
```

The script

- finds the ten poses as separate regions of opaque pixels, so they don't have to sit on an
  even grid, and gives loose bits (sparkles, hearts, props) to the pose whose card is closest;
- finds each card as the most rectangular patch of near-colourless paper;
- writes the digit on the card in the outline colour (`--ink`, default a dark plum);
- places every pose on the same canvas, centred on its card and standing on one baseline.

It writes `themes/yourtheme.json`. Add it to the `themes` object at the top of
`lib/render.js`, and use it with `?theme=yourtheme`.
