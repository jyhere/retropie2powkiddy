# *************************************************
# **                                             **
# ** RetroPieGame to Powkiddy A12 List Generator **
# **                    V1.0                     **
# **                                             **
# *************************************************
#
#
# Author : Jyhere
#
# Based on Wagner TechTalk genGamelist.py script
#
#
# Usage : retropie2powkiddy.py -r <retropie_system> -p <powkiddy_system>
#
# Example :
# Creates a new system "cps" in Retropie (see retropie doc for adding systems), copy your cps roms in the roms/cps
# directory and scrap art.
# Enter the command : retropie2powkiddy.py -r cps -p CPS


import sys, getopt, shutil, os, os.path
from os import path
from PIL import Image
from lxml import etree
from xml.sax.saxutils import escape
from operator import itemgetter

# RetroPie target system to import and PowKiddy target system for export
retroPieTargetSystem = powKiddyTargetSystem = ''

def main(argv):
    global retroPieTargetSystem, powKiddyTargetSystem
    powKiddySupportedSystems = [
        'CPS',
        'FBA',
        'FC',
        'GB',
        'GBA',
        'GBC',
        'GG',
        'MD',
        'NEOGEO',
        'PS',
        'SFC',
    ]
    try:
        opts, args = getopt.getopt(argv, "hr:p:", ["retropiesystem=", "powkiddysystem="])
    except getopt.GetoptError:
        print('retropie2powkiddy.py -r <retropiesystem> -p <powkiddysystem>')
        print('Available <powkiddysystem> systems : ' + ' '.join(powKiddySupportedSystems))
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('retropie2powkiddy.py -r <retropiesystem> -p <powkiddysystem>')
            sys.exit()
        elif opt in ("-r", "--retropiesystem"):
            retroPieTargetSystem = arg
        elif opt in ("-p", "--powkiddysystem"):
            powKiddyTargetSystem = arg
            powKiddyTargetSystem = powKiddyTargetSystem.upper()
    if retroPieTargetSystem == '' or powKiddyTargetSystem == '':
        print('Missing argument')
        print('retropie2powkiddy.py -r <retropiesystem> -p <powkiddysystem>')
        exit()
    if powKiddyTargetSystem not in powKiddySupportedSystems:
        print('PowKiddy available systems : ' + ' '.join(powKiddySupportedSystems))
        exit()


if __name__ == "__main__":
    main(sys.argv[1:])


# ====== IMPORTANT =======
# Root path of retropie installation
retroPieRootPath = '/opt/retropie'

# Path for retropie roms
retroPieRomsPath = '/home/jyhere/RetroPie/roms'

# Set to false if you don't want game art images
createArtImages = True

# Set to true if you don't want default no art image for games with missing art
createNoArtImage = False
# ========================

# For PowKiddy A12 (number of games that will show up on each page)
pageSize = 8

# This is the output file name that will be created, shouldn't need to change this
outputFileName = 'game_strings_en.xml'
# New Game Subdirectory
exportGameDirPath = 'roms'
# Name of the directory which will contain your converted images (converted from .jpg to .png) in
# a filename to match your game (roms).
imageDirPath = 'art'
# No art file name (Image that is displayed if no boxart can be found for the game)
noArtFilename = 'no_art.png'

# constants
EXTENSION_JPG = '.jpg'
EXTENSION_PNG = '.png'
GAMELIST_XML = 'gamelist.xml'
CRLF = '\r\n'

retroPieGameListXml = retroPieRootPath + '/configs/all/emulationstation/gamelists/' + retroPieTargetSystem + '/' + GAMELIST_XML
retroPieGameListImagesPath = retroPieRootPath + '/configs/all/emulationstation/downloaded_images/' + retroPieTargetSystem
retroPieGameListRomsPath = retroPieRomsPath + '/' + retroPieTargetSystem

if not path.exists(retroPieGameListXml):
    # try to read xml in rom directory
    retroPieGameListXml = retroPieGameListRomsPath + '/' + GAMELIST_XML
    if not path.exists(retroPieGameListXml):
        print("File " + retroPieGameListXml + 'is missing')
        exit()
if not path.exists(retroPieGameListRomsPath):
    print("Directory " + retroPieGameListXml + 'is missing')
    exit()
if not path.exists(retroPieGameListImagesPath):
    print("Directory " + retroPieGameListXml + 'is missing')
    exit()

gameList = {}
if path.exists(retroPieGameListXml):
    tree = etree.parse(retroPieGameListXml)

    for game in tree.xpath("/gameList/game"):
        gameProperties = list(game.iter())
        gamePath = gameName = gameImage = ''
        for gameProperty in gameProperties:
            if gameProperty.tag == 'path':
                gamePath = gameProperty.text
                hasPath = True
            if gameProperty.tag == 'name':
                gameName = gameProperty.text
                hasName = True
            if gameProperty.tag == 'image':
                gameImage = gameProperty.text

        if gamePath:
            archiveName = gamePath.lstrip('./')
            if path.exists(retroPieGameListRomsPath + '/' + archiveName):
                iFileExtensionIndex = gamePath.rindex('.')
                gameFileExtension = gamePath[iFileExtensionIndex:]
                shortName = archiveName.replace(gameFileExtension, '')
                if not gameName:
                    gameName = shortName
                if gameImage:
                    if gameImage[0] == '~':
                        # images are in the home directory
                        gameImage = os.path.expanduser(gameImage)
                    elif gameImage[0] == '.':
                        # images are in the gamelist.xml directory
                        gameImage = retroPieGameListXml.rstrip(GAMELIST_XML) + gameImage.lstrip('./')
                gameList[shortName] = {'name': gameName, 'short': shortName, 'file': archiveName, 'image': gameImage}

