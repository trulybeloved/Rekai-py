import asyncio
import typing

import requests

from pyppeteer import launch as PyppeteerLaunch
from pyppeteer.errors import TimeoutError, PageError, NetworkError, BrowserError
from loguru import logger
import aiohttp

from custom_modules.custom_exceptions import WebPageLoadError


def get_http_response_status(url: str) -> int:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.head(url, headers=headers)
        return response.status_code
    except requests.RequestException as e:
        logger.exception(f'There was an exception while sending an http request for url: {url} \n Exception: {e}')
        return 0


async def async_get_http_response_status(url: str) -> int:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.head(url) as response:
                return response.status
    except aiohttp.ClientError as e:
        logger.exception(f'There was an exception while sending an http request for url: {url} \n Exception: {e}')
        return 0


async def async_pyppeteer_webscrape(
        url: str,
        query_selectors: typing.Union[str, list],
        semaphore: asyncio.Semaphore = asyncio.Semaphore(1),
        browser: PyppeteerLaunch = None) -> dict:

    if isinstance(query_selectors, str):
        query_selectors = [query_selectors]

    results = {}
    results['scraped_url'] = url

    scrape_results = {}

    async with semaphore:

        if not browser:
            try:
                browser = await PyppeteerLaunch(
                    headless=False,
                    handleSIGINT=False,
                    handleSIGTERM=False,
                    handleSIGHUP=False)
                logger.warning(
                    'Browser was not provided. A new browser instance will be run for each iteration. '
                    'This will add considerable overhead.')

                browser_launched_within_function = True
            except BrowserError as e:
                raise e
        else:
            browser_launched_within_function = False

        # Open a new tab in the browser
        page = await browser.newPage()

        try:
            await page.goto(url)
            # Ensure webpage is fully loaded
            sub_tasks = []
            for query_selector in query_selectors:
                sub_tasks.append(page.waitForSelector(query_selector))
            await asyncio.gather(*sub_tasks)

        except (NetworkError, TimeoutError, PageError) as e:
            logger.error(f'There was an error while loading the page for {url}')
            raise WebPageLoadError()

        for query_selector in query_selectors:
            element = await page.querySelector(selector=query_selector)

            if element:
                outer_html = await page.evaluate('(element) => element.outerHTML', element)

            scrape_results[f'{query_selector}'] = f'{outer_html}' if outer_html else None

        if browser_launched_within_function:
            await browser.close()

    results['scrape_results'] = scrape_results

    return results

# Example usage
url = "https://ncode.syosetu.com/n2267be/663/"
html = asyncio.run(async_pyppeteer_webscrape(url, ['.novel_subtitle', '#novel_honbun']))

chapter_html = html['scrape_results']['#novel_honbun']

with open('chapter_html.html', 'w', encoding='utf-8') as html_file:
    html_file.write(chapter_html)

