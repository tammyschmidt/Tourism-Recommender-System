# Manipulate reviews data to handle DataAfterQuoteException in Cypher
# by deleting all smileys in the form of ":\" (or similar) at the end of the 'text' field
# in order to avoid escaped double quote.

import csv

input_file = 'reviews.csv'
output_file = 'reviews_cleaned.csv'

with open(input_file, mode='r', encoding='utf-8', newline='') as infile, \
     open(output_file, mode='w', encoding='utf-8', newline='') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

    writer.writeheader()

    for row in reader:
        text = row.get('text', '')
        # If text ends with "\", remove it
        if text.endswith('\\'):
            row['text'] = text[:-1]  # Remove last character
        writer.writerow(row)

print("Done! Cleaned file saved as 'reviews_cleaned.csv'")


