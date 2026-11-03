# Todo

Plans, bugs and features for the plugin.

## Bugs

- A departure without a platform shows an empty `(Platf. )` on the board (rendered).
- A board without departures is blank apart from the title bar (rendered), and that bar is
  also the only place that shows "Unknown station ...". Show a message in the board itself.
- The title bar is cut off on half vertical and quadrant: "Last updated" and most of the
  title are gone (rendered).
- Text in the middle column can render bold when there are three columns (seen in the
  Firefox `trmnlp` uses, not checked on TRMNL's own renderer). Rounding the column width
  did not help.

## Plans

- Render the stops people really use, to see how the board looks for the average user and
  decide what to optimise. The request logs show which stops are polled (kept 30 days), so
  count them and preview the most used ones on each layout. This also gives real data for
  the cut-off times, the empty platform label and the board without departures above.
  Entur answers for future start times with planned data, so a weekday rush hour needs no
  waiting. `trmnlp build --png` in the `trmnl/trmnlp` Docker image renders all four layouts
  of a board in 5 to 7 s, with the data in `variables` of `.trmnlp.yml` and
  `framework_version: 2.3.7` in `settings.yml`. `trmnlp` also polls the live URL and merges
  the answer with `variables`, so blank `polling_url` in the test copy.
- Upgrade the framework from 2.3.7 to 3.x. The upgrade guide says v3 is backward
  compatible, but dithering changed and `.trmnl .column` is custom CSS on framework
  classes. Test on a private copy first, because saves on the recipe reach all installs.

## Cleanup

- The README still links to `usetrmnl.com`, which redirects to `trmnl.com`.
- Check the Cloud Function runtime version.
