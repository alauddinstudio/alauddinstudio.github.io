# alauddinstudio.com

Alauddin Studio-র পুরো ওয়েবসাইট এই একটা repo-তেই থাকে। এখানে push করলে GitHub Pages এক-দুই মিনিটে https://alauddinstudio.com আপডেট করে দেয়।

## তিনটা নিয়ম

1. **সাইটের সবকিছু শুধু এখানে বদলাবেন।** `cozy-idle-games` বা `alauddin-apps` repo-তে সাইটের কোনো কপি নেই, রাখবেনও না।
2. **গেম আর অ্যাপের পাতা হাতে লিখবেন না।** লেখা বদলাতে `data/games.json` বদলান, তারপর চালান:
   ```
   python3 tools/build.py
   ```
3. **কোনো পাতার ঠিকানা বদলাবেন না।** Play Console, AdMob আর গেমের কোডে এই ঠিকানাগুলোই বসানো আছে।

## কোন ফাইল কী কাজ করে

| ফাইল বা folder | কী | হাতে বদলানো যায়? |
|---|---|---|
| `data/games.json` | সব গেম আর অ্যাপের লেখা, অবস্থা, রঙ। গেমগুলো চালু হলে এটা পড়ে "More cozy games" তালিকা দেখায় | হ্যাঁ, সব বদল এখান থেকে শুরু |
| `tools/build.py` | `games.json` থেকে সব পাতা বানায় | শুধু নকশা বদলাতে |
| `index.html`, `games/`, `honeybee/`, `bakery/`, `flower/`, `petsalon/`, `sheep/`, `wooltree/`, `leafcure/index.html`, `paincast/index.html`, `robots.txt`, `sitemap.xml` | build-এর বানানো পাতা | না, পরের build মুছে দেয় |
| `honey-bee/`, `cozy-bakery/`, `flower-shop/`, `pet-salon/`, `sheep-merge/`, root-এর `privacy.html` আর `support.html` (Wool Tree) | গেমের Privacy আর Support | হ্যাঁ, হাতে লেখা |
| `leafcure/privacy.html`, `paincast/privacy.html` | অ্যাপের Privacy | হ্যাঁ, হাতে লেখা |
| `assets/` | নকশা (`style.css`, `app.js`), লোগো, গেমের আইকন, screenshot, ভিডিও | হ্যাঁ। তবে `assets/icons/` আর `assets/shots/`-এর ফাইলের নাম বদলাবেন না, গেমগুলো এই নামেই ছবি আনে |
| `app-ads.txt` | AdMob-এর ফাইল | না, root-এই থাকতে হবে |
| `CNAME` | domain `alauddinstudio.com` | না |
| `google*.html` | Search Console-এর যাচাই | না, মুছলে যাচাই বাতিল হয় |
| `.nojekyll` | GitHub-কে ফাইল যেমন আছে তেমন দেখাতে বলে | না |

## বিস্তারিত

পুরো গাইড (কোন পাতায় কী আছে, গেম live করা, নতুন গেম বা অ্যাপ যোগ করা, domain আর account-এর তথ্য) আছে `cozy-idle-games` repo-র [`docs/cozyidle_website.md`](https://github.com/Alauddinahmed9282/cozy-idle-games/blob/main/docs/cozyidle_website.md)-এ।
