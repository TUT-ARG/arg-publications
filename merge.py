#!/usr/bin/env python

import os, csv, math, sys
import re
import pybtex
from pybtex.database.input import bibtex
from unidecode import unidecode
from pylatexenc.latexwalker import LatexWalker
from pylatexenc.latex2text import LatexNodes2Text
from IPython import embed
import string


def main(argv):
    print('Merge BibTex bibliographies')
    print('===========================================')
    collections_path = os.path.join('collections')
    target_collection = 'publications.bib'

    bibtex_files = []
    for file in os.listdir(collections_path):
        if file.endswith(".bib"):
            bibtex_files.append(os.path.join(collections_path, file))

    pub_source_map = {
        'Audio Engineering Society': 'AES',
        'AES': 'AES',
        'Workshop on Machine Listening in Multisource Environments': 'CHiME',
        'CHiME workshop': 'CHiME',
        'Finnish Signal Processing Symposium': 'FINSIG',
        'IEEE Workshop on Applications of Signal Processing to Audio and Acoustics': 'WASPAA',
        'Applications of Signal Processing to Audio and Acoustics': 'WASPAA',
        'European Signal Processing Conference': 'EUSIPCO',
        'EUSIPCO': 'EUSIPCO',
        'INTERSPEECH': 'InterSpecch',
        'International Speech Communication Association': 'InterSpecch',
        'International Joint Conference on Neural Networks': 'IJCNN',
        'International Workshop on Acoustic Signal Enhancement': 'IWAENC',
        'International Workshop on Acoustic Echo and Noise Control': 'IWAENC',
        'IEEE International Symposium on Circuits and Systems': 'ISCAS',
        'IEEE International Conference on Acoustics, Speech, and Signal Processing': 'ICASSP',
        'IEEE International Conference on Acoustics Speech and Signal Processing': 'ICASSP',
        'IEEE International Conference on Acoustics, Speech and Signal Processing': 'ICASSP',
        'International Conference on Acoustics, Speech, and Signal Processing': 'ICASSP',
        'IEEE Int. Conf. Acoustics, Speech, Signal Processing': 'ICASSP',
        'ICASSP': 'ICASSP',
        'IEEE International Workshop on Machine Learning for Signal Processing': 'MLSP',
        'Machine Learning for Multimodal Interaction': 'MLMI',
        'Proceedings of International Workshop on Nonlinear Signal and Image Processing': 'NSIP',
        'IEEE International Symposium on Intelligent Signal Processing and Communication Systems': 'ISPACS',
        'IEEE International Conference on Signal and Image Processing Applications': 'ICSIPA',
        'International Conference on Music Information Retrieval': 'ISMIR',
        'International conference Speech and Computer': 'SPECOM',
        'TISE': 'TISE',
        'International Conference on Digital Audio Effects': 'DAFx',
        'DAFx': 'DAFx',
        'International Multiconference on Circuits, Systems, Communications and Computers': 'CSCC',
        'IEEE Sensor Array and Multichannel Signal Processing Workshop': 'SAM',
        'IEEE Workshop on Sensor Array and Multichannel Processing': 'SAM',
        'IEEE Nordic Signal Processing Symposium': 'NORSIG',
        'Norsig': 'NORSIG',
        'IEEE International Symposium on consumer Electronics': 'ISCE',
        'International Conference on Digital Signal Processing': 'DSP',
        'ISCA': 'ISCA',
        'International Symposium on Signal, Circuits and Systems': 'ISSCS',
        'SPIE': 'SPIE',
        'Music Information Retrieval Evaluation eXchange': 'MIREX',
        'IEEE International Conference on Multimedia and Expo': 'ICME',
        'IEEE International Conf. on Multimedia and Expo': 'ICME',
        'Computers in Music Modeling and Retrieval Conference': 'CMMR',
        'International Conference on Latent Variable Analysis and Signal Separation': 'LVA_ICA',
        'International Conference on Latent Variable Analysis and Source Separation': 'LVA_ICA',
        'Sound and Music Computing Conference': 'SMC',
        'IMTC': 'IMTC',
        'International Conference on Speech Prosody': 'SP',
        'Detection and Classification of Acoustic Scenes and Events': 'DCASE',
        'CRAC': 'CRAC',
        'International Symposium on Control, Communications and Signal Processing': 'ISCCSP',
        'International Symposium on Communications, Control and Signal Processing':'ISCCSP',
        'ICA': 'ICA',
        'International Symposium on Communications and Information Technologies': 'ISCIT',
        'International Symposium on Intelligent Signal Processing and Communication Systems': 'ISPACS',
        'ICSPAT': 'ICSPAT',
        'Lecture Notes in Computer Science': 'LNCS',
        'International Symposium on Signal Processing and its Applications': 'ISSPA',
        'Workshop on Statistical Signal and Array Processing': 'SSAP',
        'The Speaker and Language Recognition Workshop': 'Odyssey',
        'International Computer Music Conference': 'ICMC',
        'Signal Processing Methods for Music Transcription': 'SPMMT',
        'International Symposium on Image and Signal Processing and Analysis': 'ISPA',
        'European Conference on Technology Enhanced Learning': 'EX-TEL',
        'IEEE/ACM Transactions on Audio, Speech, and Language Processing': 'TASLP',
        'IEEE-ACM Transactions on Audio Speech and Language Processing': 'TASLP',
        'IEEE Transactions on Audio, Speech, and Language Processing': 'TASLP',
        'Transactions on Audio, Speech and Language Processing': 'TASLP',
        'IEEE Trans. Audio, Speech, and Language Processing': 'TASLP',
        'IEEE Trans. Speech and Audio Processing': 'TASP',
        'IEEE Signal Processing Magazine': 'SPM',
        'IEEE Journal of Selected Topics in Signal Processing': 'JSTSP',
        'Journal of Signal and Information Processing': 'JSIP',
        'IEEE Transactions on Affective Computing': 'TAC',
        'Digital Signal Processing': 'DSP',
        'Applied Acoustics': 'AA',
        'Journal of New Music Research': 'JNMR',
        'Signal Processing': 'SP',
        'Eurasip Journal on Audio, Speech, and Music Processing': 'JASM',
        'EURASIP Journal on Audio, Speech and Music Processing': 'JASM',
        'IEEE Sensors Journal': 'SJ',
        'Eurasip Journal on Image and Video Processing': 'JIV',
        "Computer Speech & Language": 'CSL',
        'Applied Sciences': 'AS',
        'Computer Music Journal': 'CMJ',
        'Personal and Ubiquitous Computing': 'PUC',
        'Neural Networks': 'NN',
        'PLoS ONE': 'PLOSONE'
    }

    unique_entries = []
    public_entry_keys = []
    all_bib_data = pybtex.database.BibliographyData()
    for collection_filename in bibtex_files:
        print('  Processing [{filename}]'.format(filename=collection_filename))
        parser = pybtex.database.input.bibtex.Parser()
        bib_data = parser.parse_file(collection_filename)
        entries = sorted(list(bib_data.entries.keys()))

        # Go through entries
        for entry_key in entries:
            # Get lastname of first author
            author = str(bib_data.entries[entry_key].persons['author'][0].last_names[0])
            if '\\' in author:
                author = LatexNodes2Text().nodelist_to_text(LatexWalker(author).get_latex_nodes()[0])

            # Get title
            title = bib_data.entries[entry_key].fields.get('title')
            if '\\' in title:
                title = LatexNodes2Text().nodelist_to_text(LatexWalker(title).get_latex_nodes()[0])

            # Get year
            year = int(bib_data.entries[entry_key].fields.get('year'))

            # Generate key for the entry
            key = '{year}_{author}_{title}'.format(
                author=unidecode(author),
                year=year,
                title=title.lower().replace(' ','').replace(',','').replace('{','').replace('}','').replace(':','').replace('-','').replace('(','').replace(')','')
            )

            # Get journal or conference name to be added into public bibtex key
            pub = ''
            if bib_data.entries[entry_key].type == 'inproceedings':
                booktitle = bib_data.entries[entry_key].fields.get('booktitle')
                conf_name = re.search(r'\((.*?)\)', booktitle)
                if conf_name:
                    pub = '_' + conf_name.group(1)
                else:
                    for search_item in pub_source_map:
                        if search_item.lower() in booktitle.lower():
                            pub = '_' + pub_source_map[search_item]
                            break

            elif bib_data.entries[entry_key].type == 'article':
                journal = bib_data.entries[entry_key].fields.get('journal')
                journal_name = re.search(r'\((.*?)\)', journal)
                if journal_name:
                    pub = '_' + journal_name.group(1)
                else:
                    for search_item in pub_source_map:
                        if search_item.lower() in journal.lower():
                            pub = '_' + pub_source_map[search_item]
                            break

            elif bib_data.entries[entry_key].type == 'mastersthesis':
                pub = '_master'
            elif bib_data.entries[entry_key].type == 'phdthesis':
                pub = '_phd'

            # Generate public entry key, and store it
            public_entry_key = '{author}{year}{pub}'.format(author=author, year=year, pub=pub)
            if public_entry_key not in public_entry_keys:
                public_entry_keys.append(public_entry_key)

            else:
                # Default one is not unique
                for letter in string.ascii_lowercase:
                    if public_entry_key+'_'+letter not in public_entry_keys:
                        public_entry_key = public_entry_key+'_'+letter
                        public_entry_keys.append(public_entry_key)
                        break

            # Store entry
            if key not in unique_entries:
                # Store entry
                all_bib_data.add_entry(
                    key=public_entry_key,
                    entry=bib_data.entries[entry_key]
                )

                # Store key
                unique_entries.append(key)

            else:
                print('    Dup [{author} {year}, {title}]'.format(author=author, year=year, title=title))

    # Save bibtex
    all_bib_data.to_file(file=target_collection)


if __name__ == "__main__":
    sys.exit(main(sys.argv))