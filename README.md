# alauddinstudio.com

The whole Alauddin Studio website lives in this one repo. When you push here, GitHub Pages updates https://alauddinstudio.com within a minute or two.

## Three rules

1. **Change the site only here.** The `cozy-idle-games` and `alauddin-apps` repos hold no copy of the site, and should not.
2. **Don't hand-edit the game and app pages.** To change their text, edit `data/games.json`, then run:
   ```
   python3 tools/build.py
   ```
3. **Never change a page's address.** These addresses are set in Play Console, AdMob and the game code.

## What each file does

| File or folder | What it is | Edit by hand? |
|---|---|---|
| `data/games.json` | Text, status and colors for every game and app. The games read it at launch to show the "More cozy games" list | Yes, every change starts here |
| `tools/build.py` | Builds all pages from `games.json` | Only to change the design |
| `index.html`, `games/`, `honeybee/`, `bakery/`, `flower/`, `petsalon/`, `sheep/`, `wooltree/`, `leafcure/index.html`, `paincast/index.html`, `kinring/index.html`, `robots.txt`, `sitemap.xml` | Pages made by the build | No, the next build overwrites them |
| `honey-bee/`, `cozy-bakery/`, `flower-shop/`, `pet-salon/`, `sheep-merge/`, and the root `privacy.html` and `support.html` (Wool Tree) | Game Privacy and Support pages. Each folder's `index.html` just sends visitors to `support.html`, because the games link to addresses like `alauddinstudio.com/pet-salon` | Yes, hand-written |
| `leafcure/privacy.html`, `paincast/privacy.html`, `kinring/privacy.html` | App Privacy pages | Yes, hand-written |
| `assets/` | Design (`style.css`, `app.js`), logo, game icons, screenshots, videos | Yes. But don't rename files in `assets/icons/` or `assets/shots/`, the games load images by these names |
| `app-ads.txt` | AdMob file | No, it must stay at the root |
| `CNAME` | The `alauddinstudio.com` domain | No |
| `google*.html` | Search Console verification | No, deleting them cancels verification |
| `.nojekyll` | Tells GitHub to serve files exactly as they are | No |

## More details

- Day-to-day guide (what each page holds, taking a game live, adding a new game or app, domain and accounts): [`docs/cozyidle_website.md`](https://github.com/Alauddinahmed9282/cozy-idle-games/blob/main/docs/cozyidle_website.md) in the `cozy-idle-games` repo.
- Architecture (what each repo does, what changed on 2026-11-02): [`docs/common/website_architecture.md`](https://github.com/Alauddinahmed9282/cozy-idle-games/blob/main/docs/common/website_architecture.md). The same file is also in `alauddin-apps/docs/common/`.
