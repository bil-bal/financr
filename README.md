# financr

[financr](https://financronline.de) is an easy and lightweight way to keep track of your expenses
It is meant to help you add your daily spendings to a database from anywhere and be able to look up your finances and filter the entries multiple ways to give you the best fitting overview you need. But you can use it however its possible and you like.

The entries are made up of date, category, price, and optional notes which you can add. It is possible to edit every entry after adding it to the table. You can set custom categories for everything you can think of, to help you keep things organised to your preference.

You can add a monthly limit to your total spendings which will show how much of that limit you reached or if you passed it and by how much percent.

It is possible to download your entries as a .csv file for easy transfer, a local backup or to work on the data. Importing a .csv file is possible too. Just make sure it contains the header date, category, price, notes with the data in the correct columns.

The actual amounts (price column and monthly limit) will be encrypted through the Fernet (symmetric encryption) algorithm and a secret key and everytime they get looked up, or downloaded as a .csv file they will be decrypted.

Finally, you can view graphs for your data to help you visualize the expenses.

## Built with

- HTML
- CSS
- Python
- PostgreSQL

## Modules used

- Django
- Cryptography
- Pygal

## To do

- Add new features.
