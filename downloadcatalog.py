import requests
from bs4 import BeautifulSoup
import csv

import requests
from bs4 import BeautifulSoup
import csv

def get_page(url):
    """ Fetch the web page and return a BeautifulSoup object. """
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print("Failed to retrieve the webpage:", response.status_code)
        return None

def get_department_urls(base_url):
    """ Fetch the main catalog page and extract department URLs. """
    catalog_page = base_url + "/thecollege/programsofstudy/"
    soup = get_page(catalog_page)
    if not soup:
        return []
    
    department_links = []
    # Select links from the Program of Study section
    for link in soup.select('ul.nav.leveltwo li a'):
        href = link.get('href')
        if href:
            full_url = base_url + href
            department_links.append(full_url)
    return department_links

def parse_courses(soup):
    """ Extract course data from the BeautifulSoup object. """
    courses = []
    course_blocks = soup.find_all('div', class_='courseblock')

    for block in course_blocks:
        title_info = block.find('p', class_='courseblocktitle').text.strip() if block.find('p', class_='courseblocktitle') else 'N/A'
        description = block.find('p', class_='courseblockdesc').text.strip() if block.find('p', class_='courseblockdesc') else 'N/A'

        # Initialize details to 'N/A'
        instructors = 'N/A'
        terms_offered = 'N/A'
        equivalent_courses = 'N/A'
        prerequisites = 'N/A'

        detail_block = block.find('p', class_='courseblockdetail')
        if detail_block:
            detail_info = detail_block.text.strip()
            # Instructor(s): might be followed by Terms Offered or Equivalent Course(s)
            if 'Instructor(s):' in detail_info:
                instructor_line = detail_info.split('Instructor(s):')[1]
                # Assuming 'Terms Offered:' or 'Equivalent Course(s):' comes after 'Instructor(s):'
                instructors = instructor_line.split('Terms Offered:')[0].split('Equivalent Course(s):')[0].strip()

            if 'Terms Offered:' in detail_info:
                terms_offered = detail_info.split('Terms Offered:')[1].split('Equivalent Course(s):')[0].strip()
                
            if 'Equivalent Course(s):' in detail_info:
                equivalent_courses = detail_info.split('Equivalent Course(s):')[1].strip()

        courses.append({
            'Course Number': title_info.split('.')[0].strip() if title_info != 'N/A' else 'N/A',
            'Title': title_info.split('.')[1].strip() if len(title_info.split('.')) > 1 else 'N/A',
            'Description': description,
            'Instructors': instructors,
            'Terms Offered': terms_offered,
            'Equivalent Courses': equivalent_courses
        })
    
    return courses


def save_to_csv(courses, filename='uchicago_courses.csv'):
    """ Save the list of courses to a CSV file. """
    if not courses:
        print("No courses to save.")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=courses[0].keys())
        writer.writeheader()
        writer.writerows(courses)
    print(f"Data successfully saved to {filename}.")

def main():
    base_url = 'http://collegecatalog.uchicago.edu'
    department_urls = get_department_urls(base_url)
    all_courses = []

    for url in department_urls:
        print(f"Scraping courses from {url}")
        soup = get_page(url)
        if soup:
            department_courses = parse_courses(soup)
            all_courses.extend(department_courses)

    save_to_csv(all_courses)

if __name__ == '__main__':
    main()
