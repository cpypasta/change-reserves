# change-reserves

This is a GUI tool to quickly modify the reserve bin files. At the moment, the tool can make the following modifications:

1. Updates the population size of all the reserves.
1. Updates the number of deployables on all the reserves.

# How To Build

To build executable:

```sh
pyinstaller -F --noconsole --add-data "reserves/data;reserves/data" reserves.py
```