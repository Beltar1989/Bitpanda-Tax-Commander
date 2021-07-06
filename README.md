# Bitpanda-Tax-Commander
Calculate Transactions less than 1 year from Bitpanda CSV
Combine Bought Coins with Sold Coins as FIFO

Initial Release is for Testing.
Please keep in Mind, its your Personal Response to check the Data and calculate Tax by yourself.
This Tool just help you ordering and do some precalculation for you. I developed to track my free transactions (<~440€ in Austria).

Default Setting for Deposit is Year 2010, because i bought my deposits everytime earlier than one year.
If you wanna change that, just set deposit_realdate=1 at beginning.

Put bitpanda.csv at same directory and start with:
python commander.py

wait until Graphical Interface appear. With new csv or some changes its suggested to remove database file and restart.

Notes:
bitpanda.csv might not be complete
If you got some advertisment coins its not listed.
For example i got: 
19 BEST (5Euro) on 8.01.2021
ETH(5Euro) on 8.11.2018
ICO not listed too

Since last version they add some data before in csv, maybe edit line 24:
        if dataptr > 7:
to adjust start of values