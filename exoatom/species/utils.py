MAX_IONIZATION_STAGE = 119  # fully-stripped oganesson!

def int_to_roman(n):
    vals = [
        100, 90, 50, 40,
        10, 9, 5, 4, 1
    ]
    numerals = [
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV", "I"
    ]
    roman_numeral = ""
    i = 0
    while n > 0:
        for _ in range(n // vals[i]):
            roman_numeral += numerals[i]
            n -= vals[i]
        i += 1
    return roman_numeral

# Mapping between integers and roman numerals...
int_to_roman_numerals = {i: int_to_roman(i) for i in range(1, MAX_IONIZATION_STAGE+1)}
# ...in both directions.
roman_numerals_to_int = {int_to_roman_numerals[i]: i for i in int_to_roman_numerals}
