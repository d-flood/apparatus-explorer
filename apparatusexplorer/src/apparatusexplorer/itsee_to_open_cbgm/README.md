# itsee-to-open-cbgm
Utility script for reformatting the TEI XML output of the ITSEE Collation Editor for use in the open-cbgm library

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://choosealicense.com/licenses/mit/)

## About This Project

The Institute for Textual Scholarship and Electronic Editing (ITSEE) has developed and maintains a collation editor that accepts manuscript transcriptions in JSON format (converted from TEI XML format), resegments and classifies them according to user specifications, and outputs a finalized collation in TEI XML format. The editor is freely available as a standalone utility (https://github.com/itsee-birmingham/standalone_collation_editor) or as a component to be embedded in a platform with access to a database (https://github.com/itsee-birmingham/collation_editor_core). Given this editor's status as an established and commonly-used tool for biblical manuscript collation, I have made the open-cbgm library (https://github.com/jjmccollum/open-cbgm) flexible enough to parse ITSEE Collation Editor outputs with minimal changes in formatting. As a result, the only change that needs to be made to the output of the ITSEE Collation Editor for it to work with the open-cbgm library is the addition of local stemmata under its `<app>` (textual apparatus entry) elements.

Even so, the output of the ITSEE Collation Editor contains a number of idiosyncrasies that makes it less readable or less convenient to reference in the open-cbgm library's modules:
- It lacks a distinct list of all textual witnesses cited in variation units. This list would occur in the output's TEI header, but the output lacks a TEI header, as well.
- Since the editor was designed to collate small chunks of text (specifically, verses) at a time, its output includes an initial variation unit dedicated to isolating all witnesses that are lacunose for the entire portion of text collated. While this variation unit gives users a handy reference of witnesses that will not be cited in any other variation units, it is superfluous from the perspective of the open-cbgm library, which treats a witness as lacunose in every variation unit where it supports no reading. Moreover, because this variation unit lacks a `<rdg>` element showing which witnesses are extant for the collated text, it would be parsed by the open-cbgm library as a unit in which every witness is lacunose.
- For similar reasons, the output of the editor assigns the same index (presumably, the verse index) to each `<app>` element's `n` attribute, while relegating specific varation unit indices to its `from` and `to` attributes. This adheres to the TEI guidelines for the `<app>` element (https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-app.html), and so as not to discourage compliance with this standard, I have modified the open-cbgm library to parse elements labeled according to this convention. Nevertheless, referencing variation units in the open-cbgm modules would be facilitated if the `n`, `from`, and `to` attributes were merged into a single `n` attribute.
- For omission readings, the "om" placeholder is supplied as the text of the `<rdg>` element. Such a placeholder should probably be introduced at a higher processing stage rather than in the XML encoding, so `<rdg>` elements representing omissions should contain no text.
- Similarly, the addition of explicit `<wit>` elements under `<rdg>` elements is superfluous, since the `wit` attribute of the `<rdg>` element already contains the same information. The placement of the witness list after the content of the reading should probably be handled at a higher processing stage rather than in the XML encoding.
- Segments of text where all witnesses agree are treated as `<app>` elements with one `<rdg>` element, when they should be treated as text parallel to other `<app>` elements.
- The Unicode Combining Dot Below (U+0323), used for marking uncertain letters, is escaped as `&amp;#803;` by the editor, but since the output uses UTF-8 encoding, this character does not need to be escaped. (In practice, the combining dot is misplaced in most text editors, but the result is still more human-readable than text with the character escaped.)

The script contained in this repository addresses the minor issues detailed above, and it adds a `<note>` element containing a human-readable label, an `<fs>` (feature set) element containing the default connectivity setting, and a `<graph>` element that contains a node for every variant reading, but no edges. (The addition of edges to orient the stemma, of course, must be done by the user.) It was originally developed for David Flood to facilitate the use of the open-cbgm library in a project of his, but I have made it public to offer the same convenience to others. Feature requests are welcome to be submitted in the form of issues.

## Installation and Dependencies

This script was developed and tested in Python 3 and should be run in Python 3 for best results. Its only dependencies are the Python argparse and lxml modules.

## Usage

A TEI XML collation of John 6:23 as output by the ITSEE Collation Editor has been included in the xml directory for convenience. To convert this file to a form more amenable for use with the open-cbgm library, run the following command from the py directory:

    python itsee_to_open_cbgm.py ../xml/john_6_23_collation.xml

(Depending on your Python installation, you may need to use the `python3` command in place of `python`.) This will generate a reformatted john_6_23_collation_open_cbgm.xml file in the xml directory. If you want to give the generated file a different name, just use the `-o` flag followed by the name you want, as follows:

    python itsee_to_open_cbgm.py -o reformatted_john_6_23_collation.xml ../xml/john_6_23_collation.xml