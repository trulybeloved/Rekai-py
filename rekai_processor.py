import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from nlp_modules.basic_nlp import TextSplitter

from nlp_modules.japanese_nlp import Classifier


class Transform:

    @staticmethod
    async def jisho_parse(list_of_lines: list, *, sleep: bool = False) -> list:

        # logging needs to be added

        # core functionality

        list_of_jisho_parsed_html_elements = []

        if isinstance(list_of_lines, list):

            # try:
            #     driver = webdriver.Chrome()
            # except Exception as e:
            #     print('Webdriver initialization failed')
            #     print(e)

            driver = webdriver.Chrome()

            for i, line in enumerate(list_of_lines):

                async def async_task(i ,line):
                    if Classifier.contains_no_parsable_text(line):
                        list_of_jisho_parsed_html_elements.append('unparsable')

                    else:
                        url = f'https://jisho.org/search/{line}'

                        try:
                            print(f"JISHO AUTOPARSE: Trying line {i}")
                            driver.get(url=url)
                            zen_bar_element = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.ID, "zen_bar"))
                            )

                            zen_outer_html = zen_bar_element.get_attribute('outerHTML')

                            # Selenium adds linebreaks that mess with the html when assigned to a string
                            zen_html = str(zen_outer_html).replace('\n', "").strip()

                            list_of_jisho_parsed_html_elements.append(zen_html)
                            if sleep:
                                await asyncio.sleep(3)
                        except Exception as e:
                            print('Element not found: ', e)
                            # jishoLog += "An Exception occurred:" + str(e) + "\n\n"
                            zen_html = f'<p>((Text is not parsable or could not be parsed))</p>'
                            list_of_jisho_parsed_html_elements.append(zen_html)
                await async_task(i, line)
            driver.quit()
            print("JISHO AUTOPARSE: All lines parsed")

            # Replace Jisho relative ref urls with full urls and add classes to open jisho linked in embedded iframe
            list_of_jisho_parsed_html_elements = [html.replace('/search/', 'https://jisho.org/search/')
                                                  for html in list_of_jisho_parsed_html_elements]

            list_of_jisho_parsed_html_elements = [html.replace('class="current"', 'class=""')
                                                  for html in list_of_jisho_parsed_html_elements]

            list_of_jisho_parsed_html_elements = [html.replace('class=""', 'class="jisho-link"')
                                                  for html in list_of_jisho_parsed_html_elements]

        else:
            print(f"JISHO AUTOPARSE:Type ERROR: argument was not a string/list but {str(type(list_of_lines))}")
            return ['JISHO AUTOPARSE: Function could not run as there was a type error in the argument']

        return list_of_jisho_parsed_html_elements


from nlp_modules.basic_nlp import test_text as test_lines
from nlp_modules.basic_nlp import test_text_2 as test_lines_2

test_list = TextSplitter.splitlines_to_list(input_text=test_lines, strip_each_line=True, trim_list=True)
test_list_2 = TextSplitter.splitlines_to_list(input_text=test_lines_2, strip_each_line=True, trim_list=True)

async def main():
    print('start of main function')

    task1 = asyncio.create_task(Transform.jisho_parse(test_list))
    task2 = asyncio.create_task(Transform.jisho_parse(test_list_2))

    await task1
    await task2

    print('main complete')

if __name__ == '__main__':

    asyncio.run(main())