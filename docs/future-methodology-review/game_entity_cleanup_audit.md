# Game-Entity Cleanup Audit — Second-Pass Extension (after 169)

**Date:** 2026-08-24
**Inputs:** `bgg_research_population.parquet` 16627, `phase2-second-pass` 169 pruned (edition 153 + family 17 −1), surviving 16458 games (16458)
**Method:** Extended audit using richer BGG snapshot: `game_links` 43k (version/reimplementation/expansion/family), `families` (975 Game: families, 110 with >5), `title_clean`/`title`/`year`/`designer`/`weight`/`mechanics`/`is_reimplementation`/`description` where useful. Title keywords as signals, corroborated by `designer`/`year`±1, `families` Jaccard, `weight`≤0.2, `game_links` version, `title_clean`/Levenshtein. Keep more popular per group (not higher-residual). Do not remove every sequel/reimplementation — only same underlying game for hidden-gem discovery.

**Summary:** newly detected 100 (not in 169), already handled 169 (of 169), intentionally retained despite relationship 269 (distinct designs kept).

**Related parent game_id where applicable** (e.g., Small World Designer Edition 140135 → base 40692).

## Counts per rule

| Rule | Newly detected (remove) | Already handled (remove) | Intentionally retained |
|---|---|---|---|
| alternate_language | 0 | 0 | 2 |
| base_set | 0 | 0 | 3 |
| base_set_starter_set | 1 | 0 | 14 |
| bundle_collection | 1 | 0 | 10 |
| duplicate_title_clean | 0 | 0 | 227 |
| edition_bigbox | 0 | 153 | 0 |
| edition_extended | 97 | 0 | 0 |
| expansion_standalone | 0 | 0 | 1 |
| family_large | 0 | 0 | 6 |
| family_monikers_timesup | 0 | 16 | 0 |
| game_system | 0 | 0 | 5 |
| reprint_alternate_version | 1 | 0 | 1 |

**Total new to remove:** 100 unique games (1.00% + additional 0.61% of surviving 16458). Combined total pruned would be 269 (1.62% of 16627).

## Newly detected records (not in 169 already pruned)

