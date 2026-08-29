# Port notes

## Differences from the Sketch original

- The copies are grouped, but the original object is left visible by default;
  tick *Hide the original object* on the Count tab for the original behavior.
- Random rotation uses the documented behavior (angle ± randomize range).
  The original had a JavaScript quirk (`Math.random(a, b)` ignores its
  arguments) that made it rotate by a uniform 0-100° regardless of settings.
- Random move scatters relative to the original object's position, not the
  artboard origin (Inkscape has no artboards).
- A random *seed* option was added so results can be reproduced and the
  dialog's live preview stays stable.
- Grid margins are the spacing between successive copies' origins, matching
  the original implementation.
- The Google Analytics tracking of the original was not ported.

## Live preview

Enable **Live preview** in the extension dialog to see the pattern update as
you change parameters. With random modes, set a non-zero seed (Count tab) so
the preview doesn't change on every refresh.

## Development / tests

`test/run_tests.py` runs the extension headlessly against `test/test.svg`
and verifies copy counts, transforms, grid layout, opacity fades, seeded
reproducibility and error handling:

```
pip install inkex
python test/run_tests.py
```

Tested on Inkscape 1.2.2 and 1.4.4 (bundled Python/inkex) and standalone
inkex 1.4.1.
