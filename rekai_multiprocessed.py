import concurrent.futures
import threading
from loguru import logger

from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec



from nlp_modules.basic_nlp import TextSplitter
from nlp_modules.japanese_nlp import Classifier

logger.add(sink='log.log')

class Transform:
    @staticmethod
    def jisho_parse_string(line, index: str = 0):

        driver = webdriver.Chrome()

        jisho_parsed_html_element = str()


        if Classifier.contains_no_parsable_text(line):
            jisho_parsed_html_element += 'unparsable'

        else:
            url = f'https://jisho.org/search/{line}'

            try:

                logger.info(f'Trying to parse line {index}')

                driver.get(url=url)
                logger.info(f'{index} - Webdriver instance Started')

                zen_bar_element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "zen_bar")))
                zen_outer_html = zen_bar_element.get_attribute('outerHTML')

                # Selenium adds linebreaks that mess with the html when assigned to a string
                zen_html = str(zen_outer_html).replace('\n', "").strip()

                jisho_parsed_html_element += zen_html

            except Exception as e:
                print('Element not found: ', e)
                # jishoLog += "An Exception occurred:" + str(e) + "\n\n"
                zen_html = f'<p>((Text is not parsable or could not be parsed))</p>'
                jisho_parsed_html_element += zen_html

            driver.quit()

        return jisho_parsed_html_element

    @staticmethod
    def jisho_parse(list_of_lines: list) -> list:

        logger.info('JISHO AutoParse initialized')

        if isinstance(list_of_lines, list):

            with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
                index_list = [index for index, line in enumerate(list_of_lines)]
                list_of_jisho_parsed_html_elements = list(executor.map(Transform.jisho_parse_string, list_of_lines, index_list))
                print(list_of_jisho_parsed_html_elements)
            logger.info("JISHO AutoParse: All lines parsed")

            # Replace Jisho relative ref urls with full urls and add classes to open jisho links in embedded iframe
            list_of_jisho_parsed_html_elements = [html.replace('/search/', 'https://jisho.org/search/')
                                                  for html in list_of_jisho_parsed_html_elements]

            list_of_jisho_parsed_html_elements = [html.replace('class="current"', 'class=""')
                                                  for html in list_of_jisho_parsed_html_elements]

            list_of_jisho_parsed_html_elements = [html.replace('class=""', 'class="jisho-link"')
                                                  for html in list_of_jisho_parsed_html_elements]

        else:
            logger.error(f"JISHO AUTOPARSE:Type ERROR: argument was not a list but {str(type(list_of_lines))}")
            raise TypeError(f"JISHO AutoParse: argument was not a list but {str(type(list_of_lines))}")

        return list_of_jisho_parsed_html_elements


from nlp_modules.basic_nlp import test_text as test_lines
from nlp_modules.basic_nlp import test_text_2 as test_lines_2

test_list = TextSplitter.splitlines_to_list(input_text=test_lines, strip_each_line=True, trim_list=True)
test_list_2 = TextSplitter.splitlines_to_list(input_text=test_lines_2, strip_each_line=True, trim_list=True)

# def threaded_function(test_list, test_list_2):
#     th1 = threading.Thread(target=Transform.jisho_parse, args=(test_list,))
#     th2 = threading.Thread(target=Transform.jisho_parse, args=(test_list_2,))
#     th1.start()
#     th2.start()
#     th1.join()
#     th2.join()

# if __name__ == '__main__':

    # Transform.jisho_parse(list_of_lines=test_list)