| game_id | title | year | n_active | rule | reason | related_game_id | keeper title |
|---|---|---|---|---|---|---|---|
| 2288 | Blood Bowl (Second Edition) | 1988.0 | 1394 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 712.0 | Blood Bowl (Third Edition) |
| 3183 | Car Wars (Fifth Edition) | 2002.0 | 220 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;families_identical;title_levenshtein_0) | 2795.0 | Car Wars |
| 4928 | Clue: 50th Anniversary Edition | 1999.0 | 517 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;title_levenshtein_0) | 130592.0 | Clue |
| 12493 | Twilight Imperium: Third Edition | 2005.0 | 18382 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;title_levenshtein_0) | 233078.0 | Twilight Imperium: Fourth Edition |
| 13362 | Warhammer 40,000 (Fourth Edition) | 2004.0 | 1084 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;title_levenshtein_0) | 2162.0 | Warhammer 40,000 (Third Edition) |
| 15509 | Scene It? Movie Deluxe | 2005.0 | 195 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 32688.0 | Scene It? Movie Second Edition |
| 23010 | Risk: 40th Anniversary Collector's Edition | 1999.0 | 680 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 181.0 | Risk |
| 26055 | Twilight Imperium: Second Edition | 2000.0 | 547 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (families_identical;title_levenshtein_0) | 233078.0 | Twilight Imperium: Fourth Edition |
| 26138 | Dungeon Twister Collectors Box | 2006.0 | 108 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.4;families_identical;title_levenshtein_0) | 12995.0 | Dungeon Twister |
| 27624 | Pictionary: 15th Anniversary | 2000.0 | 153 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;title_levenshtein_0) | 2281.0 | Pictionary |
| 27626 | Pictionary: 20th Anniversary | 2005.0 | 129 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;title_levenshtein_0) | 2281.0 | Pictionary |
| 31198 | War at Sea (Third Edition) | 2007.0 | 114 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 1431.0 | War at Sea (Second Edition) |
| 32682 | Scene It? Disney Second Edition | 2007.0 | 168 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;families_identical;mechanics_identical;title_levenshtein_0) | 15830.0 | Scene It? Disney |
| 32683 | Scene It? Harry Potter Second Edition | 2007.0 | 143 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;families_identical;mechanics_identical;title_levenshtein_0) | 19578.0 | Scene It? Harry Potter |
| 33624 | Trivial Pursuit: Deluxe | 2007.0 | 181 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;families_identical;title_levenshtein_0) | 4492.0 | Trivial Pursuit: 20th Anniversary Edition |
| 37061 | Star Fleet Battles (Designer's Edition) | 1979.0 | 118 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.4;families_identical;title_levenshtein_0) | 1589.0 | Star Fleet Battles |
| 37988 | Trivial Pursuit: 25th Anniversary Edition | 2008.0 | 324 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;families_identical;mechanics_identical;title_levenshtein_0) | 4492.0 | Trivial Pursuit: 20th Anniversary Edition |
| 59061 | Drakon | 2001.0 | 173 | reprint_alternate_version | reprint_title_lev≤2_designer_year±1_families_identical (lv=2) | 61269.0 | Drakon (Second Edition) |
| 61269 | Drakon (Second Edition) | 2002.0 | 416 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;title_levenshtein_0) | 23107.0 | Drakon (Third Edition) |
| 63091 | Space Hulk (Second Edition) | 1996.0 | 623 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;title_levenshtein_0) | 54625.0 | Space Hulk (Third Edition) |
| 88827 | Battle Cry: 150th Civil War Anniversary Edition | 2010.0 | 1200 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_similar;title_levenshtein_0) | 551.0 | Battle Cry |
| 123607 | Puzzle Strike: Third Edition | 2012.0 | 1815 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;title_levenshtein_0) | 67928.0 | Puzzle Strike |
| 126613 | Warhammer 40,000 (Sixth Edition) | 2012.0 | 392 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;weight_within_0.2;mechanics_identical;title_levenshtein_0) | 37165.0 | Warhammer 40,000 (Fifth Edition) |
| 128666 | BANG! 10th Anniversary | 2012.0 | 369 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 3955.0 | BANG! |
| 135840 | Napoleon at Leipzig (Fifth Edition) | 2013.0 | 135 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;title_levenshtein_0) | 10183.0 | Napoleon at Leipzig |
| 144568 | Dawn of the Zeds (Second Edition) | 2013.0 | 645 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;title_levenshtein_0) | 175095.0 | Dawn of the Zeds (Third Edition) |
| 146439 | BattleLore: Second Edition | 2013.0 | 6269 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;title_levenshtein_0) | 25417.0 | BattleLore |
| 147170 | El Grande Decennial Edition | 2006.0 | 978 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 93.0 | El Grande |
| 157820 | Escape: The Curse of the Temple – Big Box | 2014.0 | 1654 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;title_levenshtein_0) | 113294.0 | Escape: The Curse of the Temple |
| 158098 | Star Fleet Battles (Commander's Edition) | 1983.0 | 95 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;title_levenshtein_0) | 1589.0 | Star Fleet Battles |
| 159517 | Get Bit! Collectors Edition | 2014.0 | 166 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_similar;title_levenshtein_0) | 30539.0 | Get Bit! |
| 160069 | Ticket to Ride: 10th Anniversary | 2014.0 | 5355 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 9209.0 | Ticket to Ride |
| 165838 | Space Hulk (Fourth Edition) | 2014.0 | 1734 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 54625.0 | Space Hulk (Third Edition) |
| 171630 | Drakon (Fourth Edition) | 2015.0 | 1096 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;mechanics_identical;title_levenshtein_0) | 23107.0 | Drakon (Third Edition) |
| 172307 | The Game of Life (2013- Editions) | 2013.0 | 584 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;title_levenshtein_0) | 2921.0 | The Game of Life |
| 173637 | Monopoly:  80th Anniversary Edition | 2015.0 | 165 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.4;families_identical;mechanics_identical;title_levenshtein_0) | 7098.0 | Monopoly: Deluxe Edition |
| 193670 | Darkest Night: Second Edition | 2018.0 | 708 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 128445.0 | Darkest Night |
| 195503 | City of Iron: Second Edition | 2016.0 | 1275 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;title_levenshtein_0) | 123499.0 | City of Iron |
| 196326 | Love Letter: Premium Edition | 2016.0 | 6017 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;weight_within_0.2;families_identical;title_levenshtein_0) | 129622.0 | Love Letter |
| 196712 | Battlestations: Second Edition | 2017.0 | 254 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 12350.0 | Battlestations |
| 213984 | Notre Dame: 10th Anniversary | 2017.0 | 2360 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 25554.0 | Notre Dame |
| 214000 | In the Year of the Dragon: 10th Anniversary | 2017.0 | 2100 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_similar;title_levenshtein_0) | 31594.0 | In the Year of the Dragon |
| 229892 | Container: 10th Anniversary Jumbo Edition! | 2018.0 | 2070 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.4;families_identical;title_levenshtein_0) | 26990.0 | Container |
| 242722 | Here I Stand: 500th Anniversary Edition | 2017.0 | 1181 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_similar;title_levenshtein_0) | 17392.0 | Here I Stand |
| 253149 | Wok Star (3rd Edition) | 2018.0 | 178 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;mechanics_identical;title_levenshtein_0) | 71655.0 | Wok Star |
| 257089 | Big Trouble in Little China: The Game – Deluxe Edition | 2018.0 | 141 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.2;families_similar;title_levenshtein_0) | 204286.0 | Big Trouble in Little China: The Game |
| 260126 | New Salem: Second Edition | 2019.0 | 102 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 161757.0 | New Salem |
| 261424 | Big City: 20th Anniversary Jumbo Edition! | 2019.0 | 329 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;title_levenshtein_0) | 70.0 | Big City |
| 268098 | Warhammer: The Game of Fantasy Battles (7th Edition) | 2006.0 | 101 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;families_identical;title_levenshtein_0) | 130552.0 | Warhammer: The Game of Fantasy Battles (8th Edition) |
| 268159 | Warhammer: The Game of Fantasy Battles (6th Edition) | 2000.0 | 180 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;title_levenshtein_0) | 130552.0 | Warhammer: The Game of Fantasy Battles (8th Edition) |
| 268183 | Warhammer: The Game of Fantasy Battles (5th Edition) | 1996.0 | 101 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (families_identical;title_levenshtein_0) | 130552.0 | Warhammer: The Game of Fantasy Battles (8th Edition) |
| 274466 | Valley of the Kings: Premium Edition | 2019.0 | 1310 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;title_levenshtein_0) | 150999.0 | Valley of the Kings |
| 276502 | Roads & Boats: 20th Anniversary Edition | 2019.0 | 513 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;mechanics_identical;title_levenshtein_0) | 875.0 | Roads & Boats |
| 281073 | Cat Lady: Premium Edition | 2019.0 | 477 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;mechanics_identical;title_levenshtein_0) | 228504.0 | Cat Lady |
| 291828 | Car Wars (Sixth Edition) | 2021.0 | 180 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (families_identical;title_levenshtein_0) | 2795.0 | Car Wars |
| 295260 | It's a Wonderful World: Heritage Edition | 2019.0 | 921 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.2;families_identical;title_levenshtein_0) | 271324.0 | It's a Wonderful World |
| 299971 | Island Siege: Second Edition | 2021.0 | 125 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_similar;mechanics_identical;title_levenshtein_0) | 133405.0 | Island Siege |
| 305668 | Catan: 25th Anniversary Edition | 2020.0 | 282 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 13.0 | CATAN |
| 313010 | Cosmic Encounter: 42nd Anniversary Edition | 2018.0 | 1360 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 39463.0 | Cosmic Encounter |
| 317519 | Frostgrave: Second Edition | 2020.0 | 302 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 177354.0 | Frostgrave |
| 321757 | Monza 20th Anniversary | 2020.0 | 188 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;title_levenshtein_0) | 4209.0 | Monza |
| 327890 | Creature Comforts (Kickstarter Edition) | 2022.0 | 932 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.2;title_levenshtein_0) | 304051.0 | Creature Comforts |
| 329841 | Ticket to Ride: Europe – 15th Anniversary | 2021.0 | 4003 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 14996.0 | Ticket to Ride: Europe |
| 329954 | Carcassonne: 20th Anniversary Edition | 2021.0 | 2589 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 822.0 | Carcassonne |
| 332398 | Everdell: The Complete Collection | 2022.0 | 3328 | bundle_collection | bundle_collection_same_underlying_game_keep_base (designer/weight corroborated) | 199792.0 | Everdell |
| 333144 | Stronghold: Undead (Second Edition) | 2021.0 | 146 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;families_similar;mechanics_identical;title_levenshtein_0) | 206593.0 | Stronghold: Undead (Second Edition) – Kickstarter Edition |
| 334310 | Hellboy: The Board Game – Deluxe Edition | 2019.0 | 160 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.4;families_identical;mechanics_identical;title_levenshtein_0) | 243759.0 | Hellboy: The Board Game |
| 334931 | Robinson Crusoe: Adventures on the Cursed Island – Collector | 2024.0 | 591 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 121921.0 | Robinson Crusoe: Adventures on the Cursed Island |
| 339263 | Summoner Wars (Second Edition): Starter Set | 2021.0 | 472 | base_set_starter_set | starter_set_component_of_parent_system_keep_parent (weight/year/designer corroborated, game_links parent) | 332800.0 | Summoner Wars (Second Edition) |
| 341080 | Warhammer Age of Sigmar (Third Edition): Core Book | 2021.0 | 117 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;title_levenshtein_0) | 256422.0 | Warhammer Age of Sigmar (Second Edition) Core Rules |
| 341169 | Great Western Trail: Second Edition | 2021.0 | 14309 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;title_levenshtein_0) | 193738.0 | Great Western Trail |
| 351605 | Bohnanza: 25th Anniversary Edition | 2022.0 | 1411 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 11.0 | Bohnanza |
| 354568 | Amun-Re: 20th Anniversary Edition | 2023.0 | 679 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_similar;title_levenshtein_0) | 5404.0 | Amun-Re |
| 357028 | Dungeon Fighter: Second Edition | 2021.0 | 1356 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 102548.0 | Dungeon Fighter |
| 357813 | 51st State: Ultimate Edition (Gamefound Edition) | 2023.0 | 98 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_1;weight_within_0.2;families_identical;title_levenshtein_0) | 357726.0 | 51st State: Ultimate Edition |
| 358808 | Smash Up: 10th Anniversary | 2022.0 | 118 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 122522.0 | Smash Up |
| 361284 | Sleeping Gods: Distant Skies (Gamefound Edition) | 2023.0 | 127 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;families_identical;title_levenshtein_0) | 358320.0 | Sleeping Gods: Distant Skies |
| 366012 | Henchmania: Second Edition | 2024.0 | 65 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;mechanics_identical;title_levenshtein_0) | 204817.0 | Henchmania |
| 369103 | Dead by Daylight: The Board Game – Collector's Edition | 2023.0 | 193 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;mechanics_identical;title_levenshtein_0) | 358246.0 | Dead by Daylight: The Board Game |
| 371486 | Tainted Grail: Kings of Ruin (Gamefound Edition) | 2024.0 | 37 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_1;weight_within_0.4;families_identical;title_levenshtein_0) | 360366.0 | Tainted Grail: Kings of Ruin |
| 371956 | Fall of the Mountain King (Kickstarter Edition) | 2022.0 | 135 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.2;families_similar;title_levenshtein_0) | 334829.0 | Fall of the Mountain King |
| 372343 | Eleven: Football Manager Board Game (Gamefound Edition) | 2022.0 | 92 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 329716.0 | Eleven: Football Manager Board Game |
| 373597 | The Witcher: Old World – Big Box | 2023.0 | 136 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.4;title_levenshtein_0) | 331106.0 | The Witcher: Old World |
| 378877 | Power Plants (Kickstarter Edition) | 2022.0 | 135 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.4;families_similar;mechanics_identical;title_levenshtein_0) | 341974.0 | Power Plants |
| 381715 | Teotihuacan: City of Gods – Deluxe Master Set | 2024.0 | 307 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;title_levenshtein_0) | 229853.0 | Teotihuacan: City of Gods |
| 385643 | Paperback: 10th Anniversary Edition | 2024.0 | 156 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;title_levenshtein_0) | 141572.0 | Paperback |
| 390478 | Gloomhaven: Second Edition | 2025.0 | 143 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;title_levenshtein_0) | 174430.0 | Gloomhaven |
| 391288 | Firefly: The Game – 10th Anniversary Collector's Edition | 2024.0 | 345 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 138161.0 | Firefly: The Game |
| 406321 | Take 5: 30th Anniversary Edition | 2024.0 | 256 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;families_identical;title_levenshtein_0) | 432.0 | Take 5 |
| 410292 | Hunted: Kobayashi Tower (2nd Edition) | 2024.0 | 76 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 289566.0 | Hunted: Kobayashi Tower |
| 417219 | I C E: Second Edition | 2026.0 | 26 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;title_levenshtein_0) | 306482.0 | I C E |
| 420240 | Hunted: Mining Colony 415 (2nd Edition) | 2024.0 | 48 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;families_identical;title_levenshtein_0) | 289565.0 | Hunted: Mining Colony 415 |
| 420361 | Trekking the World: Second Edition | 2024.0 | 248 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (year_within_5;weight_within_0.2;title_levenshtein_0) | 300442.0 | Trekking the World |
| 421529 | Barony (Royal Edition) | 2025.0 | 10 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;title_levenshtein_0) | 167513.0 | Barony |
| 422426 | Foundations of Rome (Maximus Edition) | 2024.0 | 42 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_5;weight_within_0.2;mechanics_identical;title_levenshtein_0) | 284189.0 | Foundations of Rome |
| 424972 | Sushi Go! 10th Anniversary Edition | 2024.0 | 67 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_identical;mechanics_identical;title_levenshtein_0) | 133473.0 | Sushi Go! |
| 425064 | Kingsburg (Third Edition) | 2024.0 | 28 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.4;mechanics_identical;title_levenshtein_0) | 199966.0 | Kingsburg (Second Edition) |
| 426275 | Dungeon Kart (Gold Tier Kickstarter Edition) | 2024.0 | 50 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;year_within_1;weight_within_0.2;families_identical;title_levenshtein_0) | 398032.0 | Dungeon Kart |
| 426467 | Trekking the National Parks: Third Edition | 2024.0 | 44 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (designer_identical;weight_within_0.2;families_similar;mechanics_identical;title_levenshtein_0) | 255708.0 | Trekking the National Parks: Second Edition |
| 432392 | Tales of the Arabian Nights: 40th Anniversary | 2026.0 | 0 | edition_extended | edition_deluxe_title_clean_duplicate_keep_more_popular (weight_within_0.2;title_levenshtein_0) | 34119.0 | Tales of the Arabian Nights |

