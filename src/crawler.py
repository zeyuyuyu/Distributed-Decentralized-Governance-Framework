import asyncio
import aiohttp
import hashlib
import json

class ScrapingSwarm:
    def __init__(self, seed_urls, num_agents=10, max_concurrency=100):
        self.seed_urls = seed_urls
        self.num_agents = num_agents
        self.max_concurrency = max_concurrency
        self.crawled_urls = set()
        self.queue = asyncio.Queue()
        self.results = []

    async def _fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()
                return content

    async def _process(self):
        while True:
            url = await self.queue.get()
            if url in self.crawled_urls:
                self.queue.task_done()
                continue
            self.crawled_urls.add(url)
            try:
                content = await self._fetch(url)
                result = {
                    'url': url,
                    'content_hash': hashlib.sha256(content.encode()).hexdigest()
                }
                self.results.append(result)
            except Exception as e:
                print(f'Error fetching {url}: {e}')
            self.queue.task_done()

    async def run(self):
        for url in self.seed_urls:
            self.queue.put_nowait(url)

        tasks = [asyncio.create_task(self._process()) for _ in range(self.num_agents)]
        await self.queue.join()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.results

# Example usage:
seed_urls = ['https://example.com', 'https://example.org', 'https://example.net']
swarm = ScrapingSwarm(seed_urls, num_agents=10, max_concurrency=100)
results = await swarm.run()
print(json.dumps(results, indent=2))