# Todo

Plans, bugs and features for the plugin.

## Bugs

- Times get cut off when a line has many departures. It shows on the full layout and is
  worse on the half layouts.
- A wrong station ID makes the function return a plain 503, so the user sees no helpful
  message.
- Check what a stop without departures shows. The template has no text for that case, so
  it is probably an empty board (not tested).

## Plans

- Move the board into Shared and keep only small CSS overrides in each layout. The four
  layouts are nearly the same copy, and only the full layout is in this repo.
- Upgrade the framework from 2.3.7 to 3.x. The upgrade guide says v3 is backward
  compatible, but dithering changed and `.trmnl .column` is custom CSS on framework
  classes. Test on a private copy first, because saves on the recipe reach all installs.

## Cleanup

- `polling_body` still holds an old copy of the form fields. It is not used with GET.
- The README and a comment in the markup still link to `usetrmnl.com`, which redirects to
  `trmnl.com`.
- Check the Cloud Function runtime version.
