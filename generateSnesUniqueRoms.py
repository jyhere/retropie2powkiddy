import sys, getopt, shutil, os, time, zipfile, re, zlib
from os.path import isfile, join, basename
from os import listdir

romPath = "/home/jyhere/Downloads/FULL Super Nintendo -- Famicom (GoodSNES 2 04)[GoodMerged]/FULL Super Nintendo -- Famicom (GoodSNES 2.04)[GoodMerged]"
targetDir = "/home/jyhere/GoodSNes Unique Roms"

# Set to True if you want zipped roms
compressRoms = True

FLAG_BETA = "(Beta)"
FLAG_JAP = "(J)"
FLAG_USA = "(U)"
FLAG_EURO = "(E)"
FLAG_FRE = "(F)"
FLAG_VERIFIED = "[!]"
ROM_EXTENSION = "smc"

try:
    os.mkdir(targetDir)
    print('Target directory ', targetDir, ' created.')
except FileExistsError:
    print('Target directory ', targetDir, ' already exists.')

gamesCount = len(listdir(romPath))
print("Found " + str(gamesCount) + " games.")
time.sleep(1)

for file in listdir(romPath):
    found = False
    filePath = join(romPath, file)

    # if filePath is a file, Game has only one rom
    if isfile(filePath):
        found = True
        #print('Found ' + file + ", copying... ", end='')
        if compressRoms:
            zipFileName = os.path.splitext(join(targetDir, file))[0] + '.zip'
            zipFile = zipfile.ZipFile(zipFileName, mode='w', compression=zipfile.ZIP_BZIP2, compresslevel=9)
            try:
                zipFile.write(filePath, basename(filePath))
            finally:
                zipFile.close()
        else:
            shutil.copy(filePath, join(targetDir, file))
        #print('OK')
        continue

    # filePath is a directiory. Game has many roms in this directory, we try to select one using this order of preference :
    # .*\([EUJF]\)( \(M[2-9]\))?( \(V[1-9]\.\d\))? \[!\]\.smc
    # https://regex101.com/r/aqjw1T/3
    # Verified FR > FR > Verified EUR > EUR > Verified US > US > Verified JAP >  JAP
    preferences = [
        ".*\(F\)( \(M[2-9]\))?( \(V[1-9]\.\d\))?( \(NP\))?( \(ST\))?( \(BS\))?( \(NSS\))?( \[!\])?\.smc",
        ".*\(E\)( \(M[2-9]\))?( \(V[1-9]\.\d\))?( \(NP\))?( \(ST\))?( \(BS\))?( \(NSS\))?( \[!\])?\.smc",
        ".*\(U\)( \(M[2-9]\))?( \(V[1-9]\.\d\))?( \(NP\))?( \(ST\))?( \(BS\))?( \(NSS\))?( \[!\])?\.smc",
        ".*\(J\)( \(M[2-9]\))?( \(V[1-9]\.\d\))?( \(NP\))?( \(ST\))?( \(BS\))?( \(NSS\))?( \[!\])?\.smc",
        ".*\(Beta\)( \(M[2-9]\))?( \(V[1-9]\.\d\))?( \(NP\))?( \(ST\))?( \(BS\))?( \(NSS\))?( \[!\])?\.smc",
    ]
    # preferences = [
    #     FLAG_FRE + ' ' + FLAG_VERIFIED + '.' + ROM_EXTENSION,
    #     FLAG_FRE + '.' + ROM_EXTENSION,
    #     FLAG_EURO + ' ' + FLAG_VERIFIED + '.' + ROM_EXTENSION,
    #     FLAG_EURO + '.' + ROM_EXTENSION,
    #     FLAG_USA + ' ' + FLAG_VERIFIED + '.' + ROM_EXTENSION,
    #     FLAG_USA + '.' + ROM_EXTENSION,
    #     FLAG_JAP + ' ' + FLAG_VERIFIED + '.' + ROM_EXTENSION,
    #     FLAG_JAP + '.' + ROM_EXTENSION,
    # ]
    for preference in preferences:
        for subFile in listdir(filePath):
            if re.match(preference, subFile):
                found = True
                #print('Found ' + file + ", copying... ", end='')
                if compressRoms:
                    zipFileName = os.path.splitext(join(targetDir, subFile))[0] + '.zip'
                    zipFile = zipfile.ZipFile(zipFileName, mode='w', compression=zipfile.ZIP_BZIP2, compresslevel=9)
                    try:
                        zipFile.write(join(filePath, subFile), subFile)
                    finally:
                        zipFile.close()
                else:
                    shutil.copy(join(filePath, subFile), join(targetDir, subFile))
                #print('OK')
                break
        if found:
            break

    if not found:
        print("NO MATCH FOUND for " + file)
        #time.sleep(2)