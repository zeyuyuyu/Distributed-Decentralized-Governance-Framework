import asyncio
import aiohttp
import logging
from typing import List, Set
from urllib.parse import urljoin
from aiohttp import ClientSession
from asyncio import Semaphore
from collections import deque

class DistributedCrawler:
    def __init__(self, max_concurrent: int = 10, rate_limit: float = 1.0):
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.semaphore = Semaphore(max_concurrent)
        self.visited: Set[str] = set()
        self.queue = deque()
        self.session: ClientSession = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def fetch_url(self, url: str) -> str:
        """Fetch URL content with rate limiting and error handling"""
        async with self.semaphore:
            try:
                await asyncio.sleep(self.rate_limit)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    self.logger.warning(f'Error fetching {url}: {response.status}')
            except Exception as e:
                self.logger.error(f'Failed to fetch {url}: {str(e)}')
            return ''

    async def process_url(self, url: str, base_url: str) -> List[str]:
        """Process a URL and extract all linked URLs"""
        content = await self.fetch_url(url)
        if not content:
            return []

        # Extract links (simplified - production code would use proper HTML parsing)
        links = []
        for line in content.split('\n'):
            if 'href=' in line:
                # Basic link extraction - would use BeautifulSoup in production
                start = line.find('href=') + 6
                end = line.find('"', start)
                if start > 5 and end > start:
                    link = line[start:end]
                    absolute_url = urljoin(base_url, link)
                    links.append(absolute_url)
        return links

    async def crawl(self, start_url: str, max_depth: int = 3) -> Set[str]:
        """Perform distributed crawling starting from given URL"""
        self.queue.append((start_url, 0))
        self.visited.add(start_url)

        while self.queue:
            url, depth = self.queue.popleft()
            if depth >= max_depth:
                continue

            links = await self.process_url(url, start_url)
            for link in links:
                if link not in self.visited:
                    self.visited.add(link)
                    self.queue.append((link, depth + 1))
                    self.logger.info(f'Found new URL: {link} at depth {depth + 1}')

        return self.visited

async def main():
    async with DistributedCrawler(max_concurrent=5, rate_limit=1.0) as crawler:
        urls = await crawler.crawl('https://example.com', max_depth=2)
        print(f'Crawled {len(urls)} URLs')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
