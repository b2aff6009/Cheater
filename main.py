
import json
import os  # needed for user id check
import psutil
import platform

import finder
import crawler.crawler
import gui

SettingsPath = "configuration.json"
settings = {}


def osName():
    Names = {"Windows": "Windows", "Linux": "Linux", "Darwin": "Mac"}
    return Names[platform.system()]


def getProcessName():
    p = psutil.Process(os.getpid())
    return p.name()


def parseShortSheet(cheatSheet):
    keyList = cheatSheet["entry"]
    valueList = cheatSheet["common"]
    data = {}
    data["visible"] = cheatSheet["visible"]
    data["common"] = []
    for value in valueList:
        entry = {}
        for i, key in enumerate(keyList, 0):
            entry[key] = value[i]
        data["common"].append(entry)
    return data


def GetSheets(config):
    if (config["crawler"]["use"] == True):
        sheetCrawler = crawler.crawler.createCrawler(config["crawler"])
        sheetList = list(sheetCrawler.generator())
        sheets = {}
        for sheet in sheetList:
            sheets[os.path.basename(sheet)] = sheet
        config["sheets"] = sheets
    return config["sheets"]


def SelectSheet(config, name=""):
    sheets = GetSheets(config)
    if name == "":
        name = settings["defaultSheet"]
    if name == "" or name not in config['sheets']:
        selector = finder.createFinder(settings["finder"], sheets, True)
        selectGui = gui.Gui(selector, settings,  True)
        selectGui.run()
        name = selectGui.sheet
    return name


def setDefault(data, key, val):
    data[key] = data.get(key, val)


def SetDefaultSettings(config):
    '''Ensure that every config parameter exists, if it doens't it will be set to a default value'''

    # Settings used by crawler
    setDefault(config, "crawler", {})
    setDefault(config["crawler"], "use", True)
    setDefault(config["crawler"], "recrusive", True)
    setDefault(config["crawler"], "extension", ".csh")
    setDefault(config["crawler"], "directories", ["./"])

    setDefault(config, "sheets", {})

    setDefault(config, "settings", {})
    setDefault(config["settings"], "defaultSheet", "")
    setDefault(config["settings"], "AllowOverwrite", True)
    setDefault(config["settings"], "shortSheet", False)
    setDefault(config["settings"], "finder", "normal")

    # Settings used by Gui
    setDefault(config["settings"], "bgColors", [
               "SkyBlue1", "SkyBlue2", "SkyBlue3"])
    setDefault(config["settings"], "HeadlineFont", 'Helvetica 15 bold')
    setDefault(config["settings"], "Font", 'Helvetica 11')
    setDefault(config["settings"], "multiLineEntry", False)
    setDefault(config["settings"], "columns", 1)
    setDefault(config["settings"], "selectKey", '<Return>')
    setDefault(config["settings"], "position", [0.25, 0.25])
    setDefault(config["settings"], "opacity", 1)
    setDefault(config["settings"], "maxEntrys", 30)
    setDefault(config["settings"], "selectionUp", '<Up>')
    setDefault(config["settings"], "selectionDown", '<Down>')
    setDefault(config["settings"], "backKey", '<Ctrl-Escape>')
    setDefault(config["settings"], "cleanKey", '<Escape>')
    setDefault(config["settings"], "Debug", False)


def LoadConfig(name):
    global settings
    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    SetDefaultSettings(configJson)
    settings = configJson["settings"]
    if settings["Debug"]:
        print(configJson)

    return configJson, settings


def LoadSheet(name, config, settings):
    with open(config["sheets"][name], 'rb') as f:
        data = json.load(f)
    data["common"].extend(data.get(osName(), []))

    # Overwrite global settings with specific sheet settings
    if settings["AllowOverwrite"]:
        for key in data["settings"]:
            settings[key] = data["settings"][key]

    if (settings["shortSheet"]):
        data = parseShortSheet(data)
    return data


if __name__ == "__main__":
    config, settings = LoadConfig("")
    sheetName = SelectSheet(config)
    sheet = LoadSheet(sheetName, config, settings)
    mFinder = finder.createFinder(settings["finder"], sheet)

    if settings["Debug"] == True:
        print("Finder typ: {}".format(mFinder.__class__))
    Ui = gui.Gui(mFinder, settings)
    Ui.run()