## Records already handled by existing 169-game cleanup (show overlap)

Existing 169 pruned: edition 153 + family 17 −1 overlap =169. Overlap with new detection: 0 (should be 0, new are distinct). Jaccard vs original 16627 = 0.9898 surviving.

| game_id | title | year | n_active | rule | reason | related_game_id |
|---|---|---|---|---|---|---|
| 793 | Yahtzee Deluxe Poker | 1994.0 | 560 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=yahtzee) | 2243.0 |
| 10707 | Hacker: Deluxe Edition | 2001.0 | 312 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=hacker) | 1250.0 |
| 22477 | Deluxe Camping | 2006.0 | 135 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=) | 12304.0 |
| 33495 | Time's Up! Édition purple | 2007.0 | 356 | family_monikers_timesup | family_timesup_keep_base (Game: Time's Up!) | 1353.0 |
| 35052 | Axis & Allies Anniversary Edition | 2008.0 | 2874 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=axis & allies) | 98.0 |
| 36553 | Time's Up! Title Recall! | 2008.0 | 3629 | family_monikers_timesup | family_timesup_keep_base (Game: Time's Up!) | 1353.0 |
| 37141 | Time's Up! Deluxe | 2008.0 | 1024 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=time's up!) | 1353.0 |
| 38713 | Time's Up! Edición Amarilla | 2008.0 | 1622 | family_monikers_timesup | family_timesup_keep_base (Game: Time's Up!) | 1353.0 |
| 39103 | Jungle Speed: Deluxe | 2008.0 | 256 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=jungle speed) | 8098.0 |
| 42627 | MidEvil Deluxe | 2009.0 | 115 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=midevil) | 15738.0 |
| 45358 | Alhambra: Big Box | 2009.0 | 4622 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=alhambra) | 6249.0 |
| 46158 | Time's Up! Academy | 2009.0 | 575 | family_monikers_timesup | family_timesup_keep_base (Game: Time's Up!) | 1353.0 |
| 47410 | Catan Dice Game Deluxe Edition | 2009.0 | 92 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=catan dice game) | 27710.0 |
| 57660 | Time's Up! Edición Azul | 2006.0 | 1365 | family_monikers_timesup | family_timesup_keep_base (Game: Time's Up!) | 1353.0 |
| 59602 | Upwords Deluxe | 2007.0 | 128 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=upwords) | 1515.0 |
| 60153 | War of the Ring Collector's Edition | 2010.0 | 1056 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=war of the ring) | 9609.0 |
| 70653 | Monopoly: Nintendo Collector's Edition | 2010.0 | 169 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=monopoly: nintendo) | 24000.0 |
| 88126 | Time's Up! Family | 2010.0 | 969 | family_monikers_timesup | family_timesup_keep_base (Game: Time's Up!) | 1353.0 |
| 139991 | Fresco: Big Box | 2014.0 | 1669 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=fresco) | 66188.0 |
| 139993 | Kingdom Builder: Big Box | 2014.0 | 1251 | edition_bigbox | edition_deluxe_title_clean_duplicate_keep_more_popular (base=kingdom builder) | 107529.0 |

