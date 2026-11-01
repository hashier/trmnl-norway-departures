# Todo

Plans, bugs and features for the plugin.

## Bugs

- Times get cut off when a line has many departures. It shows on the full layout and is
  worse on the half layouts.
- A wrong station ID makes the function return a plain 503, so the user sees no helpful
  message. Entur answers `stopPlace: null`, the code then fails on `None` and exits. IDs are
  case sensitive: `nsr:StopPlace:59605` failed like this 15 times on 2026-10-22 until the
  user changed it to `NSR:StopPlace:59605`. Normalizing the case, or returning a 400, would
  also keep user errors out of the 5xx alert.
- `requests.post` to Entur has no timeout, so a hanging Entur blocks the request until Cloud
  Run gives up (from reading the code, not seen).
- A departure without a platform probably shows an empty `(Platf. )` on the board: the
  template always prints that text around `txt[1]` (from reading the markup, not rendered).
- Check what a stop without departures shows. The template has no text for that case, so
  it is probably an empty board (not tested).

## Plans

- Move the board into Shared and keep only small CSS overrides in each layout. The four
  layouts are nearly the same copy, and only the full layout is in this repo.
- Upgrade the framework from 2.3.7 to 3.x. The upgrade guide says v3 is backward
  compatible, but dithering changed and `.trmnl .column` is custom CSS on framework
  classes. Test on a private copy first, because saves on the recipe reach all installs.

## Cleanup

- The README and a comment in the markup still link to `usetrmnl.com`, which redirects to
  `trmnl.com`.
- Check the Cloud Function runtime version.
