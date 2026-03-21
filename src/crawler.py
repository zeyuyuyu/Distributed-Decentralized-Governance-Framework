import time
import random
from urllib.parse import urlparse
from collections import defaultdict

class PolitenessPolicies:
    def __init__(self):
        self.domain_access_times = defaultdict(float)
        self.domain_rates = defaultdict(lambda: 1.0) # requests per second
        self.min_delay = 1.0 # global minimum delay between requests
        self.backoff_factor = 1.5 # multiplicative increase on 429/503
        self.recovery_factor = 0.9 # multiplicative decrease when successful

    def get_delay(self, url):
        domain = urlparse(url).netloc
        current_time = time.time()
        last_access = self.domain_access_times[domain]
        rate = self.domain_rates[domain]
        
        delay = max(self.min_delay, 1.0/rate)
        wait_time = max(0, last_access + delay - current_time)
        
        # Add small random jitter
        wait_time += random.uniform(0, 0.1)
        return wait_time

    def record_success(self, url):
        domain = urlparse(url).netloc
        self.domain_access_times[domain] = time.time()
        self.domain_rates[domain] *= self.recovery_factor

    def record_failure(self, url, status_code):
        domain = urlparse(url).netloc
        if status_code in (429, 503):
            self.domain_rates[domain] /= self.backoff_factor

class Crawler:
    def __init__(self):
        self.politeness = PolitenessPolicies()
        self.visited_urls = set()
        self.queue = []

    def add_url(self, url):
        if url not in self.visited_urls:
            self.queue.append(url)

    async def crawl(self, url):
        if url in self.visited_urls:
            return

        # Wait according to politeness policy
        delay = self.politeness.get_delay(url)
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            # Placeholder for actual HTTP request
            response = await self.make_request(url)
            
            self.visited_urls.add(url)
            self.politeness.record_success(url)

            # Process response and extract new URLs
            new_urls = self.extract_urls(response)
            for new_url in new_urls:
                self.add_url(new_url)

        except Exception as e:
            self.politeness.record_failure(url, getattr(e, 'status', 500))
            # Log error and potentially retry

    async def make_request(self, url):
        # Placeholder for actual HTTP request implementation
        pass

    def extract_urls(self, response):
        # Placeholder for URL extraction logic
        return []

    async def run(self):
        while self.queue:
            url = self.queue.pop(0)
            await self.crawl(url)
