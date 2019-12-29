# Manga Desktop Reader

A simple manga reader for the desktop. Keeps track of all your favorite manga from your favorite manga sites all in place.

This is written in Python 3, but is python2.7 compatable(for windows users), and uses GTK3 for its GUI

## Getting Started

This application use existing manga reading site's library, thus must be supplied a url to fetch and display the title. However, once a url is given the title can be downloaded and read without a internet connection.

* To add a title, click on the "file" button in the upper left hand corner, and click the option "add Manga (URL)".

**Note** - currently only titles from the site [Manga Park](https://mangapark.net) are supported for download from this application. Support for other sites are planned for later releases.

### Prerequisites

If you wish run from source, please make sure the following python 3 packages are installed. If not download the apporpriate execuable for your system.

#### Packages
* **Selenium** - web automation
* **lxml** - HTML parser
* **requests** - allow for sending html requests
* **beautifulsoup4** - HTML extractor
* **PyObject** - GTK python/C++ binding library

### Linux
```
pip3 install selenium, lxml, requests, beautifulsoup4, PyObject
```
### Windows

At the moment there is not a windows executable so running from source is the only option. To run from source download the latest version of [Python 2.7](https://www.python.org/downloads/) and download [PyGObject](https://sourceforge.net/projects/pygobjectwin32/).
Once installed then install the same python packages as above (excluding PyObject as you already installed it). Then run the python script named "Main.py"

### Configure
This application uses a json configurtion file called config.json

#### Webdriver
The WebDriver is how Selenium creates a headless webbrowser for extracting the HTML elements needed, that only generate when in a browser. This Application uses these drivers for generating the manga's chapter pages so thay can be extracted. 
This webdriver must support the version of a web browser already installed on your system (e.g. Google Chome, Firefox).
**Note** - currently only drivers for Google Chrome have been tested.
Additional drivers can be found [here](https://selenium.dev/downloads/)

In the config file there are three properies need to tell the application which driver to use.
```
    "Webdriver Location" : "./WebDrivers",
    "Browser Version" : "2.45",
    "Browser" : "Chrome",
```
* **Webdriver Location** - Specifies the locations for all downloaded drivers
* **Browser Version** - Specifies the version number of your normal Webbrowser already installed in your system
* **Browser** - Specifies the target browser to use.

### Run
Download the apporpriate execuable for your system and run.

**Note** - Linux is the only platform supported at the moment. Windows and Mac execuables will be provided at a later date.

## Version

version 0.1 beta

## Author(s)

* **August B. Sandoval** - *Initial work* - [asandova](https://gitlab.com/asandova)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
