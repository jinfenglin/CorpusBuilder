from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import jsonlines
import argparse
import time
from tqdm import tqdm


def get_definition(driver, mag_url):
    driver.get(mag_url)
    html = None

    w = WebDriverWait(driver, 8)
    w.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    print("Page load happened")
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    try:
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
    except:
        return "-1"


def get_defs_for_all_concepts(concepts, out_path):
    """
    Process the concepts one by one
    """
    count_all = len(concepts)
    with jsonlines.open(out_path, "w") as fout:
        driver = webdriver.Chrome("./webdriver/chromedriver_win64.exe")
        count = 0
        for cid in tqdm(concepts):
            count += 1
            if count % 20 == 0:
                print(cid)
                time.sleep(100)
            url = f"https://academic.microsoft.com/topic/{cid}/publication"
            def_str = ""
            try:
                def_str = get_definition(driver, url)
            finally:
                fout.write({"id": cid, "concept": concepts[cid], "definition": def_str})
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept_file", default="./data/computer_science_jinfeng.terms")
    parser.add_argument("--out_path", default="./data/concept_definition.jsonl")
    args = parser.parse_args()
    concepts = dict()
    with open(args.concept_file) as fin:
        for line in fin:
            cid, cpt = line.strip("\n\t\r ").split("\t")[:2]
            concepts[cid] = cpt
    get_defs_for_all_concepts(concepts, out_path=args.out_path)