*Total already handled rows shown 20 of 169; full list in CSV.*

## Records intentionally retained despite relationship (distinct designs kept)

Examples where `Pandemic` vs `Pandemic Legacy` (weight 2.40 vs 2.83, Legacy adds Campaign, year gap 8) — distinct, or `Brass: Birmingham` vs `Brass: Lancashire` (distinct weight/year/mechanics) — must stay separate per task.

| game_id | title | year | n_active | rule | reason | related_game_id | keeper title |
|---|---|---|---|---|---|---|---|
| 15 | Cosmic Encounter | 1977.0 | 3862 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 39463.0 | Cosmic Encounter |
| 34 | Arkham Horror | 1987.0 | 541 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 15987.0 | Arkham Horror |
| 97 | Conquest of the Empire | 1984.0 | 1021 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 17710.0 | Conquest of the Empire |
| 121 | Dune | 1979.0 | 5716 | duplicate_title_clean | intentionally_retained_duplicate_moderate_not_strict (year_close=False, fam_identical=False, lv=0) | 283355.0 | Dune |
| 278 | Catan Card Game | 1996.0 | 13840 | family_large | intentionally_retained_family_Catan_distinct_design (year/weight distinct) | 13.0 | CATAN |
| 304 | Evergreen | 1999.0 | 364 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 363307.0 | Evergreen |
| 414 | Around the World in 80 Days | 1986.0 | 341 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 12005.0 | Around the World in 80 Days |
| 426 | The Battle of the Bulge | 1981.0 | 408 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 16444.0 | The Battle of the Bulge |
| 463 | Magic: The Gathering | 1993.0 | 38914 | game_system | intentionally_retained_system_entry_distinct_design (collectible card game system, distinct for hidden-gem) | nan |  |
| 565 | Port Royal | 2000.0 | 153 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 156009.0 | Port Royal |
| 571 | Papua | 1992.0 | 96 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 255034.0 | Papua |
| 573 | Grand Prix | 1975.0 | 94 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 163163.0 | Grand Prix |
| 680 | Dune | 1984.0 | 353 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 283355.0 | Dune |
| 690 | Singapore | 1984.0 | 101 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 103235.0 | Singapore |
| 711 | Elfenroads | 1992.0 | 306 | duplicate_title_clean | intentionally_retained_duplicate_moderate_not_strict (year_close=False, fam_identical=False, lv=0) | 180325.0 | Elfenroads |
| 716 | Pizza Party | 1987.0 | 153 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 144579.0 | Pizza Party |
| 731 | Escape from New York | 1981.0 | 101 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 362723.0 | Escape from New York |
| 736 | San Francisco | 2000.0 | 328 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 357271.0 | San Francisco |
| 741 | Trajan | 1991.0 | 124 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 102680.0 | Trajan |
| 788 | Tales of the Arabian Nights | 1985.0 | 815 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 34119.0 | Tales of the Arabian Nights |
| 859 | Illuminati | 1982.0 | 2613 | duplicate_title_clean | intentionally_retained_duplicate_moderate_not_strict (year_close=False, fam_identical=False, lv=0) | 28.0 | Illuminati |
| 927 | Lift Off | 2000.0 | 166 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 260757.0 | Lift Off |
| 954 | Pony Express | 1991.0 | 125 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 42490.0 | Pony Express |
| 1017 | Fresh Fish | 1997.0 | 995 | duplicate_title_clean | intentionally_retained_duplicate_moderate_not_strict (year_close=False, fam_identical=False, lv=0) | 164698.0 | Fresh Fish |
| 1143 | Warrior Knights | 1985.0 | 571 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 22038.0 | Warrior Knights |
| 1205 | Luxor | 2001.0 | 309 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 245643.0 | Luxor |
| 1225 | Quest | 1984.0 | 154 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 316287.0 | Quest |
| 1323 | Cry Havoc | 1981.0 | 726 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 192457.0 | Cry Havoc |
| 1346 | Crazy Race | 2001.0 | 152 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 217176.0 | Crazy Race |
| 1352 | Bali | 2001.0 | 250 | duplicate_title_clean | intentionally_retained_duplicate_distinct_designer | 233956.0 | Bali |

