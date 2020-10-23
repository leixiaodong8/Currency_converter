# Currency Converter

Simple cross-platform currency converter with graph plotting and visualization of values in a table-like manner.

## Download and usage

The application is available for Windows, Mac and Linux and it can be simply cloned using Git:

```bash
git clone https://github.com/leixiaodong8/Currency_converter.git
```

Or it can be deployed with Pyinstaller:

First the `.spec` file needs to be created with `pyi-makespec <options> main.py`. Then, in the `.spec` file these paths need to be added so that everything is included in the executable:

```
datas=[
    ("currency_scraper/scrapy.cfg", "currency_scraper"),
    ("currency_scraper/currency_scraper/*", "currency_scraper/currency_scraper"),
    ("Gui/*", "Gui"),
    ("Gui/Images/*", "Gui/Images")
]
```

Then the application can be deployed with:

```bash
pyinstaller main.spec
```

## Description

This currency converter aims to implement additional features to the "standard" model, such as graph plotting and interaction with the historical values retrieved from the database, which is created entirely with values scraped from [this website][0].

The main goal of this application is educational and for learning purposes. The project uses important Python libraries, such as PyQt5, Matplotlib, Twisted and Scrapy. Even though things could be done more efficiently with less libraries, this application is aimed mainly for learning these frameworks, so it uses more resources on purpose. Some embedded SQL language was implemented with `cursor.execute()` in the Sqlite3 library for limiting the size of the databases using triggers (no ORMs were used). The program can be compiled to run as a standalone application using Pyinstaller with the configurations in `main.spec` and, although it uses some big libraries, the total size of the executable ammounts to ~70mb (if UPX is used).

### Utilization

The GUI has two distinct parts: a part that plots graphs and loads the database records in a table-like fashion and the actual conversion part. Both are fairly intuitive, enabling the user to choose between the currencies available (located inside comboboxes), as the example shows:

![Currency-converter-layout](https://user-images.githubusercontent.com/67561977/97057242-30d1d100-1561-11eb-8b51-680adb18621e.png)

Every time the user clicks the "Update database" button, the Scrapy spider is initialized and fetches data from the website, storing it in a local database with the Scrapy pipelines. When the user chooses to delete all records, the button "Delete database" can be pressed, and a warning will pop up informing the user that all changes are permanent.


[0]: https://br.investing.com/currencies/exchange-rates-table
