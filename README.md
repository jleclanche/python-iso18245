# python-iso18245

A Python implementation of the ISO 18245 Merchant Category Codes database.

## Installation

- `pip install iso18245`

## Usage

```py

>>> import iso18245
>>> iso18245.get_mcc("5542")
MCC(range=MCCRange(start='5000', end='5599', description='Retail outlets', reserved=False), iso_description='Automated fuel dispensers', usda_description='Automated Fuel Dispensers', stripe_description='Automated Fuel Dispensers', stripe_code='automated_fuel_dispensers')
>>> iso18245.get_mcc("3000")
MCC(range=MCCRange(start='3000', end='3999', description='Reserved for private use', reserved=True), iso_description='', usda_description='UNITED AIRLINES', stripe_description='', stripe_code='')
>>> iso18245.get_mcc("3000").usda_description
'UNITED AIRLINES'
>>> iso18245.get_mcc("3000").range
MCCRange(start='3000', end='3999', description='Reserved for private use', reserved=True)
>>> iso18245.get_mcc("999999")
Traceback (most recent call last):
  …
iso18245.InvalidMCC: 999999
```

## External links

- [Wikipedia: ISO 18245](https://en.wikipedia.org/wiki/ISO_18245)
- [ISO Standard 18245:2003](https://www.iso.org/standard/33365.html)
- [AFNOR: ISO 18245](http://portailgroupe.afnor.fr/public_espacenormalisation/ISOTC68SC7/ISO%2018245.html)
- [Stripe MCC List](https://stripe.com/docs/issuing/categories)
- [USDA MCC List (incl. private MCCs)](https://www.dm.usda.gov/procurement/card/card_x/mcc.pdf)
- [VISA Merchant Data Standards Manual](https://usa.visa.com/content/dam/VCOM/download/merchants/visa-merchant-data-standards-manual.pdf)