*Total intentionally retained 268; full list in CSV.*

## Evidence columns used per decision

- `game_links` rel=version/reimplementation/expansion/family, other_id/other_name 43,196 rows (33,483 filtered)
- `families` JSON array (975 Game: families, 110 with >5) via `bgg_research_population.families`
- `reimplementation`/`version` metadata (`is_reimplementation`, `reimplements_name`, `num_implementations`)
- `titles` / `title_clean`, `year`, `designer`, `weight`, `mechanics`, `description`/`metadata` where useful
- `product`/`system` relationships (e.g., System in families)
- `title_clean` exact duplicates or Levenshtein ≤2 after stripping edition suffixes, year ±1, designer identical, families identical

*Title keywords used as signals, not final rule: Big Box alone not enough; require game_links rel + designer/year + families corroboration.*

## Provenance

- Script: `scripts/36_second_pass_audit_extension.py` (bounded 4GB/3 threads, copy-once to `scratch/second-pass-audit`)
- Scratch: `scratch/second-pass-audit` (16458 surviving games, 16564 active games with ≥1 rating)
- Outputs: `docs/future-methodology-review/game_entity_cleanup_audit.csv` (machine-readable) + this MD
- Already handled provenance: `data/processed/phase2-second-pass/pruned_lists/` + `comparison_table.json`
