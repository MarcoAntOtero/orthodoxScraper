from fpdf import FPDF
from datetime import date

# Auto-generated from weekly document
vespers_variable = {'fellowship': '',
 'date': '',
 'memory': 'Memory of our St. Isidore Pelusiotes',
 'stichera': [{'kind': 'verse_prayer',
               'tone': '1',
               'verse': 'If You, O Lord, should mark transgression, O Lord, who would stand? For '
                        'there is forgiveness with You.',
               'prayer': 'We celebrate the divine gift: namely that Christ our God * appeared on '
                         'earth to save us. Being born as an infant * immutably from Mary the '
                         'Virgin, today * in the Temple His Mother brings * Him to His Father and '
                         'God, and He is received * in the arms of Elder Symeon.',
               'text': 'If You, O Lord, should mark transgression, O Lord, who would stand? For '
                       'there is forgiveness with You. We celebrate the divine gift: namely that '
                       'Christ our God * appeared on earth to save us. Being born as an infant * '
                       'immutably from Mary the Virgin, today * in the Temple His Mother brings * '
                       'Him to His Father and God, and He is received * in the arms of Elder '
                       'Symeon.'},
              {'kind': 'verse_prayer',
               'tone': '1',
               'verse': 'Because of Your law, O Lord, I waited for You; my soul waited for Your '
                        'word. My soul hopes in the Lord.',
               'prayer': 'You had appeared to the Prophets, as far as possible * for them of old, '
                         'O Jesus. But now, O God the Logos, * You willingly appeared to the world '
                         'in the flesh * from the Virgin Mary, O Christ, * and You revealed Your '
                         'salvation to all mankind * born of Adam, O benevolent Lord.',
               'text': 'Because of Your law, O Lord, I waited for You; my soul waited for Your '
                       'word. My soul hopes in the Lord. You had appeared to the Prophets, as far '
                       'as possible * for them of old, O Jesus. But now, O God the Logos, * You '
                       'willingly appeared to the world in the flesh * from the Virgin Mary, O '
                       'Christ, * and You revealed Your salvation to all mankind * born of Adam, O '
                       'benevolent Lord.'},
              {'kind': 'verse_prayer',
               'tone': '1',
               'verse': 'From the morning watch until night; from the morning watch until night, '
                        'let Israel hope in the Lord.',
               'prayer': 'You are the One who on Sinai ordered the Law of old, * and now today in '
                         'Zion, You fulfill its injunctions, * accepting to be brought as a babe '
                         'in the flesh * by Your Mother with sacrifice * into the Temple of God, '
                         'and to be embraced * in the arms of Elder Symeon.',
               'text': 'From the morning watch until night; from the morning watch until night, '
                       'let Israel hope in the Lord. You are the One who on Sinai ordered the Law '
                       'of old, * and now today in Zion, You fulfill its injunctions, * accepting '
                       'to be brought as a babe in the flesh * by Your Mother with sacrifice * '
                       'into the Temple of God, and to be embraced * in the arms of Elder Symeon.'},
              {'kind': 'verse_prayer',
               'tone': '4',
               'verse': 'For with the Lord there is mercy, and with Him is abundant redemption; '
                        'and He shall redeem Israel from all his transgressions.',
               'prayer': 'You were lifted to God on high, O all-wise one, throughout your life * '
                         'in both the contemplative and the active life. * Your contemplation was '
                         'founded on the practice of virtues all. * And you wisely loved the '
                         'height * of desires, namely the Lord, * whom you have attained. * You '
                         'were granted a blessed end according to your longing, and illumined * by '
                         'the divine and tri-solar Light.',
               'text': 'For with the Lord there is mercy, and with Him is abundant redemption; and '
                       'He shall redeem Israel from all his transgressions. You were lifted to God '
                       'on high, O all-wise one, throughout your life * in both the contemplative '
                       'and the active life. * Your contemplation was founded on the practice of '
                       'virtues all. * And you wisely loved the height * of desires, namely the '
                       'Lord, * whom you have attained. * You were granted a blessed end according '
                       'to your longing, and illumined * by the divine and tri-solar Light.'},
              {'kind': 'verse_prayer',
               'tone': '4',
               'verse': 'Praise the Lord, all you Gentiles; praise Him, all you peoples.',
               'prayer': 'With the grace of your words, O Saint, * as with showers and waterfalls, '
                         '* godly-minded people are all watered by you. * You put your mouth to '
                         'the chalice of the wisdom of God, as if * to a well, and richly drew * '
                         'for yourself and distributed widely everywhere, * by your letters and '
                         'teachings and your counsels * the divine rays of your doctrines, * '
                         'devout and praiseworthy Isidore.',
               'text': 'Praise the Lord, all you Gentiles; praise Him, all you peoples. With the '
                       'grace of your words, O Saint, * as with showers and waterfalls, * '
                       'godly-minded people are all watered by you. * You put your mouth to the '
                       'chalice of the wisdom of God, as if * to a well, and richly drew * for '
                       'yourself and distributed widely everywhere, * by your letters and '
                       'teachings and your counsels * the divine rays of your doctrines, * devout '
                       'and praiseworthy Isidore.'},
              {'kind': 'verse_prayer',
               'tone': '4',
               'verse': 'For His mercy rules over us; and the truth of the Lord endures forever.',
               'prayer': 'All-devout Saint, through self-control * you indeed put to death the '
                         'mind * set upon the flesh, donning a life-bearing death. * And you '
                         'increased the capacity * of your soul, O Isidore, * manifestly making it '
                         '* more receptive to the divine * Spirit’s gifts of grace. * You became '
                         'thus the vessel of the teachings that were truly God-inspired, * and '
                         'where ineffable wisdom dwelt.',
               'text': 'For His mercy rules over us; and the truth of the Lord endures forever. '
                       'All-devout Saint, through self-control * you indeed put to death the mind '
                       '* set upon the flesh, donning a life-bearing death. * And you increased '
                       'the capacity * of your soul, O Isidore, * manifestly making it * more '
                       'receptive to the divine * Spirit’s gifts of grace. * You became thus the '
                       'vessel of the teachings that were truly God-inspired, * and where '
                       'ineffable wisdom dwelt.'},
              {'kind': 'doxology', 'tone': '4', 'text': 'Glory. Both now. For the Feast.'},
              {'kind': 'prayer',
               'tone': 'grave',
               'text': 'Our Savior, the Light of revelation to the nations, ⁄ You descended from '
                       'heaven to earth! ⁄ You came forth from the Virgin; ⁄ You rested in the '
                       'arms of righteous Simeon. ⁄ It was fitting that an old man should '
                       'recognize You, ⁄ for You came to release him, Giver of life. ⁄⁄ This was '
                       'Your promise, Lord of great mercy!'}],
 'aposticha': [{'kind': 'prayer',
                'tone': '2',
                'text': 'Symeon the devout, * receive the Lord of glory * as once the Holy Spirit '
                        '* revealed to you, O just one. * Behold! for He has now arrived. Verse:'},
               {'kind': 'verse_prayer',
                'tone': '2',
                'verse': 'Lord, now You are letting Your servant depart in peace, according to '
                         'Your word; for my eyes have seen Your salvation which You have prepared '
                         'before the face of all peoples.',
                'prayer': 'Carrying in her arms * the Master and Creator * now as a newborn '
                          'infant, * into the Temple enters the Virgin all-immaculate.',
                'text': 'Lord, now You are letting Your servant depart in peace, according to Your '
                        'word; for my eyes have seen Your salvation which You have prepared before '
                        'the face of all peoples. Carrying in her arms * the Master and Creator * '
                        'now as a newborn infant, * into the Temple enters the Virgin '
                        'all-immaculate.'},
               {'kind': 'verse_prayer',
                'tone': '2',
                'verse': 'A light to bring revelation to the Gentiles, and the glory of Your '
                         'people Israel.',
                'prayer': 'Great and amazing is * the mystery and awesome! * The Master who '
                          'caresses * all things and fashions infants * is handled as a babe in '
                          'arms.',
                'text': 'A light to bring revelation to the Gentiles, and the glory of Your people '
                        'Israel. Great and amazing is * the mystery and awesome! * The Master who '
                        'caresses * all things and fashions infants * is handled as a babe in '
                        'arms.'},
               {'kind': 'prayer',
                'tone': '2',
                'text': 'Today Simeon receives in his arms ⁄ the Lord of glory whom Moses saw of '
                        'old on Sinai ⁄ when in the cloud and darkness he was given the tables of '
                        'the law. ⁄ This is He Who has spoken through the prophets! ⁄ He is the '
                        'Creator of the law! ⁄ This is He Whom David foretold: ⁄⁄ He is fearful to '
                        'all, yet shows us great mercy!'}],
 'apolytikion': [{'kind': 'apolytikion',
                  'title': 'For the Devout Man',
                  'tone': 'pl. 4',
                  'text': 'In you, O Father, is preserved undistorted what was made in the image '
                          'of God; for taking up the cross, you followed Christ and by example '
                          'taught, that we should overlook the flesh, since it passes away, and '
                          'instead look after the soul, since it is immortal. And therefore, O '
                          'devout Isidore, your spirit rejoices with the angels.'},
                 {'kind': 'apolytikion',
                  'title': 'of the Feast',
                  'tone': '1',
                  'text': 'Lady full of grace, rejoice, O Virgin Theotokos, for Christ our God, '
                          'the Sun of righteousness has risen from you and He illumined those in '
                          'darkness. And you, righteous Elder, be glad in heart, receiving in your '
                          'embraces the One who liberates our souls and bestows on us the '
                          'Resurrection.'}]}


