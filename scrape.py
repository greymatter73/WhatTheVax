import sys
import random
from datetime import datetime
import csv

from googlesearch import get_random_user_agent
from search_engines import *

# Minimum wait time between calling an engine for different searches (in
# seconds)
ENGINE_COOLDOWN_TIME = 5

# The number of pages worth of search results to consider from each search
# attempt.
SEARCH_PAGES = 1

search_engines = [
    Ask,
    Bing,
    Dogpile,
    Duckduckgo,
    # Google really really hates being scraped. You can uncomment it but even
    # with the search engine randomization and pacing their heuristics tend to
    # ban scapers really quickly.
    # Google,
    Mojeek,
    Startpage,
    Yahoo
]


def main():
    with open('county_list.csv', newline='') as f:
        r = csv.reader(f, delimiter=',')
        n = 0
        for row in r:
            n += 1
            if n > 10:
                break

            county, state = row[0], row[1]
            prush("{}, {}...".format(county, state))

            engine_times = dict()
            time_since_last_use = 0
            engine_name = ""
            while True:
                engine = random.choice(search_engines)()
                engine_name = engine.__class__.__name__
                if not engine_name in engine_times:
                    break
                time_since_last_use = (
                    datetime.now() - engine_times[engine_name]).total_seconds()
                if time_since_last_use < ENGINE_COOLDOWN_TIME:
                    prush("Engine '{}' used too recently. Trying another...".format(
                        engine_name))
                else:
                    break

            engine.set_headers({'User-Agent': get_random_user_agent()})
            # internally intepreted as sleep(random_uniform(*self._delay))
            # This value set low (or zero) since we pause between use of each
            # engine (above).
            engine._delay = (0, 0)

            subject = "site:gov {} County {} covid vaccine access".format(
                county, state)
            search_results = engine.search(subject, pages=SEARCH_PAGES).links()

            if len(search_results) == 0:
                subject = "{} County {} covid vaccine access".format(
                    county, state)
                search_results = engine.search(
                    subject, pages=SEARCH_PAGES).links()

            engine_times[engine_name] = datetime.now()

            title = "{} Search for '{}':".format(engine_name, subject)

            markdown = ""
            with open(state + "/" + county + ".md", "r") as county_file:
                markdown = county_file.read()

            if len(search_results) == 0 or search_results[0] in markdown:
                continue

            if len(markdown.strip()) == 0 or "no tips submitted for this location yet" in markdown.lower():
                markdown = "## Covid tips for {}, {}\n\n{}\n{}\n{}".format(
                    county, state, title, search_results[0], datetime.now())
            else:
                markdown = "{}\n\n{}\n{}\n{}".format(
                    markdown, title, search_results[0], datetime.now())

            with open(state + "/" + county + ".md", "w") as county_file:
                county_file.write(markdown)


def prush(*args):
    """prush is a print followed by a flush"""
    print(*args)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
