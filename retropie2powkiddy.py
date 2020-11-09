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

import sys, getopt, shutil, os, pathlib, os.path
from os import path
from PIL import Image
from lxml import etree
from xml.sax.saxutils import escape

retroPieTargetSystem = powKiddyTargetSystem = ''


def main(argv):
    global retroPieTargetSystem, powKiddyTargetSystem
    try:
        opts, args = getopt.getopt(argv, "hr:p:", ["retropiesystem=", "powkiddysystem="])
    except getopt.GetoptError:
        print('retropie2powkiddy.py -r <retropiesystem> -p <powkiddysystem>')
        print('Supported <powkiddysystem> values : CPS, FBA, FC, GB')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -r <retropiesystem> -p <powkiddysystem>')
            sys.exit()
        elif opt in ("-r", "--retropiesystem"):
            retroPieTargetSystem = arg
        elif opt in ("-p", "--powkiddysystem"):
            powKiddyTargetSystem = arg
    print('RetroPie system is "' + retroPieTargetSystem)
    print('powkiddy system is "' + powKiddyTargetSystem)


if __name__ == "__main__":
    main(sys.argv[1:])


# ====== IMPORTANT =======
# Root path of retropie installation
retroPieRootPath = '/opt/retropie'

# Path for retropie roms
retroPieRomsPath = '/home/jyhere/RetroPie/roms'

# Targeted system
retroPieTargetSystem = 'cps'

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
exportGameSubdir = 'roms'
# Name of the directory which will contain your converted images (converted from .jpg to .png) in
# a filename to match your game (roms).
imageDirName = 'art'
# No art file name (Image that is displayed if no boxart can be found for the game)
noArtFilename = 'no_art.png'

# No need to change anything below this - I don't think...
CRLF = '\r\n'

retroPieGameListXml = retroPieRootPath + '/configs/all/emulationstation/gamelists/' + retroPieTargetSystem + '/gamelist.xml'
retroPieGameListImagesPath = retroPieRootPath + '/configs/all/emulationstation/downloaded_images/' + retroPieTargetSystem
retroPieGameListRomsPath = retroPieRomsPath + '/' + retroPieTargetSystem

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
        hasPath = hasName = False
        for gameProperty in gameProperties:
            if gameProperty.tag == 'path':
                tmpPath = gameProperty.text
                hasPath = True
            if gameProperty.tag == 'name':
                gameName = gameProperty.text
                hasName = True

        if hasPath and hasName:
            archiveName = tmpPath.lstrip('./')
            iFileExtensionIndex = tmpPath.rindex('.')
            gameFileExtension = tmpPath[iFileExtensionIndex:]
            shortName = archiveName.replace(gameFileExtension, '')
            gameList[shortName] = {'name': gameName, 'file': archiveName}

gameListCount = len(gameList)
print(gameListCount)

imageDirName = retroPieTargetSystem + '/' + imageDirName
exportGameSubdir = retroPieTargetSystem + '/' + exportGameSubdir
sDestinationImagePath = imageDirName + '/'

# Create system directory
try:
    os.mkdir(retroPieTargetSystem)
except FileExistsError:
    pass

# If Games are found in the XML
if createArtImages and gameListCount > 0:
    # Create image directory
    try:
        os.mkdir(imageDirName)
        print('Image Directory ', imageDirName, ' created.')
    except FileExistsError:
        print('Image Directory ', imageDirName, ' already exists.')

try:
    os.mkdir(exportGameSubdir)
    print('Game Directory ', exportGameSubdir, ' created.')
except FileExistsError:
    print('Game Directory ', exportGameSubdir, ' already exists.')

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

for gameShortName, gameData in gameList.items():

    print(gameShortName + '... ', end='')

    # Page header
    if currentItemOnPage == 0:
        xmlOutput = xmlOutput + '  <icon_page' + str(currentPage) + '> ' + CRLF
        pageOpened = True

    # Copying roms
    sourceFilePathName = retroPieGameListRomsPath + '/' + gameData['file']
    newFilePathName = exportGameSubdir + '/' + gameData['file']
    shutil.copyfile(sourceFilePathName, newFilePathName)

    # Copy Image file with the new name
    if createArtImages:
        sourceImageFile = retroPieGameListImagesPath + '/' + gameShortName + '-image'
        # convert art if format is JPG
        sourceImageFileExistsJPG = path.exists(sourceImageFile + '.jpg')
        sourceImageFileExistsPNG = path.exists(sourceImageFile + '.png')
        if sourceImageFileExistsJPG:
            # Convert .jpg artwork to .png (needed for Powkiddy A12)
            destImageFile = sDestinationImagePath + gameShortName + '.png'
            img = Image.open(sourceImageFile + '.jpg')
            img.save(destImageFile)
        elif sourceImageFileExistsPNG:
            destImageFile = sDestinationImagePath + '/' + gameShortName + '.png'
            shutil.copyfile(sourceImageFile + '.png', destImageFile)
        elif createNoArtImage:
            # If unable to copy, use default image (you can customize this, if you want)
            sourceImageFile = noArtFilename
            destImageFile = sDestinationImagePath + '/' + gameShortName + '.png'
            shutil.copyfile(sourceImageFile, destImageFile)

        xmlOutput = xmlOutput + '    <icon' + str(currentItemOnPage) + '_para  name=\"' + str(currentItem) + '.' + escape(gameData['name']) + '\" game_path=\"' + gameData['file'] + '\"></icon' + str(currentItemOnPage) + '_para> ' + CRLF

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
oFile = open(retroPieTargetSystem + '/' + outputFileName, "bw")
oFile.write(bytes)
oFile.close()

# Output a summary
print('*** SUMMARY OF ACTIONS ***')
print('\"' + retroPieTargetSystem + '/' + outputFileName + '\" created.')
print('Games found and Processed : ' + str(currentItem - 1))
print('Pages generated : ' + str(currentPage) + ' [up to ' + str(pageSize) + ' games per page]')

