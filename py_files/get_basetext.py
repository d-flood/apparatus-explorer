import re

def create_full_reference(ref):
    ref = ref.split('.')
    chp = ref[0]
    vrs = ref[1]
    if chp.startswith('Matt') or chp.startswith('Mt'):
        book = "Matt"
    elif chp.startswith('Mark') or chp.startswith('Mk'):
        book = "Mark"
    elif chp.startswith('L'):
        book = "Luke"
    elif chp.startswith('John') or chp.startswith('Jn'):
        book = "John"
    elif chp.startswith('Acts') or chp.startswith('Ac'):
        book = "Acts"
    elif chp.startswith('Rev'):
        book = "Rev"
    elif chp.startswith('R'):
        book = "Rom"
    elif (chp.startswith('IC') 
            or chp.startswith('1C') 
            or chp.startswith('1 Cor') 
            or chp.startswith('I Cor') 
            or chp.startswith('1Cor')):
        book = "1Cor"
    elif (chp.startswith('IIC') 
            or chp.startswith('2C') 
            or chp.startswith('2 Cor') 
            or chp.startswith('2 Cor')
            or chp.startswith('2Cor')):
        book = "2Cor"
    elif chp.startswith('G'):
        book = "Gal"
    elif chp.startswith('E'):
        book = "Eph"
    # reduce chp variable to merely the chapter number
    chp = re.sub(chp[0:1], '', chp)
    chp = re.sub(r'\D', '', chp)
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