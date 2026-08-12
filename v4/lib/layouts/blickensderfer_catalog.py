# Blickensderfer catalog entries:
#   (number, description, catalog page, preset, note)
#
# Transcribed from 14 page scans of a Blickensderfer type-wheel catalog
# (~/Blickensderfer-Catalog; see blickensderfer_layout.py for provenance).
#
# Unlike Hammond, this catalog has NO printed numerical index, and its
# descriptions do not encode the layout: "Small Roman, British Scientific"
# is a plain DHIATENSOR wheel on one page and a fraction wheel on another.
# So the preset per entry is recorded here as OBSERVED DATA rather than
# classified from the description the way gen_catalog_index.py does for
# Hammond. What is still computed, never hand-maintained, is the STATUS:
# an entry counts as imported exactly when its preset name is present in
# LAYOUT_PRESETS, and gen_catalog_index.py fails loudly on a name that
# isn't - so renaming or dropping a preset can't silently leave a stale
# "imported" row behind.
#
# preset "" means not imported; note then says why.
BLICKENSDERFER_CATALOG = [
    # --- catalog page 3 ---
    ('218',  'Armenian',                                    '3',  '',  'full Armenian script; needs its own transcription pass'),
    ('426',  'Small Roman, Bohemian',                       '3',  '',  'doubled dead-key accents (´´ / ˇˇ) not separable at this resolution'),
    ('443',  'Small Roman, Bohemian No. 2',                 '3',  '',  'same case as 426'),
    ('452½', 'Bulgarian',                                   '3',  '',  'Cyrillic; solvable by alphabet accounting, not yet done'),
    ('435',  'Elite, British Scientific',                   '3',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('405',  'Small Roman, British Scientific',             '3',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    # --- catalog page 4 ---
    ('412',  'Large Roman, British Scientific',             '4',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('428',  'Extra Large Roman, British Scientific',       '4',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('363',  'Small Roman, British Scientific',             '4',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('393',  'Large Roman, British Scientific',             '4',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('357',  'Roman, British Scientific',                   '4',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('407½', 'Small Roman, British Scientific',             '4',  'DHIATENSOR_BRITISH', ''),
    # --- catalog page 5 ---
    ('212',  'Imperial, British',                           '5',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('E458', 'Narrow Roman, British Scientific',            '5',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('331',  'Mimeograph, British Scientific',              '5',  'BRITISH_SCIENTIFIC_FRACTION_MIMEO', ''),
    ('454',  'Italic, British Scientific',                  '5',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('300',  'Script, British Scientific',                  '5',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    ('205',  'Vertical Script, British Scientific',         '5',  'BRITISH_SCIENTIFIC_FRACTION', ''),
    # --- catalog page 6 ---
    ('381',  'Elite Literary, British',                     '6',  'BRITISH_LITERARY', ''),
    ('462',  'Small Roman Literary, British',               '6',  'BRITISH_LITERARY', ''),
    ('307',  'Extra Large Roman Literary, British',         '6',  'BRITISH_LITERARY', ''),
    ('383',  'Italic Literary, British',                    '6',  'BRITISH_LITERARY', ''),
    ('395',  'Script Literary, British',                    '6',  'BRITISH_LITERARY', ''),
    ('213',  'Vertical Script Literary, British',           '6',  'BRITISH_LITERARY', ''),
    # --- catalog page 7 ---
    ('376',  'British Telegraph',                           '7',  '',  'non-standard row shape, not the usual three-row 28-column form'),
    ('350',  'Elite, British Universal',                    '7',  'UNIVERSAL_FRACTION', ''),
    ('441',  'Small Roman, British Universal',              '7',  'QWERTY_BRITISH', ''),
    ('442',  'Large Roman, British Universal',              '7',  'QWERTY_BRITISH', ''),
    ('494',  'Small Roman, British Universal',              '7',  'UNIVERSAL_FRACTION', ''),
    ('379',  'Large Roman, British Universal',              '7',  'UNIVERSAL_FRACTION', ''),
    # --- catalog page 8 ---
    ('387',  'Special British, Universal',                  '8',  '',  'last five slots are shilling numerators (1⁄ 3⁄ 5⁄ 7⁄ 9⁄) cast as single type; only ⅟ has a codepoint'),
    ('371',  'Italic, British Universal',                   '8',  'UNIVERSAL_FRACTION', ''),
    ('337',  'Script, British Universal',                   '8',  'UNIVERSAL_FRACTION', ''),
    ('217',  'Vertical Script, British Universal',          '8',  'UNIVERSAL_FRACTION', ''),
    ('203',  'Small Roman Literary, British Universal',     '8',  'UNIVERSAL_LITERARY', ''),
    ('433',  'Small Roman, British-American Scientific',    '8',  'BRITISH_AMERICAN', ''),
    # --- catalog page 9 ---
    ('432',  'Large Roman, British-American Scientific',    '9',  'BRITISH_AMERICAN', ''),
    ('458',  'Narrow Roman, British-India Scientific',      '9',  'BRITISH_INDIA', ''),
    ('385',  'Chemical, English Scientific',                '9',  'CHEMICAL_ENGLISH', ''),
    ('222',  'Chemical, Universal (British)',               '9',  'CHEMICAL_UNIVERSAL', ''),
    ('328',  'Cosmopolitan Scientific',                     '9',  'COSMOPOLITAN', ''),
    ('367',  'Small Roman, Universal',                      '9',  'UNIVERSAL_ACCENT', ''),
    # --- catalog page 10 ---
    ('420',  'Small Roman, Danish',                         '10', 'DANISH', ''),
    ('365',  'Elite, English Scientific',                   '10', 'DHIATENSOR', ''),
    ('407',  'Small Roman, English Scientific',             '10', 'DHIATENSOR', ''),
    ('409',  'Large Roman, English Scientific',             '10', 'DHIATENSOR', ''),
    ('455',  'Narrow Roman, English Scientific',            '10', 'DHIATENSOR', ''),
    ('457',  'Large Narrow Roman, English Scientific',      '10', 'DHIATENSOR', ''),
    # --- catalog page 11 ---
    ('356',  'Roman, English Scientific',                   '11', 'DHIATENSOR', ''),
    ('362',  'Small Roman, English Scientific',             '11', 'DHIATENSOR', ''),
    ('374',  'Large Roman, English Scientific',             '11', 'DHIATENSOR', ''),
    ('474',  'Mimeograph, English Scientific',              '11', 'DHIATENSOR', ''),
    ('440',  'Italic, English Scientific',                  '11', 'DHIATENSOR', ''),
    ('499',  'Script, English Scientific',                  '11', 'DHIATENSOR', ''),
    # --- catalog page 12 ---
    ('201',  'Vertical Script, English Scientific',         '12', 'DHIATENSOR', ''),
    ('223',  'Print Type, English Scientific',              '12', 'DHIATENSOR', ''),
    ('308',  'Gothic, English Scientific',                  '12', 'DHIATENSOR', ''),
    ('325',  'Elite, Universal',                            '12', 'QWERTY', ''),
    ('406',  'Small Roman, Universal',                      '12', 'QWERTY', ''),
    ('418',  'Large Roman, Universal',                      '12', 'QWERTY', ''),
    # --- catalog page 13 ---
    ('364',  'Small Roman, Universal',                      '13', 'QWERTY', ''),
    ('359',  'Mimeograph, Universal',                       '13', 'QWERTY', ''),
    ('497',  'Italic, Universal',                           '13', 'QWERTY', ''),
    ('304',  'Script, Universal',                           '13', 'QWERTY', ''),
    ('216',  'Vertical Script, Universal',                  '13', 'QWERTY', ''),
    ('436',  'Elite, English Fractional Scientific',        '13', 'DHIATENSOR_FRACTION', ''),
    # --- catalog page 14 ---
    ('424',  'Small Roman, English Fractional',             '14', 'DHIATENSOR_FRACTION', ''),
    ('425',  'Large Roman, English Fractional',             '14', 'DHIATENSOR_FRACTION', ''),
    ('447',  'Small Roman, English Fractional',             '14', 'DHIATENSOR_FRACTION_ALT', ''),
    ('494½', 'Small Roman, Universal Fractional',           '14', 'UNIVERSAL_FRACTION_US', ''),
    ('332',  'Small Roman, English-Japanese Scientific',    '14', 'ENGLISH_JAPANESE', ''),
    ('333',  'Large Roman, English-Japanese Scientific',    '14', 'ENGLISH_JAPANESE', ''),
    # --- catalog page 18 ---
    ('404',  'Small Roman, German',                         '18', 'GERMAN', ''),
    ('423',  'Large Roman, German',                         '18', 'GERMAN', ''),
    ('303',  'Extra Large Roman, German',                   '18', 'GERMAN_ESZETT', ''),
    ('378',  'Large Roman, German',                         '18', 'GERMAN', ''),
    ('204',  'Large Roman, German',                         '18', 'GERMAN_FRACTION', ''),
    ('489',  'Italic, German',                              '18', 'GERMAN', ''),
    # --- catalog page 21 ---
    ('309',  'Ancient Greek',                               '21', '',  'Greek script; needs its own transcription pass'),
    ('354',  'Hebrew',                                      '21', '',  'Hebrew script; needs its own transcription pass'),
    ('358',  'Hebrew',                                      '21', '',  'catalog states in prose: 354 with £ for $ - do 354 first'),
    ('348',  'Hebrew-English (Hebrew-British)',             '21', '',  'Hebrew script; needs its own transcription pass'),
    ('351',  'Hebrew-English No. 2',                        '21', '',  'Hebrew script; needs its own transcription pass'),
    ('415',  'Small Roman, Hungarian',                      '21', 'HUNGARIAN', ''),
]

# Catalog pages PRESENT in the scans: 3-14, 18, 21. Missing: 1, 2, 15-17,
# 19, 20, and anything past 21. Every page present holds exactly six
# entries, so the gaps are worth roughly 42 more shuttles. The missing
# 15-17 fall between ENGLISH-JAPANESE and GERMAN alphabetically, and
# 19-20 between GERMAN and GREEK - so French, Esperanto and the rest of
# the German section are known-absent rather than unaccounted for.
PAGES_PRESENT = ('3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                 '13', '14', '18', '21')
PAGES_MISSING = ('1', '2', '15', '16', '17', '19', '20')
