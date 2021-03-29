import csv
import sys

import requests
from bs4 import BeautifulSoup


def main():
	url = "https://global.alipay.com/docs/ac/files/mcclist"
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	table = soup.find("table", class_="lake-table")
	rows = []
	for row in table.find_all("tr"):
		cells = row.find_all("td")
		if not cells:
			continue
		mcc, description = cells[0].text, cells[1].text
		if mcc == "MCC":
			continue
		if not mcc.isdigit():
			raise ValueError(f"Unexpected MCC: {mcc!r} ({description!r})")
		rows.append([mcc, description])

	writer = csv.writer(sys.stdout)
	writer.writerow(["MCC", "DESCRIPTION"])
	writer.writerows(rows)


if __name__ == "__main__":
	main()
