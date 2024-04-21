import csv
import os.path
from typing import Dict, List, NamedTuple

from pkg_resources import resource_filename

ISO_VERSION_YEAR = 2003


class MCCNotFound(KeyError):
	pass


class InvalidMCC(ValueError):
	pass


class MCCRange(NamedTuple):
	start: str
	end: str
	description: str
	reserved: bool


class MCC(NamedTuple):
	mcc: str
	range: MCCRange
	iso_description: str
	usda_description: str
	stripe_description: str
	stripe_code: str
	visa_description: str
	visa_req_clearing_name: str
	alipay_description: str
	mastercard_description: str
	mastercard_abbreviated_airline_name: str
	amex_description: str


_cached_csv: Dict[str, List[List[str]]] = {}


def _load_csv(path: str) -> List[List[str]]:
	if path not in _cached_csv:
		full_path = resource_filename("iso18245", os.path.join("data", path))
		with open(full_path, "r") as f:
			reader = csv.reader(f)
			_cached_csv[path] = list(reader)[1:]

	return _cached_csv[path]


def _find_mcc_in_csv(mcc: str, path: str) -> List[str]:
	for row in _load_csv(path):
		if row[0] == mcc:
			return row[1:]
	return []


def validate_mcc(mcc: str) -> int:
	mcc_as_num = int(mcc)
	if mcc_as_num < 0 or mcc_as_num > 9999:
		raise InvalidMCC(mcc)

	return mcc_as_num


def get_mcc(mcc: str) -> MCC:
	mcc_range = get_mcc_range(mcc)
	found = False
	iso_description = ""
	usda_description = ""
	stripe_description = ""
	stripe_code = ""
	visa_description = ""
	visa_req_clearing_name = ""
	alipay_description = ""
	mastercard_description = ""
	mastercard_abbreviated_airline_name = ""
	amex_description = ""

	if not mcc_range.reserved:
		data = _find_mcc_in_csv(mcc, "iso18245_official_list.csv")
		if data:
			iso_description, found = data[0], True

	usda_data = _find_mcc_in_csv(mcc, "usda_list.csv")
	if usda_data:
		usda_description, found = usda_data[0], True

	visa_info = _find_mcc_in_csv(mcc, "visa_list.csv")
	if visa_info:
		visa_description, visa_req_clearing_name, found = (
			visa_info[0],
			visa_info[1],
			True,
		)

	stripe_info = _find_mcc_in_csv(mcc, "stripe_list.csv")
	if stripe_info:
		stripe_description, stripe_code, found = stripe_info[0], stripe_info[1], True

	alipay_info = _find_mcc_in_csv(mcc, "alipay_list.csv")
	if alipay_info:
		alipay_description, found = alipay_info[0], True

	mastercard_info = _find_mcc_in_csv(mcc, "mastercard_list.csv")
	if mastercard_info:
		mastercard_description, mastercard_abbreviated_airline_name, found = mastercard_info[0], mastercard_info[1], True

	amex_info = _find_mcc_in_csv(mcc, "amex_list.csv")
	if amex_info:
		amex_description, found = amex_info[0], True

	if not found:
		raise MCCNotFound(mcc)

	return MCC(
		mcc=mcc,
		range=mcc_range,
		iso_description=iso_description,
		usda_description=usda_description,
		stripe_description=stripe_description,
		stripe_code=stripe_code,
		visa_description=visa_description,
		visa_req_clearing_name=visa_req_clearing_name,
		alipay_description=alipay_description,
		mastercard_description=mastercard_description,
		mastercard_abbreviated_airline_name=mastercard_abbreviated_airline_name,
		amex_description=amex_description,
	)


def get_mcc_range(mcc: str) -> MCCRange:
	mcc_as_num = validate_mcc(mcc)
	range_data = _load_csv("iso18245_ranges.csv")
	for range_start, range_end, description in range_data:
		start_num, end_num = int(range_start), int(range_end)
		if start_num <= mcc_as_num <= end_num:
			return MCCRange(
				range_start,
				range_end,
				description,
				reserved=description.startswith("Reserved"),
			)

		if end_num > mcc_as_num:
			break

	raise RuntimeError(f"Could not find correct MCC range for {mcc} (likely a bug)")


def get_all_mccs_in_range(first: str, last: str) -> List[MCC]:
	first_num = validate_mcc(first)
	last_num = validate_mcc(last)

	lists = [
		_load_csv("iso18245_official_list.csv"),
		_load_csv("stripe_list.csv"),
		_load_csv("usda_list.csv"),
		_load_csv("visa_list.csv"),
		_load_csv("mastercard_list.csv"),
		_load_csv("amex_list.csv"),
	]

	mccs = set()

	for mcc_list in lists:
		for mcc in mcc_list:
			mcc_num = int(mcc[0])
			if mcc_num < first_num:
				continue
			elif mcc_num > last_num:
				break
			mccs.add(mcc[0])

	return [get_mcc(mcc) for mcc in sorted(mccs)]


def get_all_mccs() -> List[MCC]:
	return get_all_mccs_in_range("0000", "9999")
