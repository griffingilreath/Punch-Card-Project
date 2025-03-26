# IBM Punch Card Encoding Reference

This document provides a comprehensive reference for IBM punch card character encoding systems, based on historical documentation and research.

## IBM 80-Column Punch Card Format

### Physical Specifications

| Feature | Specification |
|---------|---------------|
| Dimensions | 7⅜ × 3¼ inches (187mm × 82.5mm) |
| Thickness | ~0.007 inches |
| Hole Shape | Rectangular (~1mm × 3mm) |
| Column Count | 80 (numbered 1-80 left to right) |
| Row Count | 12 (12, 11, 0-9 from top to bottom) |
| Corner Cut | Upper-left corner (for orientation) |
| Horizontal Pitch | ~0.087 inches (~2.21 mm) |
| Vertical Pitch | ~0.25 inches between rows |

### Card Layout Visualization

```
     1         2         3         4         5         6         7         8
     012345678901234567890123456789012345678901234567890123456789012345678901234567890
    ┌────────────────────────────────────────────────────────────────────────────────┐
 12 |                                                                                 |
 11 |                                                                                 |
  0 |                                                                                 |
  1 |                                                                                 |
  2 |                                                                                 |
  3 |                                                                                 |
  4 |                                                                                 |
  5 |                                                                                 |
  6 |                                                                                 |
  7 |                                                                                 |
  8 |                                                                                 |
  9 |                                                                                 |
    └────────────────────────────────────────────────────────────────────────────────┘
```

## Character Encoding Systems

IBM punch cards used specific hole patterns (or "punches") to represent characters. Different character sets were used depending on the application, but the physical encoding remained consistent.

### Encoding Notation

Punch patterns are typically written using row numbers separated by hyphens. For example:
- `12-1` means holes in rows 12 and 1
- `0-2-8` means holes in rows 0, 2, and 8

### Zone and Digit Punches

- **Zone punches**: Rows 12, 11, and 0
- **Numeric punches**: Rows 1 through 9

## IBM 026 Keypunch (FORTRAN) Character Set

Used primarily for scientific applications and FORTRAN programming.

| Character | Punch Pattern | Description |
|-----------|---------------|-------------|
| A | 12-1 | Letter A |
| B | 12-2 | Letter B |
| C | 12-3 | Letter C |
| D | 12-4 | Letter D |
| E | 12-5 | Letter E |
| F | 12-6 | Letter F |
| G | 12-7 | Letter G |
| H | 12-8 | Letter H |
| I | 12-9 | Letter I |
| J | 11-1 | Letter J |
| K | 11-2 | Letter K |
| L | 11-3 | Letter L |
| M | 11-4 | Letter M |
| N | 11-5 | Letter N |
| O | 11-6 | Letter O |
| P | 11-7 | Letter P |
| Q | 11-8 | Letter Q |
| R | 11-9 | Letter R |
| S | 0-2 | Letter S |
| T | 0-3 | Letter T |
| U | 0-4 | Letter U |
| V | 0-5 | Letter V |
| W | 0-6 | Letter W |
| X | 0-7 | Letter X |
| Y | 0-8 | Letter Y |
| Z | 0-9 | Letter Z |
| 0 | 0 | Digit 0 |
| 1 | 1 | Digit 1 |
| 2 | 2 | Digit 2 |
| 3 | 3 | Digit 3 |
| 4 | 4 | Digit 4 |
| 5 | 5 | Digit 5 |
| 6 | 6 | Digit 6 |
| 7 | 7 | Digit 7 |
| 8 | 8 | Digit 8 |
| 9 | 9 | Digit 9 |
| + | 12 | Plus sign |
| - | 11 | Minus sign |
| * | 11-8-4 | Asterisk |
| / | 0-1 | Slash |
| = | 0-8-3 | Equal sign |
| . | 12-8-3 | Period |
| , | 0-8-3 | Comma |
| $ | 11-8-3 | Dollar sign |
| ( | 12-8-5 | Open parenthesis |
| ) | 11-8-5 | Close parenthesis |
| blank | No punch | Space character |

## IBM 029 Keypunch (Commercial/Symbolic) Character Set

Expanded character set for business applications, assembly language, and other uses.

