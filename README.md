# Web Scraping Practice

This project covers: reproducing the Oxylabs web scraping tutorial, improving its code, and scraping two real websites that were not designed for scraping (IMDb Top 250 and the 2026 FOMC statements from the Federal Reserve). I also worked through the Real Python examples (urllib, regex, BeautifulSoup, MechanicalSoup, the dice page) as a warm-up. They are not included here.

Each part is a Jupyter notebook. The results are saved as CSV files.

## Project structure

```
reproduction/      Oxylabs tutorial + improved version
  oxylabs_reproduction.ipynb
  products_10pages.csv          raw data, 320 products
  products_10pages_clean.csv    cleaned data
realworld/         IMDb Top 250
  imdb_top250.ipynb
  imdb_top250.csv
realworld-2/       FOMC 2026 statements
  fomc2026.ipynb
  fomc_2026_votes.csv
requirements.txt
```

---

## 1. Oxylabs tutorial: reproduce and improve

**What I did:** Ran the tutorial code on `sandbox.oxylabs.io`, then changed it to get more fields and more pages.

**Challenges and fixes:**

- **The blog-title example no longer works.** The tutorial selects titles by the class `e1dscegp1`. The page loads fine (status 200), but that class isn't in the HTML anymore, so all four methods (BeautifulSoup, select, lxml, Selenium) return 0 results. It's an auto-generated class name that changed when the site was updated. For the product cards I used readable class names like `title` and `price-wrapper` instead.
- **Names and prices were stored in two separate lists.** If one product were missing a price, the lists would no longer line up. I changed it so each product card becomes one dict.
- **requests vs Selenium.** requests found the same 32 product cards and was about 4× faster per page. But a range check later showed every rating was 0: the stars are drawn by JavaScript, so requests can't see them. I switched pagination to Selenium (one browser for all 10 pages).

**Result:** 320 products from 10 pages, 8 fields (id, title, categories, rating, description, price, price as a number, URL).

**Cleaning:** No duplicates. Removed line breaks from descriptions and stray "-" from titles. All prices converted to numbers (33.99 to 92.99 €). Ratings are 4 - 5.


---

## 2. IMDb Top 250

**What I did:** Scraped the IMDb Top 250 movies chart.

**Challenges and fixes:**

- **IMDb blocks scrapers.** A normal User-Agent header didn't help: `requests` got status 202 and an empty page. The response header `x-amzn-waf-action: challenge` shows the page is protected by AWS WAF, which sends a JavaScript check that requests can't run.
- **CAPTCHA.** I switched to Selenium. IMDb still showed an image CAPTCHA, which I had to solve it manually. 
- **Outdated selectors.** Even with the full page loaded, I found 0 movies. Movie titles are no longer in `h3.ipc-title__text`. I saved the HTML and found a JSON-LD block with all 250 movies, so I parsed that instead. It's simpler and more stable than HTML class names.

**Result:** 250 movies, 8 fields (rank, title, rating, votes, genre, content rating, duration in minutes, URL).

**Data notes:** 6 movies have no content rating. They are all non-US movies, which likely never got a US rating, so I kept them as missing. 

<img width="1712" height="842" alt="265e84a0-4550-4a60-842d-caae041d9e3d" src="https://github.com/user-attachments/assets/dfa9ab21-69dc-4eb3-9ea3-49f02e348fc7" />

---

## 3. FOMC 2026 statements: votes and dissents

**What I did:** Collected the 6 FOMC statements released in 2026 and extracted the vote result for each meeting. This dataset is text, not a table, so the work was turning sentences into fields.

**Approach:**

1. Found the 6 statement links on the FOMC calendar page by matching URLs like `monetary2026XXXXa.htm`.
2. Used Chrome-Inspect to find where the text is: inside `div#article`, as plain `<p>` tags.
3. Saved all 6 pages once, so I didn't re-request them while testing.

**Challenges and fixes:**

- **Garbled text.** `3-1/2` showed up as `3â1/2`, and some words were stuck together (`ESTShare`). Fixed by forcing UTF-8 and using `get_text(" ")`.
- **My first parser crashed.** I assumed every statement used the same format because the first one did. The format changed in June: "Voting for ..." disappeared and a vote tally ("by a 12 - 0 vote") appeared at the top. To see every way voting is written, I searched all paragraphs for "vot" and built two rules, one per format.
- **April had two groups of dissenters** with different reasons. My first version only caught one of them. I found it by reading all the vote paragraphs.

**Result:**

| Meeting | Vote | Voting against |
|---|---|---|
| Jan 28 | 10-2 | Miran, Waller |
| Mar 18 | 11-1 | Miran |
| Apr 29 | 8-4 | Miran, Hammack, Kashkari, Logan |
| Jun 17 | 12-0 | none |
| Jul 29 | 9-3 | Hammack, Kashkari, Logan |
| Sep 16 | 12-0 | none |

**Finding:** From January to April, Miran dissented each time, wanting a rate cut. In April, Hammack, Kashkari and Logan also dissented, objecting to the statement's easing bias. In July the same three dissented again, this time wanting a rate hike. In September the committee raised rates by 1/4 point, and the vote was unanimous.

<img width="1718" height="1066" alt="fa78035f-af31-4bee-a7ae-227f233ba87a" src="https://github.com/user-attachments/assets/6139a267-ed53-414d-a639-7aece19afed6" />

---

## 4. Code improvements

| Problem | What I changed |
|---|---|
| Missing elements crash the code (`.text` on `None`) | Helper returns `None` instead of crashing; `.get()` for JSON |
| Parallel lists can misalign | One dict per item |
| Requests can hang | `timeout=10` on every request |
| One bad page stops the whole loop | `try/except` per page |
| Browser left open | `try/finally` with `driver.quit()` |
| Prices and durations are text | Converted to numbers |
| Re-requesting pages while testing | Saved pages once and parsed from memory (FOMC) |
| Hashed class names break | Used readable class names, IDs, or JSON-LD instead |


## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then open any notebook and choose the `.venv` kernel. The Oxylabs and IMDb notebooks open Chrome through Selenium, and IMDb may ask you to solve a CAPTCHA.
