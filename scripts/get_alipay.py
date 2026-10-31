import csv
import sys
from io import BytesIO
from urllib.parse import urljoin
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup


NAMESPACE = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _cell_value(cell, shared_strings):
	cell_type = cell.get("t")
	if cell_type == "inlineStr":
		value = "".join(
			text.text or "" for text in cell.findall(".//main:t", NAMESPACE)
		)
	else:
		value_element = cell.find("main:v", NAMESPACE)
		value = value_element.text if value_element is not None else ""
		if cell_type == "s" and value:
			value = shared_strings[int(value)]
	return " ".join(value.split())


def _read_mcc_rows(workbook):
	with ZipFile(BytesIO(workbook)) as archive:
		shared_strings = []
		if "xl/sharedStrings.xml" in archive.namelist():
			root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
			shared_strings = [
				"".join(text.text or "" for text in item.findall(".//main:t", NAMESPACE))
				for item in root.findall("main:si", NAMESPACE)
			]

		mcc_rows = []
		for sheet_name in sorted(
			name
			for name in archive.namelist()
			if name.startswith("xl/worksheets/") and name.endswith(".xml")
		):
			root = ET.fromstring(archive.read(sheet_name))
			rows = root.findall(".//main:sheetData/main:row", NAMESPACE)
			for index, row in enumerate(rows):
				cells = [
					(
						cell.get("r", "").rstrip("0123456789"),
						_cell_value(cell, shared_strings),
					)
					for cell in row.findall("main:c", NAMESPACE)
				]
				headers = dict(cells)
				if "MCC" not in headers.values() or "Description" not in headers.values():
					continue

				mcc_column = next(
					column for column, value in cells if value == "MCC"
				)
				description_column = next(
					column for column, value in cells if value == "Description"
				)
				for data_row in rows[index + 1 :]:
					data_cells = {
						cell.get("r", "").rstrip("0123456789"): _cell_value(
							cell, shared_strings
						)
						for cell in data_row.findall("main:c", NAMESPACE)
					}
					mcc = data_cells.get(mcc_column, "")
					description = data_cells.get(description_column, "")
					if not mcc and not description:
						continue
					if not description and mcc.startswith("[") and "]" in mcc:
						continue
					if not mcc.isdigit():
						raise ValueError(
							f"Unexpected MCC: {mcc!r} ({description!r})"
						)
					mcc_rows.append([mcc, description])
				break

		if not mcc_rows:
			raise ValueError("Could not find MCC and Description columns in the workbook")

		mcc_codes = [row[0] for row in mcc_rows]
		if len(mcc_codes) != len(set(mcc_codes)):
			raise ValueError("Duplicate MCCs found in the workbook")
		return mcc_rows


def main():
	url = "https://docs.antom.com/ac/ref/mcccodes"
	response = requests.get(url)
	response.raise_for_status()
	soup = BeautifulSoup(response.content, "html.parser")
	mcc_link = next(
		(
			anchor["href"]
			for anchor in soup.find_all("a", href=True)
			if anchor.get_text(" ", strip=True) == "MCC list"
		),
		None,
	)
	if mcc_link is None:
		raise ValueError("Could not find the MCC list download link")

	workbook_response = requests.get(urljoin(url, mcc_link))
	workbook_response.raise_for_status()
	rows = _read_mcc_rows(workbook_response.content)

	writer = csv.writer(sys.stdout, lineterminator="\n")
	writer.writerow(["MCC", "DESCRIPTION"])
	writer.writerows(rows)


if __name__ == "__main__":
	main()
