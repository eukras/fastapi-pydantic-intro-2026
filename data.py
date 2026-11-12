import csv
from collections.abc import Generator


def yield_csv_rows(filename: str) -> Generator[dict, None, None]:
    with open(filename) as csvfile:
        for i, row in enumerate(csv.reader(csvfile)):
            yield {
                "id": i + 1,
                "locality": row[0],
                "state": row[1],
                "postcode": row[2],
                "count": row[3],
                "lat": row[4],
                "long": row[5],
            }
