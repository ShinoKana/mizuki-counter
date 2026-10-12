# kana-counter: a Mizuki visitor counter

A cute visitor counter for GitHub profile READMEs and personal sites. Every digit
is held up by a pixel-art chibi **Akiyama Mizuki** (暁山瑞希) from *Project SEKAI*,
each one in a different pose.

<p align="center">
  <img alt="kana-counter demo" src="https://kana-counter.vercel.app/api/count?demo=1234567&label=1" width="600" />
</p>

GitHub プロフィールや個人サイト用のアクセスカウンターです。数字を一桁ずつ、ちびキャラの暁山瑞希が掲げます。

用于 GitHub 主页 README 和个人网站的访客计数器，每一位数字都由一个像素风 Q 版晓山瑞希举着。

## The ten poses

<p align="center">
  <img alt="digits 0 to 4" src="https://kana-counter.vercel.app/api/count?demo=01234" width="420" />
  <img alt="digits 5 to 9" src="https://kana-counter.vercel.app/api/count?demo=56789" width="420" />
</p>

- At least 5 digits are shown (`00042`); a sixth figure appears when the count reaches 100000, and so on.
- Light and dark versions, so the counter can follow the viewer's GitHub theme.
- Optional "Visitors" label on the left.
- Served as one self-contained SVG (sprites embedded), with no-cache headers so every page view is counted, also through GitHub's image proxy.

## Use it

The public instance at `kana-counter.vercel.app` keeps a counter only for its owner, so
**deploy your own copy first** (free, about two minutes):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FShinoKana%2Fkana-counter&project-name=kana-counter&repository-name=kana-counter&stores=%5B%7B%22type%22%3A%22integration%22%2C%22integrationSlug%22%3A%22upstash%22%2C%22productSlug%22%3A%22upstash-kv%22%7D%5D)

The button clones this repository and adds a free Upstash Redis database to store the
counts. Then put this in your README, with your own deployment URL and any name you like:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://YOUR-APP.vercel.app/@your-name?dark=1&label=1" />
  <img alt="visitor counter" src="https://YOUR-APP.vercel.app/@your-name?label=1" width="400" />
</picture>
```

or simply

```markdown
![visitor counter](https://YOUR-APP.vercel.app/@your-name)
```

`/@your-name` is short for `/api/count?name=your-name`.

### Parameters

| Parameter | Default | What it does |
|---|---|---|
| `name` (or the `/@name` path) | | Which counter to bump. 1 to 39 letters, digits, `.`, `_` or `-`. |
| `dark=1` | off | Slightly dimmer sprites and label colour for dark pages. |
| `label=1` | off | Writes "Visitors" to the left of the figures. |
| `digits` | `5` | Minimum number of digits (1 to 10); shorter counts get leading zeros. |
| `pad` | `0` | Transparent space on the right, in sprite pixels (one figure is 180 wide), for lining the image up with other blocks. |
| `peek=1` | off | Show the current count without adding a visit. |
| `demo=1234` | | Draw that number without touching the database (for previews like the ones above). |

### Settings for your deployment

| Environment variable | What it does |
|---|---|
| `KV_REST_API_URL`, `KV_REST_API_TOKEN` | Added automatically by the Upstash integration. `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` also work. |
| `ALLOWED_NAMES` | Optional, comma separated. Only these names are counted; others get a 403. Leave unset to count any name. |
| `COUNTER_START` | Optional, e.g. `your-name:4008`, to carry a count over from another counter. Applied once, on the first visit. |

If the database is briefly unreachable the counter still returns an image, showing the
last number it saw, so a README never shows a broken picture.

## About the art

- **Character:** Akiyama Mizuki (暁山瑞希), a member of *25-ji, Nightcord de.* (25時、ナイトコードで。)
  in *Project SEKAI COLORFUL STAGE! feat. Hatsune Miku*.
  © SEGA / © Colorful Palette Inc. / © Crypton Future Media, INC. www.piapro.net
- **Sprites:** an unofficial fan-made sprite sheet, generated with ChatGPT image generation
  from a prompt by [ShinoKana](https://github.com/ShinoKana) (the original sheet is
  [`themes/mizuki/sheet.png`](themes/mizuki/sheet.png)). The digits are drawn onto the blank
  cards afterwards in [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P).
- **"Visitors" label:** [Klee One](https://fonts.google.com/specimen/Klee+One) by Fontworks.

This project is not affiliated with or endorsed by SEGA, Colorful Palette or Crypton Future
Media. If you hold the rights and would like the artwork taken down, please open an issue
and it will be removed.

## Make a theme with your own character

[`docs/THEMES.md`](docs/THEMES.md) has the image prompt used for the Mizuki sheet and the
script that turns any 10-pose sheet into a theme: it finds each pose (they don't need to be
evenly spaced), writes the digits onto the cards, and lines the figures up.

## Licence

- Code: [MIT](LICENSE).
- Fonts: SIL Open Font License, see [`assets/fonts`](assets/fonts).
- Mizuki sprites: fan art of a character owned by SEGA / Colorful Palette. They are **not**
  covered by the MIT licence; use them for personal, non-commercial pages.
