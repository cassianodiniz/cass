# Prototype

**When.** A change that only edits an existing element in place - its text, color or variant -, hides or shows it, or fixes a visual defect, needs no prototype. Every other change to a screen gets one. When in doubt, make it.

**What it is.** One static page per screen, `.specs/features/<f>/prototype/<screen>.html`, that shows the finished screen. It has no app code and no logic.
- Styles: the project's own CSS build, run with the prototype as one more source, writes the stylesheet beside it, so every class the prototype uses exists. The page also loads the fonts the app's entry file loads.
- Pieces: each element copies the class list of the piece the screen's `**Pieces:**` line names, from that piece's file, with the variant the design manual gives for that place. Draw a new piece with the project's classes and mark it `<!-- new piece -->`. Draw a piece the change fixes as it will be after the fix and mark it `<!-- changed piece -->`.
- Frames: one frame per `## Screen states` row that lands on a criterion, headed `<screen> row <n>`, with the account and the data the row names. Data the project's seed files do not hold is added to the seed, with the values the frame shows, by a task that comes after any change to the stored model. Draw a state with motion, such as an open menu, at its open moment.
- Text: labels and sentences come from the references or the criteria, character for character.

**Photos.** Show each frame alone in a browser window of 375×812, 768×1024 and 1280×800 px, and of each other width its row names, and photograph the window to `captures/<screen>-row<n>-<width>.png`. These photos are the binding source: the row's criterion cites each one, and each is shown on a `Sources` line, `![<screen> row <n>, <width>](captures/<file>) - binding - prototype`.

**Departures from a reference.** A place where the prototype departs from what the user sent - a removed control, another label, another arrangement - is a gray area: ask it before you present the plan ([investigate.md](investigate.md)).

**When it cannot be made.** When the CSS build or a browser cannot run, ask the user as a `blocks` question. Never present a plan whose screen needs a prototype without its photos.

**The screen's line.** Under the screen's `**Pieces:**` line, write `**Prototype:** prototype/<screen>.html`, or `**Prototype:** none - <element> edited in place`, `hidden`, `shown` or `defect fixed`.
