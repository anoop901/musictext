# MusicText
MusicText is a way to represent music in a simple plaintext
format.

## How to run
You need to have a mongodb database running at port 27017.
You can do this by installing mongod locally
and running the following (I recommend doing this in a new terminal
window) like so:
```
mkdir data
mongod --dbpath data
```

Then, run the following commands to run the application
```
FLASK_APP=app.py
flask run
```

## Syntax
### Notes
A note is represented as a letter, followed by an optional
accidental, followed by an optional octave modifier.

The letter is either a capital or lowercase letter from A
to G. The case of the letter determines the octave in which
this note is located (unless there is an octave modifier). An
octave is defined as the range of notes starting at a C and
ending at the B above it. If it is a capital letter, the note
is in the octave containing middle C. If it is a lowercase
letter, the note is in the octave below.

An accidental can specify whether the note is sharp or flat.
`#` specifies sharp, and `@` specifies flat. A note can have
multiple accidentals, provided that they are all of the same
type.

To represent notes in higher octaves, append one `'`
(apostrophe) to a note for each octave you want to raise it.
Similarly, to represent notes in lower octaves, append one
`,` (comma) to a note for each octave you want to lower it.
You can only apply `'` to capital letter notes, and you can
only apply `,` to lowercase letter notes.

Here are some examples of notes:
* `C`: middle C
* `F#`: the F sharp above middle C
* `B@`: the B flat above middle C
* `g`: the G below middle C
* `E'`: the E which is an octave higher than `E`
* `E''`: the E which is 2 octaves higher than `E`
* `d,`: the D which is an octave lower than `d`
* `d,,`: the D which is 2 octaves lower than `d`

### Rhythms
Writing multiple notes sequentially represents that they are
to be played one after the other on every beat.
```
C E G C'
```
Whitespace between notes is optional.

Use a `.` to represent a rest, and a `-` to represent that
this beat sustains the same note as the previous one.
```
B - D' A - .
```

To show 2 notes in one beat, use square brackets `[]`. You
can put 2 notes in a pair of square brackets, and each will
take up half the time as they would otherwise.
```
[D F] D' - [D F] D'
```

Nest square brackets inside each other to further
half the note length.
```
[[B' E'] [C' A]] [[A' E'] [C' A]]
[[G#' E'] [C' A]] [[A' E'] [C' A]]
```

Here's an example using note continuation and square brackets
together to create syncopation:
```
B [- B] [- B] [B B] C' - - .
```

Similarly to square brackets, parentheses `()` can be used
to divide the note length by 3.
```
(b@, f b@)  (D b@ f)
(g, d g) (b g d)
(c g b@) (F b@ g)
(f, f c) (e@ c f)
```