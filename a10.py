import re
import wikipedia
from wikipedia import WikipediaPage
from bs4 import BeautifulSoup
import string
from typing import Match


# Helper Functions for World Records

def get_page_html(title: str) -> str:
    """Gets the HTML content of a Wikipedia page."""
    try:
        page = wikipedia.page(title, auto_suggest=False)
        return page.content
    except wikipedia.exceptions.DisambiguationError as e:
        raise ValueError(f"DisambiguationError: Multiple pages found, please be more specific. Options: {e.options}")
    except wikipedia.exceptions.HTTPTimeoutError:
        raise ConnectionError("HTTP timeout occurred while fetching the page.")
    except wikipedia.exceptions.RedirectError:
        raise ValueError(f"Redirect error occurred for page: {title}")
    except wikipedia.exceptions.PageError:
        raise ValueError(f"Page not found for {title}")


def get_first_infobox_text(html: str) -> str:
    """Gets first infobox html from a Wikipedia page (summary box)


    Args:
        html - the full html of the page


    Returns:
        html of just the first infobox
    """
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")


    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text

def clean_text(text: str) -> str:
    """Cleans given text by removing non-ASCII characters and duplicate spaces & newlines."""
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines


def get_match(text: str, pattern: str, error_text: str = "Page doesn't appear to have the property you're expecting") -> Match:
    """Finds regex matches for a pattern."""
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)
    if not match:
        raise AttributeError(error_text)
    return match


# Refactored Action Functions for World Record Queries

def get_fastest_time(planet_name: str) -> str:
    """Gets the fastest time record from the Wikipedia page's infobox."""
    infobox_text = clean_text(get_first_infobox_text(get_page_html(planet_name)))
    pattern = r"(?:Fastest time.*?)(?: ?[\d]+ )?(?P<fastest_time>[\d:.]+)(?:.*?)s"
    error_text = "Page infobox has no fastest time information"
    match = get_match(infobox_text, pattern, error_text)
    fastest_time_info = f"the fastest time in {planet_name} is {match.group('fastest_time')} seconds"
    return fastest_time_info


def get_highest_score(planet_name: str) -> str:
    """Gets the highest score record from the Wikipedia page's infobox."""
    infobox_text = clean_text(get_first_infobox_text(get_page_html(planet_name)))
    pattern = r"(?:Highest score.*?)(?: ?[\d]+ )?(?P<highest_score>[\d,]+)(?:.*?)points"
    error_text = "Page infobox has no highest score information"
    match = get_match(infobox_text, pattern, error_text)
    highest_score_info = f"the highest score in {planet_name} is {match.group('highest_score')} points"
    return highest_score_info


def get_longest_distance(planet_name: str) -> str:
    """Gets the longest distance record from the Wikipedia page's infobox."""
    infobox_text = clean_text(get_first_infobox_text(get_page_html(planet_name)))
    pattern = r"(?:Longest distance.*?)(?: ?[\d]+ )?(?P<longest_distance>[\d,.]+)(?:.*?)km"
    error_text = "Page infobox has no longest distance information"
    match = get_match(infobox_text, pattern, error_text)
    longest_distance_info = f"the longest distance in {planet_name} is {match.group('longest_distance')} km"
    return longest_distance_info


# Patterns for World Record Queries

pa_list = [
    (r'What is the fastest time for (.*)\?', get_fastest_time),
    (r'Who holds the record for the fastest time in (.*)\?', get_fastest_time),
    (r'What is the highest score in (.*)\?', get_highest_score),
    (r'Who has the highest score in (.*)\?', get_highest_score),
    (r'What is the longest distance in (.*)\?', get_longest_distance),
    (r'Who holds the record for the longest distance in (.*)\?', get_longest_distance),
]


# Function to process user input and respond based on pattern matching
def process_query(query: str) -> str:
    """Process a user query and return the answer if a match is found."""
    for pattern, action in pa_list:
        match_result = re.search(pattern, query)
        if match_result:
            return action(match_result.group(1))
    return "Sorry, I don't have an answer for that query."


# Interactive user input
def interactive_query():
    """Interactively prompt the user for queries and return answers."""
    print("Welcome to the World Records Query Bot!")
    print("You can ask about world records, such as fastest times, highest scores, and longest distances.")
    print("Type 'exit' to quit the program.")
    
    while True:
        query = input("\nPlease enter your query: ")
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        
        answer = process_query(query)
        print(f"Answer: {answer}")


# Run the interactive query function
interactive_query()