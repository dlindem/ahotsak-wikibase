input_file = 'D:/Ahotsak/ETC/2022-ETC-lemak-formak.xml'
output_file = 'D:/Ahotsak/ETC/2022-ETC-lemak-formak-utf8.xml'

with open(input_file, 'r', encoding='cp1252') as inp,\
        open(output_file, 'w', encoding='utf-8') as outp:
    for line in inp:
        outp.write(line)
