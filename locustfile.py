from random import randrange

from locust import HttpUser, between, tag, task


class PostcodesUser(HttpUser):
    wait_time = between(1, 5)

    @task
    @tag("data")
    def postcodes(self):
        skip = randrange(10000)
        self.client.get(f"/postcodes?skip={skip}&limit=100")

    @task
    @tag("data")
    def localities(self):
        postcode = randrange(10000)
        self.client.get(f"/postcodes/{postcode}/localities")

    @task
    @tag("sync")
    def sync_query(self):
        skip = randrange(10000)
        self.client.get(f"/postcodes/slow/sync?skip={skip}&limit=100")

    @task
    @tag("async")
    def async_query(self):
        skip = randrange(10000)
        self.client.get(f"/postcodes/slow/async?skip={skip}&limit=100")
