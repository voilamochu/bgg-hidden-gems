# Phase 2 SQLite Database Inventory

**Discovery status:** schema/data inventory only. No substantive rating or audience analysis was performed, and `data/raw/bgg.sqlite` was opened read-only.

## Database-level facts

- File: `data/raw/bgg.sqlite`, approximately **9.0 GB**.
- SQLite 3.46.1; UTF-8; 4,096-byte pages; 2,335,194 pages; 3,168 freelist pages.
- No declared foreign keys (`PRAGMA foreign_keys=0`; `PRAGMA foreign_key_list` is empty for every application table). Relationships therefore depend on matching IDs and are not database-enforced.
- The database contains 11 application tables and the internal `sqlite_stat1` table.

## Tables, row counts, and roles

| Table | Rows | Main role and schema | Declared key |
|---|---:|---|---|
| `games` | 161,404 | Browse/game listing: `rank`, `game_id`, `title`, `description`, `year`, `geek_rating`, `avg_rating`, `voters`, `link`, `thumbnail` | No declared PK; unique index on non-null `game_id` |
| `game_attrs` | 21,925 | Detailed game metadata and aggregate counts: `game_id`, name/year/player/time/age/language fields, ratings and standard deviation, user-rating/comment/owned/want/wish counts, alternate/expansion/implementation counts, reimplementation/kickstarted flags, family, image, source | PK `game_id` |
| `game_links` | 43,196 | Game-to-game relationships: `game_id`, `rel`, `other_id`, `other_name` | Composite PK (`game_id`, `rel`, `other_id`) |
| `game_ranks` | 34,513 | Category-specific ranks: `game_id`, `category`, `rank`, `source` | Composite PK (`game_id`, `category`) |
| `game_tags` | 276,045 | Tag metadata: `game_id`, `tag_type`, `tag` | Composite PK (`game_id`, `tag_type`, `tag`) |
| `rating_dist` | 485,707 | Game-level rating histogram: `game_id`, `rating_value`, `n` | Composite PK (`game_id`, `rating_value`) |
| `weights` | 22,329 | Complexity/weight data and source: `game_id`, `weight`, `num_votes`, `source`, name/year, `in_games` | PK `game_id` |
| `user_ratings` | 18,942,215 | Compact individual ratings: `game_id`, `rating`, `username` | No declared key |
| `reviews` | 29,618,326 | Review/rating records: `game_id`, `reviewid`, `user_pseudouserid`, `comment`, `comment_tstamp`, `rating`, `rating_tstamp`, `postdate` | No declared key |
| `collections` | 29,618,326 | User-game collection/status records: `game_id`, `reviewid`, `user_pseudouserid`, `own`, `status_tstamp`, `wishlistpriority`, `wanttoplay`, `preordered`, `prevowned`, `wishlist`, `want`, `wanttobuy`, `fortrade` | No declared key |
| `users` | 606,497 | Pseudonymous user/profile data: `user_pseudouserid`, `state`, `country`, and five message-board name/description/timestamp triplets (`mb0`–`mb4`) | No declared key; unique index on `user_pseudouserid` |

## Indexes

- `games`: unique `ix_games_game_id(game_id)`; `ix_games_rank(rank)`; `ix_games_geek(geek_rating)`; `ix_games_year(year)`.
- `game_attrs`: `ix_attrs_year(year)`; the primary key supplies the `game_id` index.
- `game_links`: `ix_links_other(other_id)` plus the composite-PK index.
- `game_ranks`: `ix_ranks_rank(category, rank)` plus the composite-PK index.
- `game_tags`: `ix_tags_tag(tag_type, tag)` plus the composite-PK index.
- `rating_dist`: composite-PK index.
- `weights`: `ix_weights_weight(weight)` plus the primary-key index.
- `reviews`: `ix_rev_game(game_id)`, `ix_rev_user(user_pseudouserid)`, `ix_rev_rating(rating)`.
- `collections`: `ix_coll_game(game_id)`, `ix_coll_user(user_pseudouserid)`.
- `user_ratings`: `ix_ur_game(game_id)`, `ix_ur_user(username)`.
- `users`: unique `ix_users_id(user_pseudouserid)` and `ix_users_country(country)`.

## User, rating, and timestamp evidence

### Individual ratings

`user_ratings` is an individual-rating table in shape: 18.94M rows, 21,925 games, 411,375 distinct `username` values, no null game/user/rating fields, and rating values from 0.0001 to 10.0. It has no timestamp, review ID, comment, or user-profile key beyond `username`.