gameListCount = len(gameList)
print(gameListCount)

# Sorting games by full name
gameList = sorted(gameList.values(), key=itemgetter('name'))

# Setting paths
imageDirPath = "export/settings/res/" + powKiddyTargetSystem + '/pic'
xmlDirPath = "export/settings/res/" + powKiddyTargetSystem + '/string'
exportGameDirPath = "export/game/" + powKiddyTargetSystem
destinationImagePath = imageDirPath + '/'

# If Games are found in the XML
if createArtImages and gameListCount > 0:
    # Create image directory
    try:
        os.makedirs(imageDirPath)
        print('Image Directory ', imageDirPath, ' created.')
    except FileExistsError:
        print('Image Directory ', imageDirPath, ' already exists.')

try:
    os.makedirs(exportGameDirPath)
    print('Game Directory ', exportGameDirPath, ' created.')
except FileExistsError:
    print('Game Directory ', exportGameDirPath, ' already exists.')

try:
    os.makedirs(xmlDirPath)
except FileExistsError:
    pass

print('Exporting ' + retroPieTargetSystem + 'games:')

iPageCount = round(gameListCount / pageSize)
xmlOutput = ''
xmlOutput = xmlOutput + '<?xml version="1.0"?>   ' + CRLF
xmlOutput = xmlOutput + '<strings_resources>   ' + CRLF
xmlOutput = xmlOutput + '<icon_para game_list_total=' + str(gameListCount) + '></icon_para>   ' + CRLF

currentPage = currentItem = 1
currentItemOnPage = 0

# Indicates if page closing is needed
pageOpened = False

for gameData in gameList:
    print(gameData['short'] + '... ', end='')

    # Page header
    if currentItemOnPage == 0:
        xmlOutput = xmlOutput + '  <icon_page' + str(currentPage) + '> ' + CRLF
        pageOpened = True

    # Copying roms
    sourceFilePathName = retroPieGameListRomsPath + '/' + gameData['file']
    newFilePathName = exportGameDirPath + '/' + gameData['file']
    shutil.copyfile(sourceFilePathName, newFilePathName)

    # Copy Image file with the new name
    if createArtImages and gameData['image']:
        if path.exists(gameData['image']):
            imageFileName, imageFileExtension = os.path.splitext(gameData['image'])
            # If image is in jpg format, we need to convert it to png
            # If no image is found, we create a default iamge
            if imageFileExtension.lower() == '.jpg':
                destImageFile = destinationImagePath + gameData['short'] + '.png'
                img = Image.open(gameData['image'])
                img.save(destImageFile)
            elif imageFileExtension.lower() == '.png':
                destImageFile = destinationImagePath + '/' + gameData['short'] + '.png'
                shutil.copyfile(gameData['image'], destImageFile)
            elif createNoArtImage:
                destImageFile = destinationImagePath + '/' + gameData['short'] + '.png'
                shutil.copyfile(noArtFilename, destImageFile)

        xmlOutput = xmlOutput + '    <icon' + str(currentItemOnPage) + '_para  name=\"' + str(currentItem) + '.' + escape(gameData['name']) + '\" game_path=\"' + escape(gameData['file']) + '\"></icon' + str(currentItemOnPage) + '_para> ' + CRLF

    print('OK')
    # Page Suffix
    if (currentItemOnPage == pageSize - 1) or (currentItem == gameListCount and currentItemOnPage + 1 == pageSize - 1):
        xmlOutput = xmlOutput + '  </icon_page' + str(currentPage) + '> ' + CRLF
        currentItemOnPage = -1
        currentPage += 1
        pageOpened = False

    if currentItem <= gameListCount:
        currentItem += 1
        currentItemOnPage += 1

# Page Suffix (if not already added)
if pageOpened:
    xmlOutput = xmlOutput + '  </icon_page' + str(currentPage) + '> ' + CRLF

# File end tag
xmlOutput = xmlOutput + '</strings_resources>   ' + CRLF

# Save the generated configuration file to the current directory
# Writing as a binary file solved some issues I experienced with
# line termination.
bytes = bytearray()
bytes.extend(xmlOutput.encode())
oFile = open(xmlDirPath + '/' + outputFileName, "bw")
oFile.write(bytes)
oFile.close()

# Output a summary
print('*** SUMMARY OF ACTIONS ***')
print('\"' + xmlDirPath + '/' + outputFileName + '\" created.')
print('Roms copied to \"' + exportGameDirPath + '\"')
print('Roms art images generated in \"' + imageDirPath + '\"')
print('Games found and Processed : ' + str(currentItem - 1))
print('Pages generated : ' + str(currentPage) + ' [up to ' + str(pageSize) + ' games per page]')

