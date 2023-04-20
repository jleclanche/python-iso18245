import csv
import sys

if __name__ == "__main__":
	with open(sys.argv[1]) as f:
		reader = csv.reader(f)
		last_mcc = ""
		last_mcc_num = 0
		rows = []
		for row in reader:
			if not row[0].isdigit():
				continue

			# sometimes the first digit gets cut off
			# Add the first digit of the previous mcc… should be ok
			if len(row[0]) == 3:
				last_mcc_first_digit = last_mcc[0]
				guess = last_mcc_first_digit + row[0]
				# Sanity check: MCCs are incremental in the document
				# newer MCC should never be lower than previous one
				if int(guess) < last_mcc_num:
					# try again, increase first digit by 1
					guess = str(int(guess[0]) + 1) + guess[1:]
				# now if it doesnt work error out
				assert int(guess) > last_mcc_num
				assert len(guess) == 4
				row[0] = guess

			last_mcc = row[0]
			last_mcc_num = int(last_mcc)

			final_row = [row[0]] + [k for k in row[1:] if k and not k.isdigit()]
			if len(final_row) == 2:
				final_row.append("")
			rows.append(final_row)

			# text extraction failure overrides
			if last_mcc_num == 4214:
				final_row = [
					"4214",
					"Motor Freight Carriers and Trucking–Local and Long Distance, Moving and Storage Companies, and Local Delivery Services",
					"",
				]

			if last_mcc_num == 4814:
				final_row = [
					"4814",
					"Telecommunication Services, including Local and Long Distance Calls, Credit Card Calls, Calls Through Use of Magnetic-Stripe-Reading Telephones, and Fax Services",
					"",
				]

			assert len(final_row) == 3, final_row

		writer = csv.writer(sys.stdout)
		writer.writerow(
			[
				"MCC",
				"DESCRIPTION",
				"REQUIRED NAME IN AUTHORIZATION REQUEST / CLEARING RECORD",
			]
		)
		writer.writerows(rows)
