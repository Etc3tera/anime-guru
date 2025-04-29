import code
import requests
import json

from bs4 import BeautifulSoup

def __save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4))

def __get_page_id(anime_name: str):
    r = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&formatversion=2&srsearch={anime_name}")
    jd = r.json()
    if jd['query']['searchinfo']['totalhits'] <= 0:
        return None
    
    # write for debug
    __save_json("temp/wikipedia_search_result.json", jd)

    # get first matched page's ID
    return int(jd['query']['search'][0]['pageid'])

def __get_plot_section_id(page_id: int):
    r = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&format=json&pageid={page_id}&prop=sections")
    jd = r.json()
    plot_section = next((section for section in jd['parse']['sections'] if section['line'] == 'Plot'), None)

    if plot_section:
        return int(plot_section['index'])
    
    # write for debug
    __save_json("temp/wikipedia_sections_parse_result.json", jd)

    return None

def __get_intro_text(page_id: int):
    r = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&pageids={page_id}&format=json")
    jd = r.json()

    # write for debug
    __save_json("temp/wikipedia_intro_text.json", jd)

    return jd['query']['pages'][str(page_id)]['extract']

def __get_section_information(page_id: int, section_id: int):
    '''
    Use BeautifulSoup to extract information from HTML
    '''

    r = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&format=json&prop=text&pageid={page_id}&section={section_id}")

    with open("temp/wikipedia_section_content.html", 'w', encoding="utf-8") as f:
        jd = r.json()
        content = jd['parse']['text']['*']
        f.write(content)
        soup = BeautifulSoup(content, 'html.parser')

    # remove all superscript tag (Wikipedia Ref.)
    for sup in soup.find_all('sup'):
        sup.decompose()

    # find all contents
    all_contents = []

    for p in soup.find_all('p'):
        if len(p.find_all('code')) > 0:
            continue

        all_contents.append(p.get_text().strip())

    result = ''.join(all_contents)
    with open("temp/extracted_section_information.txt", "w", encoding="utf-8") as f:
        f.write(result)

    return result

def retrieve_anime_information(anime_name: str):
    page_id = __get_page_id(anime_name)
    if not page_id:
        return None
    
    plot_section_id = __get_plot_section_id(page_id)
    if not plot_section_id:
        return None
    
    intro_text = __get_intro_text(page_id)
    plot_text_content = __get_section_information(page_id, plot_section_id)

    anime_info = f"## Introduction\n{intro_text}"
    if plot_text_content:
        anime_info += f"\n\n## Plot\n{plot_text_content}"

    # write for debug
    with open("temp/anime_info.txt", "w", encoding="utf-8") as f:
        f.write(anime_info)
    
    return anime_info