| Character | Punch Pattern | Description |
|-----------|---------------|-------------|
| # | 8-3 | Number sign |
| @ | 8-4 | At sign |
| % | 0-8-4 | Percent sign |
| & | 12 | Ampersand |
| ! | 11-8-7 | Exclamation mark |
| ? | 0-8-7 | Question mark |
| " | 8-7 | Quotation mark |
| ' | 8-5 | Apostrophe |
| : | 8-2 | Colon |
| ; | 11-8-6 | Semicolon |
| < | 12-8-6 | Less than |
| > | 0-8-6 | Greater than |
| [ | 12-8-2 | Open bracket |
| ] | 11-8-2 | Close bracket |
| { | 12-0 | Open brace |
| } | 11-0 | Close brace |

*Note: The Commercial/Symbolic set includes all the characters from the FORTRAN set, with some different assignments.*

## EBCDIC (Extended Binary Coded Decimal Interchange Code)

Introduced with the IBM System/360 in 1964, EBCDIC is an 8-bit character encoding system that mapped punch card codes to computer memory.

### EBCDIC Encoding Pattern

EBCDIC used the following bit positions to represent punch card holes:

- Bit 0 = 12 punch
- Bit 1 = 11 punch
- Bit 2 = 0 punch
- Bit 3 = 1 punch
- Bit 4 = 2 punch
- Bit 5 = 3 punch
- Bit 6 = 4 punch
- Bit 7 = 5 punch
- Bit 8 = 6 punch
- Bit 9 = 7 punch
- Bit 10 = 8 punch
- Bit 11 = 9 punch

## ASCII Punch Card Extension (ANSI X3.26-1970)

In 1970, the American National Standards Institute published ANSI X3.26, which defined punch combinations for all 128 ASCII characters on a 12-row card.

### Lowercase Letter Encoding

| Character | Punch Pattern | Description |
|-----------|---------------|-------------|
| a | 12-0-1 | Lowercase a |
| b | 12-0-2 | Lowercase b |
| c | 12-0-3 | Lowercase c |
| d | 12-0-4 | Lowercase d |
| e | 12-0-5 | Lowercase e |
| f | 12-0-6 | Lowercase f |
| g | 12-0-7 | Lowercase g |
| h | 12-0-8 | Lowercase h |
| i | 12-0-9 | Lowercase i |
| j | 12-11-1 | Lowercase j |
| k | 12-11-2 | Lowercase k |
| l | 12-11-3 | Lowercase l |
| m | 12-11-4 | Lowercase m |
| n | 12-11-5 | Lowercase n |
| o | 12-11-6 | Lowercase o |
| p | 12-11-7 | Lowercase p |
| q | 12-11-8 | Lowercase q |
| r | 12-11-9 | Lowercase r |
| s | 11-0-2 | Lowercase s |
| t | 11-0-3 | Lowercase t |
| u | 11-0-4 | Lowercase u |
| v | 11-0-5 | Lowercase v |
| w | 11-0-6 | Lowercase w |
| x | 11-0-7 | Lowercase x |
| y | 11-0-8 | Lowercase y |
| z | 11-0-9 | Lowercase z |

## Punch Card Usage Conventions

### FORTRAN Coding Sheets

FORTRAN punch cards typically followed a specific column layout:

| Columns | Purpose |
|---------|---------|
| 1-5 | Statement number |
| 6 | Continuation indicator |
| 7-72 | FORTRAN statement |
| 73-80 | Sequence number |

### COBOL Coding Sheets

COBOL programs used a different column layout:

| Columns | Purpose |
|---------|---------|
| 1-6 | Sequence number |
| 7 | Indicator area |
| 8-11 | Area A (divisions, sections, paragraphs) |
| 12-72 | Area B (statements) |
| 73-80 | Identification |

## Historical Significance

The phrase "Do not fold, spindle, or mutilate" originated as a warning printed on punch cards but became a cultural meme in the 1960s, symbolizing resistance to dehumanization by bureaucracy and computer systems.

## References

- IBM Documentation: "IBM Punched Card Stock Specification"
- Columbia University Computing History Archive
- University of Iowa Punch Card Collection (D. Jones)
- ANSI X3.26-1970: Hollerith Punched Card Code
- "Two-Bit History: The Punched Card Tabulator"
- "The Craft of Coding: Understanding Historical Computing" 