`reviews` is a second, richer individual-record table: 29.62M rows, 103,084 games, 606,497 distinct `user_pseudouserid` values, and 29,617,496 distinct `reviewid` values. It contains **26,924,709 non-null ratings**. It therefore supports user-game-rating records, but it is review-level data rather than a declared one-row-per-user-game rating table; duplicate/user-game cardinality still needs a separate audit.

### Rating timestamps and history

`reviews.rating_tstamp` is populated for **26,924,708** rows and ranges from **2001-05-29 19:28:36** to **2025-02-10 09:50:48**. `comment_tstamp` is populated for **6,264,799** rows and ranges from **2001-05-30 13:55:16** to **2025-02-10 10:52:48**. `postdate` is populated for **29,602,822** rows and ranges from **2001-05-29 19:25:21** to **2025-02-10 10:34:24**.

These are timestamps attached to records, not an explicit rating-change history. There is no observed version number, old/new rating pair, event table, or documented guarantee that the timestamp captures rating creation rather than another scrape/application event. Temporal analyses will need to establish the semantics and handle the small amount of missing timestamp data.

### User participation and collection evidence

`collections` has the same row count and the same distinct game/user/review-ID counts as `reviews`: 103,084 games, 606,497 users, and 29,617,496 review IDs. This strongly suggests a paired extraction keyed conceptually by game/review/user, but no foreign key or uniqueness constraint proves a one-to-one join. `status_tstamp` is populated for 21,061,870 rows, ranges from **2010-10-26 18:23:34** to **2025-02-10 10:34:24**, and the table records current/status flags for ownership, want-to-play, preorder, previously owned, wishlist, want, want-to-buy, and for-trade.

This is useful evidence of stated collection intent and participation-related status. It is not direct evidence of exposure, actual play, sales, or the full set of people who encountered a game but did not rate it. The flags appear as one status record per row, not a documented longitudinal status history.

### User identity and attributes

All 606,497 `reviews.user_pseudouserid` values match the unique IDs in `users`; the collection user IDs also match. `users` has no null user IDs, 195,460 null countries, and 242 distinct country values. It includes state/country plus up to five message-board records and timestamps, but no explicit demographics, play counts, exposure, purchase history, or rater-credibility field.

`user_ratings.username` has **zero** matches to `users.user_pseudouserid` in the database. The compact rating table therefore cannot currently be joined to the pseudonymous user/profile/collection path through the exposed identifiers. Whether a missing mapping exists outside this dump is unknown.

## Game-table relationships and coverage

- All **21,925** distinct `user_ratings.game_id` values occur in `game_attrs`.
- `reviews` covers **103,084** distinct game IDs, of which **21,445** occur in `game_attrs`; the remaining review records point to games not represented in the detailed-attribute table.
- `game_attrs` has 21,379 IDs present in `games`; 546 detailed-attribute IDs are absent from `games`.
- `games` is a much broader browse/listing table: 161,404 rows, 126,266 distinct non-null game IDs, and 35,138 null `game_id` rows. Its unique index permits multiple nulls but enforces uniqueness for non-null IDs.
- `game_attrs`, `game_links`, `game_ranks`, `game_tags`, `rating_dist`, and `weights` all use `game_id` as their conceptual join key, but the database does not enforce those joins.

## What the database can now support

The schema appears capable of supporting later work on rating-time patterns, user-level rating histories as represented by review records, overlap between ratings and collection/status signals, user/game participation profiles, and cross-game behavior among pseudonymous users. The combination of `reviews`, `users`, and `collections` is the main path for studying rater composition and selection.

## Important unknowns before analysis

- Whether `reviews` contains repeated ratings by the same user for the same game, and how to select or aggregate them.
- Whether `reviewid` is stable across the `reviews`/`collections` tables and whether it represents a review, a rating event, or an extraction row.
- The exact semantics and provenance of `rating_tstamp`, `comment_tstamp`, `postdate`, and `status_tstamp`.
- Whether `user_ratings` is an independent scrape, a different snapshot, or a transformed subset of `reviews`; its username identifiers are not joinable to the pseudonymous users.
- Whether collection flags are current snapshots or historical states, and whether they represent actual ownership/play or only declared BGG statuses.
- The exposure denominator: the database has no direct record of people who encountered a game and chose not to rate it, nor sales, plays, impressions, or audience-segment labels.
- Whether all user and review records share one coherent snapshot date; the latest observed record timestamps end in February 2025, while the existing game-level scrape is later.

The next phase should begin with key/cardinality, duplicate, timestamp-semantics, and snapshot-consistency audits before substantive audience or debiasing analysis.
