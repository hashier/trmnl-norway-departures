# Todo

Plans, bugs and features for the plugin.

## Bugs

- Lines go missing without a hint on a busy board: a local render of Jernbanetorget at
  08:00 on a weekday shows 11 of the 22 lines, with free space left in the third column
  (full layout, not compared with a real device).
- Times get cut off when a line has many departures. It shows on the full layout and is
  worse on the half layouts.
- A departure without a platform probably shows an empty `(Platf. )` on the board: the
  template always prints that text around `txt[1]` (from reading the markup, not rendered).
- A board without departures is blank apart from the title bar (rendered), and that bar is
  also the only place that shows "Unknown station ...". Show a message in the board itself.

## Plans

- Render the stops people really use, to see how the board looks for the average user and
  decide what to optimise. The request logs show which stops are polled (kept 30 days), so
  count them and preview the most used ones on each layout. This also gives real data for
  the cut-off times, the empty platform label and the board without departures above.
  Entur answers for future start times with planned data, so a weekday rush hour needs no
  waiting. `trmnlp build --png` in the `trmnl/trmnlp` Docker image renders all four layouts
  of a board in 5 to 7 s, with the data in `variables` of `.trmnlp.yml` and
  `framework_version: 2.3.7` in `settings.yml`.
- Move the board into Shared and keep only small CSS overrides in each layout. The four
  layouts are nearly the same copy.
- Upgrade the framework from 2.3.7 to 3.x. The upgrade guide says v3 is backward
  compatible, but dithering changed and `.trmnl .column` is custom CSS on framework
  classes. Test on a private copy first, because saves on the recipe reach all installs.

## Cleanup

- The README still links to `usetrmnl.com`, which redirects to `trmnl.com`.
- Check the Cloud Function runtime version.