#start page then add title and date
pdf = FPDF()
pdf.add_page()
pdf.set_font("Times", size=12)

# Header: Church Name
pdf.set_font("Times", size=12)
pdf.multi_cell(w=0, h=6, text="Georgetown Orthodox Christian Fellowship", align='L', new_x="LMARGIN", new_y="NEXT")

# Date
pdf.multi_cell(w=0, h=6, text="Vespers: Tuesday, April 21, 2026", align='L', new_x="LMARGIN", new_y="NEXT")

# Memory of Saint (In Red)
pdf.set_text_color(255, 0, 0) 
# Use a specific height or ln() to ensure space
pdf.multi_cell(w=0, h=6, text=vespers_variable['memory'], align='L', new_x="LMARGIN", new_y="NEXT")

# Instructions (In Italics & Black)
pdf.set_text_color(0, 0, 0)
pdf.set_font("Times", style="I", size=12)
pdf.multi_cell(w=0, h=6, text="Feel free to read or chant during the service!", align='L', new_x="LMARGIN", new_y="NEXT")
pdf.ln(4) # Adds a small vertical gap before the liturgical text


# Stichera Section and title
pdf.set_font("Times", style='U', size=12) # red and underlined for the title of the section
pdf.set_text_color(255, 0, 0)
pdf.cell(w=0, h=6, text="Stichera", new_x="RIGHT", new_y="TOP")
oldTone = None

# For the long liturgical texts:
for verse_prayer in vespers_variable['stichera']:
        
        # Add the verse in bold
        if verse_prayer['tone'] != oldTone:
                pdf.set_text_color(255, 0, 0) # red for the tone change
                pdf.set_font("Times", style="B", size=12
                             
        pdf.set_font("Times", style="B", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(w=0, h=6, txt=verse_prayer['verse'], align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Add the prayer in regular font
        pdf.set_font("Times", size=12)
        pdf.multi_cell(w=0, h=6, txt=verse_prayer['prayer'], align='L', new_x="LMARGIN", new_y="NEXT")
        
        # Add a small gap between stichera
        pdf.ln(4)






#pdf.output("simple_output.pdf")
