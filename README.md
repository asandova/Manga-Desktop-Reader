# Manga Desktop Reader

A simple manga reader for the desktop. Keeps track of all your favorite manga from your favorite manga sites all in place.

This is written in Python 3, but is python2.7 compatable and uses GTK3+(Linux only) or tkinter for its GUI

## Getting Started

This application use existing manga reading site's library, thus must be supplied a url to fetch and display the title. However, once a url is given the title and chapters are downloaded a internet connection is not needed.

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
* **pygubu** - Tkinter gui builder


#### Run from Source
To run from source make sure to install the following python packages.
```
pip3 install selenium, lxml, requests, beautifulsoup4, PyObject(Linux only), pygubu (tkinter GUI only)
```
### Linux
To run the application on Linux download the zip file containing the Linux executable.
### Windows
To run the application on Windows download the zip file containing the windows executable.

### Configure
This application uses a json configurtion file called [config.json](config.json)

#### Webdriver
The WebDriver is how Selenium creates a headless webbrowser for extracting the HTML elements needed that are only generate when in a browser. This Application uses these drivers for generating the title's chapter pages so thay can be extracted. 
This webdriver must support the version of a web browser already installed on your system (e.g. Google Chome, Firefox).

**Note** - currently only drivers for Google Chrome and Firefox are supported.
Additional drivers can be found [here](https://selenium.dev/downloads/)

In the config file there are four properies need to tell the application which web driver to use and how to place interface elements.
```
    "Webdriver Location" : "./WebDrivers",
    "Browser Version" : "2.45",
    "Browser" : "Chrome",
    "UI" : {
        "Main" : "path to the template file for the main interface",
        "Viewer" : "Path to the template file for the Viewer interface"
    }
```
* **Webdriver Location** - Specifies the locations for all downloaded drivers
* **Browser Version** - Specifies the version number of your normal Webbrowser already installed in your system
* **Browser** - Specifies the target browser to use.

* **UI** - This application allows for some customization for its interface. This is done with template files for both tkinter and gtk. The template files for GTK have the file extention ".glade" and tkinter ".ui". These are generate by Glade and Pygubu-designer respectively.
* **Main** - is the path to the Main interface file without the extention for your given interface
* **Viewer** - is the path to the Viewer interface file without the extention for your given interface (tkinter version currently doesn't support this option)

## Version

version 0.2 beta

## Author(s)

* **August B. Sandoval** - *Initial work* - [asandova](https://gitlab.com/asandova)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
