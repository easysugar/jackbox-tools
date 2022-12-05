# jackbox-tools

Jackbox tools for translating

This repository contains tools for translating Jackbox games, including:

* encoding/decoding games files
* integration with Crowdin
* calculation of top contributors
* translation report generation
* document generation of translations with original audio for voice actors
* preparation of games releases

## Settings

All tools settings are stored at `settings/` directory.  
It contains API KEY for Crowdin, games paths, etc.

## Use cases

#### Download the latest game translation from Crowdin & create release

1. Go to `scripts/` directory
2. Run `download_translations.py`
3. Run `release_game.py`

After that you will get a new version of game files with translations at your `RELEASE_PATH` directory. 
