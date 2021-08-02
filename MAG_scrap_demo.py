from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import jsonlines
import argparse


def get_definition(driver, mag_url):
    driver.get(mag_url)
    html = None

    w = WebDriverWait(driver, 8)
    w.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    print("Page load happened")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    definitions = [
        x.get_text()
        for x in soup.find("div", class_="name-section").find_all(
            "p", text=True, recursive=False
        )
    ]
    if len(definitions) == 1:
        return definitions[0]
    else:
        return "-1"


def get_defs_for_all_concepts(concepts, out_path):
    """
    Process the concepts one by one
    """
    with jsonlines.open(out_path, "w") as fout:
        driver = webdriver.Chrome("./webdriver/chromedriver_win64.exe")
        for cid in concepts:
            url = f"https://academic.microsoft.com/topic/{cid}/publication"
            def_str = ""
            try:
                def_str = get_definition(driver, url)
            finally:
                fout.write({"id": cid, "concept": concepts[cid], "definition": def_str})
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept_file")
    parser.add_argument("--out_path", default="./data/concept_definition.jsonl")
    args = parser.parse_args()
    concepts = dict()
    with open(args.concept_file) as fin:
        for line in fin:
            cid, cpt = line.strip("\n\t\r ").split(",")[:2]
            concepts[cid] = cpt
    print(concepts)
    get_defs_for_all_concepts(concepts, out_path=args.out_path)
