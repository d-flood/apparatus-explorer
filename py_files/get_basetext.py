import re

intf_sbl_books = {
    ('B01', 'Matt'): ('Matt', 'Mt', 'B01'),
    ('B02', 'Mark'): ('Mark', 'Mk', 'B02'),
    ('B03', 'Luke'): ('Luke', 'Lk', 'L', 'B03'),
    ('B04', 'John'): ('John', 'Jn', 'B04'),
    ('B05', 'Acts'): ('Acts', 'Ac', 'A', 'B05'),
    ('B06', 'Rom'): ('Rom', 'Romans', 'R', 'Rm', 'B06'),
    ('B07', '1 Cor'): ('1 Cor', '1Cor', '1C', 'IC', 'I Cor', 'B07'),
    ('B08', '2 Cor'): ('2 Cor', '2Cor', '2C', 'IIC', 'II Cor', 'B08'),
    ('B09', 'Gal'): ('Galatians', 'Gal', 'B09'),
    ('B10', 'Eph'): ('Ephesians', 'Eph', 'B10'),
    ('B11', 'Phil'): ('Philippians', 'Phil', 'B11'),
    ('B12', 'Col'): ('Col', 'Colossians', 'B12'),
    ('B13', '1 Thess'): ('1 Thess', '1Th', 'ITh', 'I Thess', 'B13'),
    ('B14', '2 Thess'): ('2 Thess', '2Th', 'IITh', 'II Thess', 'B14'),
    ('B15', '1 Tim'): ('1 Tim', '1Tim', 'ITim', 'I Tim', 'B15'),
    ('B16', '2 Tim'): ('2 Tim', '2Tim', 'IITim', 'II Tim', 'B16'),
    ('B17', 'Titus'): ('Titus', 'Tit', 'B17'),
    ('B18', 'Phlm'): ('Philm', 'Philemon', 'Philem', 'B18'),
    ('B19', 'Heb'): ('Heb', 'Hebrews', 'B19'),
    ('B20', 'Jas'): ('James', 'Jam', 'Jas', 'B20'),
    ('B21', '1 Pet'): ('1 Pet', '1Pet', '1 Peter', 'IPet', 'I Pet', 'B21'),
    ('B22', '2 Pet'): ('2 Pet', '2Pet', '2 Peter', 'IIPet', 'II Pet', 'B22'),
    ('B23', '1 John'): ('1 John', '1 Jn', '1Jn', '1John',
                        'I John', 'I Jn', 'IJn', 'I John', 'B23'),
    ('B24', '2 John'): ('2 John', '2 Jn', '2Jn', '2John', 'II John',
                        'II Jn', 'IIJn', 'II John', 'B24'),
    ('B25', '3 John'): ('3 John', '3 Jn', '3Jn', '3John', 'III John',
                        'III Jn', 'IIIJn', 'III John', 'B25'),
    ('B26', 'Jude'): ('Jude', 'Jd', 'B26'),
    ('B27', 'Rev'): ('Rev', 'Revelation', 'B27')
}


def create_full_reference(ref):
    first_character = ref[0:1]
    if first_character.isdigit():
        book = re.sub(r'(\d)(.+)(\d+)', '\\1\\2', ref)
    elif first_character.startswith('B'):
        book = ref[0:3]
        chp = re.sub(book, '', ref)
        chp = re.sub(r'V\d+', '', chp)
        vrs = re.sub(book+chp, '', ref)
        chp = re.sub('K', '', chp)
        vrs = re.sub('V', '', vrs)
    else:
        ref = ref.split('.')
        chp = ref[0]
        vrs = ref[1]
        book = re.sub(r'\d', '', chp)
        chp = re.sub(book, '', chp)
    for x in intf_sbl_books:
        if book in intf_sbl_books[x]:
            book = x[1]
            break
    full_reference = f'{book} {chp}:{vrs}'
    return full_reference


def get_basetext(ref, main_dir):
    full_reference = create_full_reference(ref)
    rp_fname = f"{main_dir}/files/basetext.txt"
    with open(rp_fname, 'r', encoding='utf-8') as file:
        basetext = file.read()
        pass
    basetext = re.search(full_reference + r'(.+)', basetext)
    basetext = re.sub(full_reference, "", basetext.group(0))
    basetext = basetext.strip().split()
    return basetext
