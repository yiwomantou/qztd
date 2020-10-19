# -*- coding: UTF-8 -*-
'''
---------------------------------------------------------------
2019-06-10: 1.更改parentasin解析方式 @get_parentasin_var
2019-06-14: 1.增加抓取变体asin @variant_list
            2.修复排名数据抓取错误
2019-07-15  1.处理音乐类商品出错的问题
            2.修复video类目价格错误
2019-11-19  1.增加品牌为图片的解析方式,并改进了品牌解析函数
2020-05-07  1.增加A+页面HTML
---------------------------------------------------------------
'''
import re
import time
import json
import random

from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs


class productDetailParse(object):
    def __init__(self):
        self.html_selector = None  # etree.HTML(html)
        self.html_soup = None  # BeautifulSoup(html,features="lxml")
        self.countryCode = 'us'  # countryCode
        self.categoryIndexArr = {
            "us": {
                "Home & Kitchen": 1055398, "Office Products": 1064954, "Musical Instruments": 11091801,
                "Amazon Launchpad": 12034488011, "Kindle Store": 133140011, "Kitchen & Dining": 13900821,
                "Automotive": 15684181, "Industrial & Scientific": 16310091, "Grocery & Gourmet Food": 16310101,
                "Digital Music": 163856011, "Toys & Games": 165793011, "Baby": 165796011,
                "Electronics": 172282, "Gift Cards": 2238192011, "Tools & Home Improvement": 228013,
                "Software": 229534, "Cell Phones & Accessories": 2335752011, "Apps & Games": 2350149011,
                "Arts, Crafts & Sewing": 2617941011, "Appliances": 2619525011, "Pet Supplies": 2619533011,
                "Movies & TV": 2625373011, "Books": 283155, "Patio, Lawn & Garden": 2972638011,
                "Sports Collectibles": 3250697011, "Sports & Outdoors": 3375251, "Health & Household": 3760901,
                "Beauty & Personal Care": 3760911, "Video Games": 468642, "Camera & Photo": 502394,
                "Entertainment Collectibles": 5088769011, "CDs & Vinyl": 5174, "Computers & Accessories": 541966,
                "Magazine Subscriptions": 599858, "Clothing, Shoes & Jewelry": 7141123011,
                "Collectible Coins": 9003130011
            },
            "jp": {
                "Home & Kitchen": 1055398, "Office Products": 1064954, "Musical Instruments": 11091801,
                "Amazon Launchpad": 12034488011, "Kindle Store": 133140011, "Kitchen & Dining": 13900821,
                "Automotive": 15684181, "Industrial & Scientific": 16310091, "Grocery & Gourmet Food": 16310101,
                "Digital Music": 163856011, "Toys & Games": 165793011, "Baby": 165796011,
                "Electronics": 172282, "Gift Cards": 2238192011, "Tools & Home Improvement": 228013,
                "Software": 229534, "Cell Phones & Accessories": 2335752011, "Apps & Games": 2350149011,
                "Arts, Crafts & Sewing": 2617941011, "Appliances": 2619525011, "Pet Supplies": 2619533011,
                "Movies & TV": 2625373011, "Books": 283155, "Patio, Lawn & Garden": 2972638011,
                "Sports Collectibles": 3250697011, "Sports & Outdoors": 3375251, "Health & Household": 3760901,
                "Beauty & Personal Care": 3760911, "Video Games": 468642, "Camera & Photo": 502394,
                "Entertainment Collectibles": 5088769011, "CDs & Vinyl": 5174, "Computers & Accessories": 541966,
                "Magazine Subscriptions": 599858, "Clothing, Shoes & Jewelry": 7141123011,
                "Collectible Coins": 9003130011
            },
            "xx": {
                'ビューティー': 52374051, 'jp-stores': 579684, 'DVD': 561958, 'ゲーム': 637394, '産業・研究開発用品': 3445393051,
                'Prime Video': 2351649051, 'スポーツ＆アウトドア': 14304371, '洋書': 52033011, '食品・飲料・お酒': 57239051,
                '車＆バイク': 2017304051, 'シューズ＆バッグ': 2016926051, 'ジュエリー': 85895051, '腕時計': 324025011, 'ホビー': 2277721051,
                'DIY・工具・ガーデン': 2016929051, 'ペット用品': 2127212051, 'ホーム＆キッチン': 3828871, '文房具・オフィス用品': 86731051,
                '楽器・音響機器': 2123629051, 'ドラッグストア': 160384011, 'デジタルミュージック': 2128134051, '家電＆カメラ': 3210981,
                '大型家電': 2277724051, '服＆ファッション小物': 352484011, 'おもちゃ': 13299531, 'PCソフト': 637392, 'ミュージック': 561956,
                'ベビー＆マタニティ': 344845011, 'パソコン・周辺機器': 2127209051, 'Amazonデバイス・アクセサリ': 4976279051,
                'Androidアプリ': 2381130051, 'Kindleストア': 2250738051, 'ギフト券': 2351652051, 'ファッション': 2229202051, '本': 465392
            },
            "de": {
                'Haustier': 340852031, 'DVD & Blu-ray': 284266, 'Küche, Haushalt & Wohnen': 3167641,
                'Auto & Motorrad': 78191031, 'Lebensmittel & Getränke': 340846031,
                'Prime Video': 3010075031, 'Amazon Launchpad': 9418395031,
                'Musik-CDs & Vinyl': 255882, 'Bürobedarf & Schreibwaren': 192416031,
                'Beleuchtung': 213083031, 'Kamera & Foto': 571860,
                'Beauty': 84230031, 'Elektronik & Foto': 562066, 'Spielzeug': 12950651,
                'Schuhe & Handtaschen': 355006011, 'Baby': 355007011,
                'Elektro-Großgeräte': 908823031, 'Bekleidung': 77028031,
                'Gewerbe, Industrie & Wissenschaft': 5866098031, 'Zeitschriften': 1161658,
                'Sport & Freizeit': 16435051, 'Musikinstrumente & DJ-Equipment': 340849031,
                'Bücher': 186606, 'Amazon-Geräte & Zubehör': 12598632031,
                'Fremdsprachige Bücher': 52044011, 'Games': 300992, 'Handmade Produkte': 9699311031,
                'Koffer, Rucksäcke & Taschen': 2454118031, 'Geschenkgutscheine': 1571256031,
                'Musik-Downloads': 77195031, 'Software': 301927, 'Sonstiges': 72921031,
                'Computer & Zubehör': 340843031, 'Apps & Spiele': 1661648031,
                'Drogerie & Körperpflege': 64187031, 'Uhren': 193707031, 'Schmuck': 327472011,
                'Garten': 10925031, 'Baumarkt': 80084031, 'Kindle-Shop': 530484031
            },
            "uk": {
                'Home & Garden Store': 3146281, 'DVD & Blu-ray': 283920, 'Shoes & Bags': 355005011,
                'Stationery & Office Supplies': 192413031, 'Prime Video': 3010085031,
                'CDs & Vinyl': 229816, 'Garden & Outdoors': 11052671, 'Handmade Products': 9699254031,
                'Large Appliances': 908798031, 'Health & Personal Care': 65801031,
                'Musical Instruments & DJ': 340837031, 'Beauty': 117332031, 'Automotive': 248877031,
                'Pet Supplies': 340840031, 'Apps & Games': 1661657031, 'Gift Cards': 1571304031,
                'Lighting': 213077031, 'Computers & Accessories': 340831031,
                'Sports & Outdoors': 318949011, 'Everything Else': 72911031, 'Grocery': 340834031,
                'Luggage': 2454166031, 'Amazon Devices & Accessories': 12598575031,
                'Business, Industry & Science': 5866054031, 'Digital Music': 77197031,
                'DIY & Tools': 79903031, 'Software': 300435, 'Jewellery': 193716031,
                'Electronics & Photo': 560798, 'Baby Products': 59624031, 'Kindle Store': 341677031,
                'Watches': 328228011, 'Toys & Games': 468292, 'Books': 266239, 'Clothing': 83450031,
                'PC & Video Games': 300703, "Amazon Launchpad": 7212961031, "Home & Kitchen": 11052681
            },
            "fr": {
                'Bricolage': 590748031, 'Animalerie': 1571268031, 'Hygiène et Santé': 197861031,
                'Livres': 301061, 'DVD & Blu-ray': 405322, 'Boutique chèques-cadeaux': 2524127031,
                'Vêtements': 340855031, 'Fournitures de bureau': 192419031, 'Informatique': 340858031,
                'Téléchargement de Musique': 77196031, 'Chaussures et Sacs': 215934031,
                'Montres': 60649031, 'Appareils Amazon et Accessoires': 12598689031,
                'Bébé & Puériculture': 206617031, 'Luminaires & Eclairage': 213080031,
                'High-Tech': 13921051, 'Logiciels': 530488, 'Amazon Launchpad': 10525448031,
                'Gros électroménager': 908826031, 'Jeux vidéo': 530490, 'Beauté et Parfum': 197858031,
                'Bijoux': 193710031, 'Epicerie': 3635788031, 'Auto et Moto': 1571265031,
                'Livres anglais et étrangers': 52042011, 'Instruments de musique et Sono': 340861031,
                'Jeux et Jouets': 322086011, 'Sports et Loisirs': 325614031, 'Autres': 72919031,
                'Commerce, Industrie et Science': 5866109031, 'Cuisine & Maison': 57004031,
                'CD & Vinyles': 301062, 'Applis et Jeux': 1661654031, 'Boutique Kindle': 672108031,
                'Bagages': 2454145031, 'Jardin': 3557027031, 'Produits Handmade': 9699368031
            },
            "it": {
                'Abbigliamento': 2844433031, 'Alimentari e cura della casa': 6198092031, 'Altro': 425919031,
                'Auto e Moto': 1571280031,
                'Bellezza': 6198082031, 'Cancelleria e prodotti per ufficio': 3606310031, 'Casa e cucina': 524015031,
                'CD e Vinili': 412600031,
                'Commercio, Industria e Scienza': 5866068031, 'Elettronica': 412609031, 'Fai da te': 2454160031,
                'Film e TV': 412606031,
                'Giardino e giardinaggio': 635016031, 'Giochi e giocattoli': 523997031, 'Gioielli': 2454163031,
                'Illuminazione': 1571292031,
                'Informatica': 425916031, 'Libri': 411663031, 'Libri in altre lingue': 433842031,
                'Musica Digitale': 1748203031,
                'Orologi': 524009031, 'Prima infanzia': 1571286031, 'Prodotti per animali domestici': 12472499031,
                'Salute e cura della persona': 1571289031, 'Scarpe e borse': 524006031,
                'Sport e tempo libero': 524012031,
                'Strumenti Musicali': 3628629031, 'Valigeria': 2454148031, 'Videogiochi': 412603031,
                'App e Giochi': 1661660031,
                'Buoni regalo': 3557017031, 'Dispositivi Amazon & Accessori': 12598749031,
                'Grandi elettrodomestici': 14437356031,
                'Kindle Store': 818937031, 'Prodotti Handmade': 9699425031, 'Software': 412612031
            },
            "es": {
                'Alimentación y bebidas': 6198072031, 'Bebé': 1703495031, 'Belleza': 6198054031,
                'Bricolaje y herramientas': 2454133031,
                'CDs y vinilos': 599373031, 'Coche y moto': 1951051031, 'Deportes y aire libre': 2454136031,
                'Electrónica': 599370031,
                'Equipaje': 2454129031, 'Hogar y cocina': 599391031, 'Iluminación': 3564289031,
                'Industria, empresas y ciencia': 5866088031,
                'Informática': 667049031, 'Instrumentos musicales': 3628866031, 'Jardín': 1571259031,
                'Joyería': 2454126031,
                'Juguetes y juegos': 599385031, 'Libros': 599364031, 'Libros en idiomas extranjeros': 599367031,
                'Música Digital': 1748200031,
                'Oficina y papelería': 3628728031, 'Otros Productos': 667040031, 'Películas y TV': 599379031,
                'Productos para mascotas': 12472654031, 'Relojes': 599388031, 'Ropa': 2846220031,
                'Salud y cuidado personal': 3677430031,
                'Videojuegos': 599382031, 'Zapatos y complementos': 1571262031, 'Grandes electrodomésticos': 4772050031,
                'Productos Handmade': 9699482031, 'Software': 599376031, 'Tienda Kindle': 818936031,
                'Apps y Juegos': 1661649031, 'Cheques regalo': 3564279031,
                'Dispositivos Amazon y Accesorios': 12598806031
            },
            'in':
                {'Bags, Wallets and Luggage': 2454169031, "Baby": 1571274031, "Beauty": 1355016031, "Books": 976389031,
                 "Car & Motorbike": 4772060031,
                 "Clothing & Accessories": 1571271031, "Computers & Accessories": 976392031, "Electronics": 976419031,
                 "Grocery & Gourmet Foods": 2454178031,
                 "Health & Personal Care": 1350384031, "Home & Kitchen": 976442031, "Home Improvement": 3704992031,
                 "Industrial & Scientific": 5866078031,
                 "Jewellery": 1951048031, "Movies & TV Shows": 976416031, "Music": 976445031,
                 "Musical Instruments": 3677697031, "Office Products": 2454172031,
                 'Outdoor Living': 2454175031, 'Pet Supplies': 2454181031, "Shoes & Handbags": 1571283031,
                 'Sports, Fitness & Outdoors': 1984443031,
                 "Toys & Games": 1350380031, 'Video Games': 976460031, "Watches": 1350387031, "Software": 976451031
                 },
            'br': {"Apps e Jogos": 6446175011, "Bebê": 17242603011, 'Beleza': 16194414011,
                   'Binquedos e Jogos': 16194299011, 'Alimentos e Bebidas': 18991079011,
                   "Jardim e Piscina": 18991021011,
                   'Casa': 16191000011, "CD e Vinil": 7791937011, 'Computadores e Informática': 16339926011,
                   'Cozinha': 16957125011, "DVD e Blu-ray": 7791856011, 'Eletrodomésticos': 16522082011,
                   'Eletrônicos': 16209062011, 'Esporte': 17349396011,
                   'Ferramentas e Materiais de Construção': 16957182011, 'Games e Consoles': 7791985011,
                   'Livros': 6740748011, "Loja Kindle": 5308307011, 'Moda': 17365811011,
                   "Papelaria e Escritório": 16957239011, "Saúde": 16215417011, "Pet Shop": 18991136011,
                   "Automotivo": 18914209011},

            'au': {"Alexa Skills": 4931595051, "Apps & Games": 2544160051, "Automotive": 4851453051, "Baby": 4851510051,
                   "Beauty": 4851567051,
                   "Books": 4851626051, "CDs & Vinyl": 4852330051, "Clothing, Shoes & Accessories": 4851856051,
                   "Computers": 4851683051, "Electronics": 4851799051,
                   "Everything Else": 4103126051, 'Health, Household & Personal Care': 4851917051, 'Home': 4851975051,
                   "Home Improvement": 4852033051,
                   "Kindle Store": 2490359051, "Kitchen & Dining": 4852150051, "Lighting": 4852207051,
                   "Movies & TV": 4852264051, 'Pantry Food & Drinks': 5547635051,
                   'Pet Supplies': 5514967051, 'Software': 4852502051, 'Sports, Fitness & Outdoors': 4852559051,
                   'Stationery & Office Products': 4852445051,
                   'Toys & Games': 4852617051, 'Video Games': 4852675051},
            'ca': {
                'Automotive': 6948389011, "Baby": 3561346011, "Beauty & Personal Care": 6205124011, "Books": 916520,
                "Clothing & Accessories": 8604903011, "Electronics": 667823011,
                'Everything Else': 2356392011, "Featured Stores": 916516, 'Grocery & Gourmet Food': 6967215011,
                'Health & Personal Care': 6205177011, "Home": 2206275011,
                'Industrial & Scientific': 11076213011, 'Jewelry': 6205496011, 'Livres': 916522,
                'Luggage & Bags': 6205505011, 'Movies & TV': 917972, 'Music': 916514,
                'Musical Instruments, Stage & Studio': 6916844011,
                'Office Products': 6205511011, 'Patio, Lawn & Garden': 6205499011, 'Pet Supplies': 6205514011,
                'Shoes & Handbags': 8604915011, 'Sports & Outdoors': 2242989011, 'Tools & Home Improvement': 3006902011,
                'Toys & Games': 6205517011, 'Video': 916518, 'Video Games': 3198031, 'Watches': 2235620011
            },
            'ae': {
                "Appliances": 15149781031, "Automotive": 11498031031, "Baby Products": 11498088031,
                "Beauty": 11497860031,
                "Books": 11497689031, "Computers": 11497746031, "Electronics": 11601327031, "Fashion": 11497632031,
                "Grocery": 15150009031, "Health": 11601441031, "Home": 16725681031, "Kitchen": 16402718031,
                "Mobile Phones & Communication Products": 12303750031, "Office Products": 15150351031,
                "Pet Supplies": 15150408031,
                "Sporting Goods": 11601213031, "Tools & Home Improvement": 11601270031, "Toys": 11497803031,
                "Videogames": 11601384031,
            },
            "mx": {
                "Industria, Empresas y Ciencia": 11076223011, "Juguetes y Juegos": 11260442011,
                "Productos para Animales": 11782336011,
                "Ropa, Zapatos y Accesorios": 13848838011, "Automotriz y Motocicletas": 13848848011,
                "Instrumentos Musicales": 13848858011,
                "Tienda Kindle": 6446439011, "Libros": 9298576011, "Electrónicos": 9482558011,
                "Hogar y Cocina": 9482593011,
                "Salud, Belleza y Cuidado Personal": 9482610011, "Música": 9482620011,
                "Películas y Series de TV": 9482630011,
                "Videojuegos": 9482640011, "Bebé": 9482650011, "Deportes y Aire libre": 9482660011,
                "Herramientas y Mejoras del Hogar": 9482670011,
                "Software": 9482690011, "Oficina y Papelería": 9673844011
            },
            "tr": {
                "Oyuncak": 12467126031, "Spor ve Outdoor": 12467068031, "Mutfak": 12466781031,
                "Ofis ve Kırtasiye": 12467009031, "Kitap": 12466380031,
                "Yapı Market": 12466724031, "Kadın Modası": 13546651031, "Ev ve Yaşam": 12466667031,
                "Elektronik": 12466496031, "Erkek Modası": 13546649031,
                "Bebek": 12466208031, "Diğer Her Şey": 12467297031, "Bilgisayarlar": 12466439031, "Moda": 12466553031,
                "Video Oyunu ve Konsol": 12467183031
            }
        }

    @property
    def initial_data(self):
        return self.html_soup, self.html_selector

    @initial_data.setter
    def initial_data(self, html):
        self.html = html
        self.html_soup = BeautifulSoup(html, features="lxml")
        self.html_selector = etree.HTML(html)
        try:
            self.img_obj = imgs = json.loads(
                re.findall("'colorImages': (\{.+\}\]\})", html)[0].replace("'initial'", '"initial"'))
        except:
            self.img_obj = None

    @property
    def country(self):
        return self.countryCode

    @country.setter
    def country(self, country):
        if country in self.categoryIndexArr:
            self.countryCode = country
        else:
            raise ValueError("countryCode only support %s" % str(self.categoryIndexArr.keys()))

    @property
    def frequently_bought_asins(self):
        related_products = []
        selector = self.html_selector
        li = selector.xpath("//*[@id='sims-fbt-form']/div[1]/ul/li")

        for i in li:
            href = i.xpath("./span/a/@href")
            if len(href) > 0:
                # print(re.findall("dp/.*?/", href[0])[0][3:-1], '======')
                related_products.append(re.findall("dp/.*?/", href[0])[0][3:-1])
            else:
                continue
        # print(related_products)
        return related_products

    @property
    def also_viewed_asins(self):
        # c_w_v_parse
        target_data = []
        try:
            selector = etree.HTML(str(self.html_soup.select('#desktop-dp-sims_session-similarities-sims-feature')[0]))
            data = selector.xpath(
                "//div[@id='desktop-dp-sims_session-similarities-sims-feature']/div/@data-a-carousel-options")[0]
        except:
            return target_data
        data = eval(data)
        params = data["ajax"]["params"]
        params["asins"] = ",".join(data["ajax"]["id_list"])
        params["count"] = 500
        params["offset"] = data["set_size"]
        params["_"] = str(int(time.time() * 1000))
        target_data = [i[:-1:] for i in data["ajax"]["id_list"]]
        return target_data

    @property
    def reviewMentionedWords(self):
        mw_list = []
        mw = self.html_selector.xpath(
            '//div[@data-hook="lighthut-terms-list"]/div[@class="cr-lighthouse-terms"]/span[@class="a-declarative"]/a/span/text()')
        for x in mw:
            mw_list.append(x.strip())
        return mw_list

    @property
    def also_bought_asins(self):
        # c_w_b_parse
        target_data = []
        try:
            selector = etree.HTML(str(self.html_soup.select('#desktop-dp-sims_purchase-similarities-sims-feature')[0]))
        except:
            return target_data
        data = \
            selector.xpath(
                "//div[@id='desktop-dp-sims_purchase-similarities-sims-feature']/div/@data-a-carousel-options")[
                0]
        data = eval(data)
        params = data["ajax"]["params"]
        params["asins"] = ",".join(data["ajax"]["id_list"])
        params["count"] = 500
        params["offset"] = data["set_size"]
        params["_"] = str(int(time.time() * 1000))
        target_data = [i[:-1:] for i in data["ajax"]["id_list"]]
        return target_data

    @property
    def sponsored_asins_1(self):
        index = []
        try:
            selector = etree.HTML(str(self.html_soup.select('#sp_detail2')[0]))
        except:
            return index
        data = selector.xpath("//div[@id='sp_detail2']/@data-a-carousel-options")[0]
        index = json.loads(data)["initialSeenAsins"]
        return index

    @property
    def sponsored_asins_2(self):
        index = []
        try:
            selector = etree.HTML(str(self.html_soup.select('#sp_detail')[0]))
        except:
            return index
        data = selector.xpath("//div[@id='sp_detail']/@data-a-carousel-options")[0]
        index = json.loads(data)["initialSeenAsins"]
        return index

    @property
    def similar_asins(self):
        asin_list = []
        try:
            selector = etree.HTML(str(self.html_soup.select('#HLCXComparisonTable')[0]))
        except:
            return asin_list
        ths = selector.xpath("//*[@id='HLCXComparisonTable']/tr[1]/th")
        for th in ths:
            product_url = th.xpath('.//a')
            if len(product_url) > 0:
                try:
                    asin_list.append(re.findall("dp/.*?/", product_url)[0][3:-1])
                except:
                    pass
            else:
                continue
        return asin_list

    @property
    def availability(self):
        selector = self.html_selector
        stock_status = 0
        quantity = -1
        try:
            temp_flag = selector.xpath('//div[@id="availability"]/span/text()')[0].strip()
            # print("==================")
            # print(temp_flag)
        except:
            pass
        else:
            if self.countryCode in ['us', 'uk', 'au', 'ca', 'in', 'ae']:
                if 'In stock on' in temp_flag:
                    stock_status = 2
                elif "Currently unavailable" in temp_flag:
                    stock_status = 1
                elif 'left in stock' in temp_flag:
                    # quantity = int(re.findall('\d+',temp_flag)[0])
                    stock_status = 3

            elif self.countryCode == 'jp':
                if '発売予定日' in temp_flag:
                    stock_status = 2
                elif '現在在庫切れです' in temp_flag:
                    stock_status = 1
            elif self.countryCode == 'de':
                if 'Lieferbar ab dem' in temp_flag:
                    stock_status = 2
                elif 'Derzeit nicht verfügbar' in temp_flag:
                    stock_status = 1
            elif self.countryCode == 'fr':
                if 'Actuellement indisponible' in temp_flag:
                    stock_status = 1
                elif 'En stock le' in temp_flag:
                    stock_status = 2
            elif self.countryCode == 'es':
                if 'No disponible' in temp_flag:
                    stock_status = 1
                elif 'Disponible el' in temp_flag:
                    stock_status = 2
            elif self.countryCode == 'it':
                if 'Attualmente non disponibile' in temp_flag:
                    stock_status = 1
                elif 'Disponibilità' in temp_flag:
                    stock_status = 2
        return stock_status, quantity

    @property
    def address(self):
        addr = self.html_selector.xpath('//span[@id="glow-ingress-line2"]/text()')
        if addr:
            return addr[0]

    def best_seller_rank(self):
        selector = self.html_selector
        soup = self.html_soup
        temp_data = {"rank": 0, "category": '', "catId": 0}
        li = []
        text = None
        try:
            selector = etree.HTML(str(soup.select('#SalesRank')[0]))
            li = selector.xpath("//*[@id='SalesRank']")[0]
            text_bsr = li.xpath('./*[@class="value"]/text()')  #
            print("--===", text_bsr)
            if len(text_bsr) > 0:
                text = text_bsr[0].strip()[:-1]
            else:
                text = li.xpath("./text()")[1].strip()[:-1]
            if text == '':
                self.rank = int(temp_data['rank'])
                self.category = temp_data['category']
                self.catId = temp_data['catId']
                return
        except Exception as e:
            try:
                selector = etree.HTML(str(soup.select('#productDetails_detailBullets_sections1')[0]))
                trs = selector.xpath("//*[@id='productDetails_detailBullets_sections1']//tr")
                first_date_available = trs.xpath('/td/text()')[-1]
                for tr in trs:
                    tag_text = tr.xpath("./th[1]/text()")[0].strip()
                    if "Rank" in tag_text or "Bestseller-Rang" in tag_text or "d'Amazon" in tag_text or 'Amazon' in tag_text:
                        bsr_text = tr.xpath("./td/span/span[1]/a/text()")[0].strip()
                        rank_text = tr.xpath("./td/span/span[1]/text()")[0].strip()
                        if 'op 100' in bsr_text.lower():
                            text = rank_text
                        else:
                            self.rank = int(temp_data['rank'])
                            self.category = temp_data['category']
                            self.catId = temp_data['catId']
                            return

            except Exception as e:
                try:
                    texts = selector.xpath('//*[@class="column col2 "]//div[@class="pdTab"]')[0]
                    text_temp = texts.xpath('string(.)').replace('\n', '').replace('  ', '')
                    if self.countryCode == 'de':
                        regex_str = '(Amazon Bestseller-Rang:.+\))'
                    elif self.countryCode == 'es':
                        regex_str = '(vendidos de Amazon:.+\))'
                    elif self.countryCode == 'it':
                        regex_str = '(Bestseller di Amazon:.+\))'
                    elif self.countryCode in ['uk', 'in', 'us', 'ca', 'ae']:
                        regex_str = '(Amazon Bestsellers Rank:.+\))'
                    elif self.countryCode == 'fr':
                        regex_str = "(ventes d'Amazon:.+\))"
                    elif self.countryCode == 'jp':
                        regex_str = "Amazon.+?:(.+?\))"
                    text = re.findall(regex_str, text_temp)[0].split('(')[0]
                except Exception as e:
                    tr = selector.xpath('//div[@id="detailBulletsWrapper_feature_div"]/ul[1]/li/span')
                    if len(tr) > 0:
                        tr = tr[0]
                        tag_text = tr.xpath('./span/text()')
                        if len(tag_text) > 0:
                            tag_text = tag_text[0]
                            if "Rank" in tag_text or "Bestseller-Rang" in tag_text or "d'Amazon" in tag_text or 'Amazon' in tag_text:
                                bsr_text = tr.xpath("./a/text()")
                                if len(bsr_text) > 0:
                                    bsr_text = bsr_text[0].strip()
                                rank_text = tr.xpath("./text()")
                                if len(rank_text) > 0:
                                    rank_text = rank_text[1].strip().replace(' (', '')
                                if 'op 100' in bsr_text.lower():
                                    text = rank_text
                                else:
                                    self.rank = int(temp_data['rank'])
                                    self.category = temp_data['category']
                                    self.catId = temp_data['catId']
                                    return

        if text is not None:
            text = text.split('(')[0]
            print('============', text)
            if self.countryCode == 'jp':
                arr = text.split(' in ')
                print('======a======', arr)
            elif self.countryCode == 'de':
                arr = text.split(' in ')
            elif self.countryCode in ['mx']:
                arr = text.split(' en ')
            elif self.countryCode == 'uk':
                arr = text.split(' in ')
            elif self.countryCode == 'it':
                arr = text.split(' in ')
            elif self.countryCode == 'es':
                arr = text.split(' en ')
            elif self.countryCode == 'br':
                arr = text.split(' em ')
            elif self.countryCode == 'tr':
                arr = text.split(' kate')
            elif self.countryCode == 'fr':
                arr = text.split(' in ')
            else:
                arr = text.split(' in ')
            # print('============', text)
            rank = ''.join(re.findall('(\d+)', text))
            print('============', rank)
            temp_data["rank"] = rank
            if self.countryCode == 'jp':
                print('============', arr)
                temp_data['category'] = arr[1].strip()
            elif self.countryCode == 'tr':
                temp_data['category'] = arr[0]
            else:
                # print(arr, '---============')
                try:
                    temp_data['category'] = str(arr[1].strip())
                except:
                    temp_data['category'] = str(text.split(' in ')[1].strip())

            if temp_data['category'] in self.categoryIndexArr[self.countryCode].keys():
                temp_data['catId'] = self.categoryIndexArr[self.countryCode][temp_data['category']]
            elif self.countryCode == 'fr' and 'tements' in temp_data['category']:
                temp_data['catId'] = 340855031
            else:
                temp_data['category'] = ''
                temp_data['catId'] = 0
        self.rank = int(temp_data['rank'])
        self.category = temp_data['category']
        self.catId = temp_data['catId']

    @property
    def title(self):
        selector = self.html_selector
        title = selector.xpath('//h1[@id="title"]/span/text()')
        if len(title) == 0:
            title_m = selector.xpath('//div[@id="dmusicProductTitle_feature_div"]/h1/text()')
            title_v = selector.xpath('//div[@class="av-detail-section"]')
            title_a = selector.xpath('//div[@id="mobileApplicationSubtitle_feature_div"]')
            if len(title_m) > 0 or len(title_v) > 0 or len(title_a) > 0:
                raise ValueError('Music')
        return title[0].strip()

    @property
    def img_url(self):
        img = ''
        img_sort = ['hiRes', 'thumb', "large"]
        if self.img_obj and self.img_obj['initial']:
            imgs = self.img_obj['initial'][0]
            key = 'hiRes'
            for k in img_sort:
                if imgs[k]:
                    key = k
                    break
            img_tmp = imgs[key].split('/')[-1]
            img_l = img_tmp.split('.')
            img = '{}.{}'.format(img_l[0], img_l[-1])
        return img

    @property
    def brand(self):
        selector = self.html_selector
        brand = selector.xpath('//div[@id="bylineInfo_feature_div"]/div/a/text()')
        if len(brand) == 0:
            brand = selector.xpath('//div[@id="byline"]/span/span/a/text()')
        if len(brand) == 0:
            brand = selector.xpath("//a[@id='bylineInfo']/text()")
        if len(brand) == 0:
            brand = selector.xpath("//a[@id='brand']/text()")
        if len(brand) > 0:
            brand = brand[0]
        else:
            brand = ""
        return brand

    @property
    def price(self):
        selector = self.html_selector
        price = selector.xpath('//*[@id="priceblock_ourprice"]/text()')
        if len(price) == 0:
            price = selector.xpath('//span[@id="priceblock_dealprice"]/text()')
        if len(price) == 0:
            price = selector.xpath('//div[@id="unqualifiedBuyBox"]/div/div/span[@class="a-color-price"]/text()')
        if len(price) == 0:
            price = selector.xpath('//span[@class="a-size-base a-color-price offer-price a-text-normal"]/text()')
        if len(price) == 0:
            price = selector.xpath('//span[@class="a-size-base a-color-price a-color-price"]/text()')
        # if len(price) == 0:
        #     price = selector.xpath('//span[@class="a-size-base a-color-secondary"]/text()')
        if len(price) == 0:
            price = selector.xpath('//span[@class="a-size-medium a-color-price"]/text()')
        if len(price) == 0:
            price = selector.xpath('//span[@id="priceblock_saleprice"]/text()')
        # if len(price) == 0:
        #     price = selector.xpath('//')
        if len(price) > 0:
            price = price[0].split('-')[0]
            try:
                price = float(''.join(re.findall('\d+', price)))
            except Exception as e:
                try:
                    price = selector.xpath('string(//*[@id="priceblock_ourprice"])')
                    price = '_' + price + '_'
                    price = price.split('-')[0]
                    price_string = ''.join(re.findall('[\.\d+]', price))
                    if '.' not in price_string:
                        price = float(price_string)
                    else:
                        price = float(price_string[:(len(price_string) - 1) // 2])
                except Exception as e:
                    print(e)
                    price = -1
        else:
            price = -1
        if self.countryCode != 'jp':
            price = float(price) / 100
        return price

    def revews_rating(self):
        rating_ratio = []
        soup = self.html_soup
        selector = etree.HTML(str(soup.select('#histogramTable')[0]))
        table = selector.xpath("//table[@id='histogramTable']")
        if len(table) > 0:
            tr_list = table[0].xpath("tr")
            for tr in tr_list:
                start = tr.xpath('td[3]/a/text()')
                if len(start) > 0:
                    start = start[0].replace('%', '')
                else:
                    start = 0
                rating_ratio.append(int(start))
        selector = self.html_selector
        CustomerReviews = selector.xpath('//div[@id="averageCustomerReviews"]')
        if len(CustomerReviews) > 0:
            rate = CustomerReviews[0].xpath('span/span/span/a/i/span/text()')
            if len(rate) > 0:
                rating = float(re.findall("(\d.\d)", rate[0].replace(',', '.'))[0])
            else:
                rating = 0
            reviews = selector.xpath('//*[@id="acrCustomerReviewText"]/text()')
            if len(reviews) > 0:
                try:
                    reviews = reviews[0].split()[0].strip()
                    reviews = ''.join(re.findall('\d+', reviews))
                except:
                    reviews = 0
            else:
                reviews = 0
        else:
            reviews = 0
            rating = 0

        self.reviews = int(reviews)
        self.rating = float(rating)
        self.rating_ratio = rating_ratio

    @property
    def QA_num(self):
        selector = self.html_selector
        qa_num = -1
        other_qa_num = 0
        try:
            qaNum = selector.xpath("//*[@id='askATFLink']/span/text()")[0].strip()
            qa_num = int(''.join(re.findall('\d+', qaNum)))
        except:
            pass
        return qa_num

    def seller_info(self):
        selector = self.html_selector
        seller_type = 0
        seller_num = 1
        merchant = ''
        try:
            merchant = selector.xpath("//*[@id='merchant-info']")
            if len(merchant) == 0:
                merchant = selector.xpath("//*[@id='tabular_feature_div']")
            merchant = merchant[0]
            merchantName = merchant.xpath('.//a[@id="sellerProfileTriggerId"]/text()')
            merchantUrl = merchant.xpath('.//a[@id="sellerProfileTriggerId"]/@href')
            if len(merchantName) == 0:
                if 'Amazon' in merchant.xpath('./text()')[0].strip():
                    seller_type = 1
                    merchantName = "Amazon.com"
                    merchantUrl = ''
                else:
                    seller_type = 1
                    merchantName = "Amazon.com"
                    merchantUrl = '-'
                    # pass
                    # raise ValueError
            else:
                merchantInfo = parse_qs(urlparse(merchantUrl[0]).query)
                merchantName = merchantName[0]
                if merchantInfo.get("isAmazonFulfilled") is not None:
                    seller_type = 2
                else:
                    seller_type = 3
                if len(merchantUrl) == 0:
                    merchantUrl = ''
                else:
                    try:
                        merchantUrl = re.findall('&seller=(.*?)&', merchantUrl[0])[0]
                    except:
                        try:
                            merchantUrl = merchantUrl[0].split('seller=')[-1]
                        except:
                            pass
        except Exception as e:
            merchantName = ''
            merchantUrl = ''
            # seller_type = None
            seller_type = 0
            # with open('~/test.html', 'w')as f:
            #     f.write(str(self.html_selector))
            # print(e,'--=-=====11111111111111111111')
        seller_num = selector.xpath("//div[@id='olp_feature_div']/div/span/a/text()")
        if len(seller_num) == 0:
            seller_num = selector.xpath("//span[@id='mbc-olp-link']/a/text()")
            # if len(seller_num) > 0:
            #   seller_num = ['(' + seller_num[0].split('\xa0')[0] + ')']
        if len(seller_num) == 0:
            seller_num = selector.xpath('//div[@id="olpLinkWidget_feature_div"]/div/span/a/div/div/span/text()')
        if len(seller_num) > 0:
            # print(seller_num,'===')
            try:
                seller_num = int(seller_num[0].split(')')[0].split('(')[1])
            except:
                seller_num = 1
        else:
            seller_num = 1
        self.seller_num = seller_num
        self.seller_type = seller_type
        self.merchantName = merchantName
        self.merchantUrl = merchantUrl

    @property
    def description(self):
        desc_dict = {}
        feature = []
        selector = self.html_selector
        try:
            descs = selector.xpath('//ul[@class="a-unordered-list a-vertical a-spacing-none"]/li')
            if not descs:
                descs = selector.xpath('//ul[@class="a-unordered-list a-vertical a-spacing-mini"]/li')
            for desc in descs:
                if desc.xpath('span/span'):
                    continue
                else:
                    text = desc.xpath('span/text()')[0].replace('\t', '').replace('\n', '').strip()
                    feature.append(text)
        except:
            pass
        try:
            soup = self.html_soup
            selector = etree.HTML(str(soup.select('#productDescription')[0]))
            productDescription = selector.xpath('//div[@id="productDescription"]//p/text()')[0]
            if len(productDescription) > 0:
                description = productDescription.strip()
        except:
            description = ''
        desc_dict['feature'] = feature
        desc_dict['description'] = description
        return desc_dict

    @property
    def alpus_page(self):
        soup = self.html_soup
        try:
            data = str(soup.select('#aplus')[0]).strip().replace('data-src', 'src')
            return data
        except:
            try:
                data = str(soup.select('.aplus')[0]).strip().replace('data-src', 'src')
                return data
            except:
                return

    @property
    def other_info(self):
        selector = self.html_selector
        aplus_video_choice = {'video': False, 'choice': '', 'aplus': False, 'coupon': False, 'sellerID': None,
                              'sellerNum': 1, 'first_list_date': '', 'bestseller': 0, 'stock_flag': 0, 'quantity': -1}
        try:
            stock_num = re.findall('stockOnHand":(\d+)', self.html)[0]
            aplus_video_choice['quantity'] = int(stock_num)
        except:
            pass
        try:
            regex = r'<ul class="(a-unordered-list a-nostyle a-button-list[\w -]+)">'
            cless = re.findall(regex, self.html)[0]
            video_page = selector.xpath('//ul[@class="%s"]/li' % cless)
            for each in video_page:
                if 'video' in each.xpath('@class')[0] and 'aok-hidden' not in each.xpath('@class')[0]:
                    aplus_video_choice["video"] = True
                elif each.xpath('span//img/@src')[0].split('.')[-1] == 'png':
                    aplus_video_choice["video"] = True
        except:
            pass
        try:
            aplus_video_choice["choice"] = selector.xpath('//span[@class="ac-for-text"]//a/text()')[0]
        except:
            pass
        try:
            if len(str(self.html_soup.select('#aplus')[0]).strip()) > 100:
                aplus_video_choice["aplus"] = True
        except:
            try:
                if len(str(self.html_soup.select('.aplus')[0]).strip()) > 100:
                    aplus_video_choice["aplus"] = True
            except:
                aplus_video_choice["aplus"] = False
        try:
            aplus_video_choice['coupon'] = float(re.findall('(\d+)%', selector.xpath(
                '//div[@id="unclippedCoupon"]//span[@class="a-color-success"]/text()')[0])[0])
        except:
            pass
        try:
            sellerID = selector.xpath('//form[@id="addToCart"]/input[@id="merchantID"]/@value')
            aplus_video_choice['sellerID'] = sellerID[0]
        except:
            pass

        try:
            if selector.xpath('//div[@id="olp_feature_div"]/div/span/a/text()')[0]:
                aplus_video_choice['sellerNum'] = \
                    re.findall('(\d+)', selector.xpath('//div[@id="olp_feature_div"]/div/span/a/text()')[0])[0]
            elif selector.xpath(
                    '//div[@id="mbc"]/div[@class="a-box"]/div[@class="a-box-inner"]/h5/span[@class="a-size-small"]/a/text()')[
                0]:
                aplus_video_choice['sellerNum'] = re.findall('(\d+)', selector.xpath(
                    '//div[@id="mbc"]/div[@class="a-box"]/div[@class="a-box-inner"]/h5/span[@class="a-size-small"]/a/text()')[
                    0])[0]
            else:
                raise ValueError('')
        except:
            pass
        try:
            aplus_video_choice['bestseller'] = int(
                selector.xpath('//div[@id="zeitgeistBadge_feature_div"]//a/@href')[0].split('/ref')[0].split('/')[-1])
        except:
            pass

        return aplus_video_choice

    @property
    def viewed_bought_other_asins(self):
        buyanother_after_view_this = []
        selector = self.html_selector
        c_b_a_v_item = selector.xpath('//ul[@class="a-unordered-list a-nostyle a-vertical p13n-sc-list-cells"]/li')
        for each in c_b_a_v_item:
            buyanother_after_view_this.append(
                str(json.loads(each.xpath('span/div/@data-p13n-asin-metadata')[0])["asin"]))
        return buyanother_after_view_this

    @property
    def get_parentasin_var(self):
        var = {"parent": "", "var": ""}
        selector = self.html_selector
        var_list = selector.xpath('//div[@id="variation_color_name"]/ul/li/@data-dp-url')
        if len(var_list) == 0:
            var_list = selector.xpath('//div[@id="variation_style_name"]/ul/li/@data-dp-url')
        if len(var_list) > 0:
            for each in var_list:
                if each != '':
                    try:
                        var['parent'] = each.split('twister_')[-1].split('?')[0].replace('/dp', '')
                        var['var'] = each.split('dp/')[-1].split('/')[0]
                        break
                    except:
                        pass

        return var

    @property
    def variant_list(self):
        style_info = None
        variant_info = None
        variant_info = {}
        selector = self.html_selector
        parentasin = ''
        vari_num = None
        try:
            js_str = selector.xpath('//div[@id="twisterJsInitializer_feature_div"]/script/text()')[0]
            parentasin = re.findall('parentAsin" : "(\w+)",', js_str)[0].replace('/dp', '')
            style_str = re.findall('("variationValues.+"\]\})', js_str)
            if len(style_str):
                json_str = "{" + style_str[0] + "}"
                style_info = json.loads(json_str)['variationValues']
            variant_str = re.findall('("asinVariationValues".+"\}\})', js_str)
            if variant_str:
                json_str = "{" + variant_str[0] + "}"
                variant_info = json.loads(json_str)['asinVariationValues']
            if style_info is not None and variant_info is not None:
                for each_asin in variant_info:
                    for each_style in variant_info[each_asin]:
                        if each_style != 'ASIN':
                            index = int(variant_info[each_asin][each_style])
                            style = style_info[each_style][index]
                            variant_info[each_asin][each_style] = style
                    del variant_info[each_asin]['ASIN']
            vari_num_str = re.findall('"num_total_variations" : (\d+)', js_str)
            if isinstance(vari_num_str, list):
                vari_num = int(vari_num_str[0])
        except:
            pass
        return variant_info, parentasin, vari_num

    @property
    def img_list(self):
        img_sort = ['hiRes', 'thumb', "large"]
        img_urls = []
        if self.img_obj:
            for x in self.img_obj['initial']:
                key = 'hiRes'
                for k in img_sort:
                    if x[k]:
                        key = k
                        break
                img_tmp = x[key].split('/')[-1]
                img_l = img_tmp.split('.')
                img = img_l[0]
                img_urls.append(img)
        return img_urls

    @property
    def rank_list(self):
        data = {}
        l = []
        if self.category != '':
            l.append({
                "catId": self.catId,
                "name": self.category,
                "rank": self.rank
            })
        soup = self.html_soup
        selector = self.html_selector
        try:
            selector = etree.HTML(str(soup.select('#productDetails_detailBullets_sections1')[0]))
            trs = selector.xpath(".//*[@id='productDetails_detailBullets_sections1']/tr")
            print('---', len(trs))
            for tr in trs:
                text = tr.xpath("./th[1]/text()")[0].strip()
                if "Rank" in text or "Bestseller-Rang" in text or "d'Amazon" in text or 'Amazon' in text:
                    subitem = tr.xpath("./td[1]/span[1]/span")
                    for span in subitem:
                        rank = ''.join(re.findall('(\d+)', span.xpath("./text()")[0]))
                        if len(span.xpath('a')) == 1:
                            span_text = span.xpath('a/text()')[0]
                            catId = span.xpath("./a/@href")[0].strip().split('/ref')[0].split('/')[-1]
                            print(span_text, '----', catId)
                            if "100" not in span_text:
                                category = span_text
                            else:
                                text = span_text.split(')')[0]
                                print(text)
                                if self.countryCode == 'jp':
                                    arr = text.split(' - ')
                                    if len(arr) == 1:
                                        arr = text.split(' in ')
                                elif self.countryCode == 'de':
                                    arr = text.split(' in ')
                                elif self.countryCode in ['fr', 'mx']:
                                    arr = text.split(' en ')
                                elif self.countryCode == 'uk':
                                    arr = text.split(' in ')
                                elif self.countryCode == 'it':
                                    arr = text.split(' in ')
                                    if len(arr) == 1:
                                        arr = text.split(' categoria ')
                                elif self.countryCode == 'es':
                                    arr = text.split(' en ')
                                elif self.countryCode == 'br':
                                    arr = text.split(' em ')
                                else:
                                    arr = text.split('in ')
                                category = str(arr[1].strip())
                                if category not in self.categoryIndexArr[self.countryCode].keys() or category in [
                                    each['name'] for each in l]:
                                    continue
                            l.append({
                                "catId": catId,
                                "name": category,
                                "rank": rank
                            })
                        elif len(span.xpath('a')) > 1:
                            category = span.xpath("./a[last()]/text()")[0]
                            catId = span.xpath("./a[last()]/@href")[0].strip().split('/ref')[0].split('/')[-1]
                            l.append({
                                "catId": catId,
                                "name": category,
                                "rank": rank
                            })
                            for each in span.xpath('a')[:-1]:
                                rank = 0
                                category = each.xpath('text()')[0]
                                catId = each.xpath('@href')[0].split('/ref')[0].split('/')[-1]
                                if catId not in [str(each['catId']) for each in l]:
                                    l.append({
                                        "catId": self.categoryIndexArr[self.countryCode][category],
                                        "name": category,
                                        "rank": rank
                                    })
        except:
            try:
                if self.countryCode == 'jp':
                    try:
                        ul = selector.xpath('//tr[@id="SalesRank"]/td[@class="value"]/text()')
                        rank = re.findall('#(.*?) ', ul[0])[0].replace(',', '')
                        category = re.findall('in (.*?) \(', ul[0])[0]
                        catId = self.categoryIndexArr[self.countryCode][category]
                        l.append({
                            "catId": catId,
                            "name": category,
                            "rank": rank
                        })
                    except:
                        pass
                ul = selector.xpath('//ul[@class="zg_hrsr"]/li')
                if len(ul) < 1:
                    print('=====3')
                    tr = selector.xpath('//div[@id="detailBulletsWrapper_feature_div"]/ul[1]/li/span')
                    if len(tr) > 0:
                        tr = tr[0]
                        subitem = tr.xpath('./ul/li/span')
                        if len(subitem) > 0:
                            span = subitem[0]
                            if len(span.xpath('./text()')) > 0:
                                rank_str = span.xpath('./text()')[0]
                                rank = ''.join(re.findall('(\d+)', rank_str))
                            if len(span.xpath('a')) == 1:
                                span_text = span.xpath('a/text()')[0]
                                catId = span.xpath("./a/@href")[0].strip().split('/ref')[0].split('/')[-1]
                                print(span_text, '----', catId)
                                if "100" not in span_text:
                                    category = span_text
                                else:
                                    text = span_text.split(')')[0]
                                    print(text)
                                    if self.countryCode == 'jp':
                                        arr = text.split(' - ')
                                        if len(arr) == 1:
                                            arr = text.split(' in ')
                                    elif self.countryCode == 'de':
                                        arr = text.split(' in ')
                                    elif self.countryCode in ['fr', 'mx']:
                                        arr = text.split(' en ')
                                    elif self.countryCode == 'uk':
                                        arr = text.split(' in ')
                                    elif self.countryCode == 'it':
                                        arr = text.split(' in ')
                                        if len(arr) == 1:
                                            arr = text.split(' categoria ')
                                    elif self.countryCode == 'es':
                                        arr = text.split(' en ')
                                    elif self.countryCode == 'br':
                                        arr = text.split(' em ')
                                    else:
                                        arr = text.split('in ')
                                    category = str(arr[1].strip())
                                    if category not in self.categoryIndexArr[self.countryCode].keys() or category in [
                                        each['name'] for each in l]:
                                        pass
                                        # continue
                                l.append({
                                    "catId": catId,
                                    "name": category,
                                    "rank": rank
                                })
                            elif len(span.xpath('a')) > 1:
                                category = span.xpath("./a[last()]/text()")[0]
                                catId = span.xpath("./a[last()]/@href")[0].strip().split('/ref')[0].split('/')[-1]
                                l.append({
                                    "catId": catId,
                                    "name": category,
                                    "rank": rank
                                })
                                for each in span.xpath('a')[:-1]:
                                    rank = 0
                                    category = each.xpath('text()')[0]
                                    catId = each.xpath('@href')[0].split('/ref')[0].split('/')[-1]
                                    if catId not in [str(each['catId']) for each in l]:
                                        l.append({
                                            "catId": self.categoryIndexArr[self.countryCode][category],
                                            "name": category,
                                            "rank": rank
                                        })

                for li in ul:
                    rank = ''.join(re.findall('(\d+)', li.xpath('span[1]/text()')[0]))
                    category = li.xpath('span[2]//a/text()')[0].strip()
                    catId = li.xpath('span[2]//a/@href')[0].split('/ref')[0].split('/')[-1]
                    l.append({
                        "catId": catId,
                        "name": category,
                        "rank": rank
                    })
                    lv = 1
                    for each in li.xpath('span[2]/a'):
                        rank = '0'
                        category = each.xpath('text()')[0]
                        catId = each.xpath('@href')[0].split('/ref')[0].split('/')[-1]
                        try:
                            if lv == 1:
                                if self.categoryIndexArr[self.countryCode][category] in [each['catId'] for each in l]:
                                    lv += 1
                                else:
                                    l.append({
                                        "catId": self.categoryIndexArr[self.countryCode][category],
                                        "name": category,
                                        "rank": rank
                                    })
                                    lv += 1
                            elif lv > 1 and catId not in [str(each['catId']) for each in l]:
                                l.append({
                                    "catId": catId,
                                    "name": category,
                                    "rank": rank
                                })
                            lv += 1
                        except:
                            continue
            except Exception as e:
                print('=====3')
                tr = selector.xpath('//div[@id="detailBulletsWrapper_feature_div"]/ul[1]/li/span/ul/span')
                if len(tr) > 0:
                    tr = tr[0]
                    subitem = tr.xpath('/ul/li/span')
                    if len(subitem) > 0:
                        span = subitem[0]
                        if span.xpath('.text()') > 0:
                            rank_str = span.xpath('./text()')[0]
                            rank = ''.join(re.findall('(\d+)', rank_str))
                        if len(span.xpath('a')) == 1:
                            span_text = span.xpath('a/text()')[0]
                            catId = span.xpath("./a/@href")[0].strip().split('/ref')[0].split('/')[-1]
                            print(span_text, '----', catId)
                            if "100" not in span_text:
                                category = span_text
                            else:
                                text = span_text.split(')')[0]
                                print(text)
                                if self.countryCode == 'jp':
                                    arr = text.split(' - ')
                                    if len(arr) == 1:
                                        arr = text.split(' in ')
                                elif self.countryCode == 'de':
                                    arr = text.split(' in ')
                                elif self.countryCode in ['fr', 'mx']:
                                    arr = text.split(' en ')
                                elif self.countryCode == 'uk':
                                    arr = text.split(' in ')
                                elif self.countryCode == 'it':
                                    arr = text.split(' in ')
                                    if len(arr) == 1:
                                        arr = text.split(' categoria ')
                                elif self.countryCode == 'es':
                                    arr = text.split(' en ')
                                elif self.countryCode == 'br':
                                    arr = text.split(' em ')
                                else:
                                    arr = text.split('in ')
                                category = str(arr[1].strip())
                                if category not in self.categoryIndexArr[self.countryCode].keys() or category in [
                                    each['name'] for each in l]:
                                    pass
                                    # continue
                            l.append({
                                "catId": catId,
                                "name": category,
                                "rank": rank
                            })
                        elif len(span.xpath('a')) > 1:
                            category = span.xpath("./a[last()]/text()")[0]
                            catId = span.xpath("./a[last()]/@href")[0].strip().split('/ref')[0].split('/')[-1]
                            l.append({
                                "catId": catId,
                                "name": category,
                                "rank": rank
                            })
                            for each in span.xpath('a')[:-1]:
                                rank = 0
                                category = each.xpath('text()')[0]
                                catId = each.xpath('@href')[0].split('/ref')[0].split('/')[-1]
                                if catId not in [str(each['catId']) for each in l]:
                                    l.append({
                                        "catId": self.categoryIndexArr[self.countryCode][category],
                                        "name": category,
                                        "rank": rank
                                    })
                else:
                    data["ranks"] = None
                    return data
        data["ranks"] = l
        return data

    @property
    def aplus_info(self):
        selector = self.html_selector
        aplus_info = selector.xpath('string(//div[@class="aplus-v2 desktop celwidget"])')
        print(aplus_info)

    @property
    def product_info(self):
        selector = self.html_selector
        product_info_list = selector.xpath('//div[@id="prodDetails"]//table//tr')
        product_info = {}
        if len(product_info_list) != 0:
            for product_data in product_info_list:
                info = product_data.xpath('./th/text()')
                if self.countryCode in ['uk', "de", "jp", "fr", "it", 'es']:
                    info = product_data.xpath('./td/text()')
                info = info[0].replace('\n', '').replace('\r', '').replace('\t', '')
                if info not in ["ASIN", "Customer Reviews", "Best Sellers Rank", 'Amazon Best Sellers Rank']:
                    if self.countryCode in ["uk", "de", "jp", "fr"]:
                        data = product_data.xpath('./td/text()')[-1].replace('\n', '').replace('\r', '').replace('\t',
                                                                                                                 '')
                    else:
                        data = product_data.xpath('./td/text()')[0].replace('\n', '').replace('\r', '').replace('\t',
                                                                                                                '')
                    product_info[info] = data
        else:
            product_info_list = selector.xpath('//div[@id="detail-bullets"]/table//ul/li')
            for product_data in product_info_list:
                try:
                    info = product_data.xpath('./b/text()')[0].replace('\n', '').replace('\r', '').replace('\t',
                                                                                                           '').strip().replace(
                        ':', '')
                    if info not in ["ASIN", "Customer Reviews", "Best Sellers Rank", 'Amazon Best Sellers Rank']:
                        data = product_data.xpath('./text()')[0].replace('\n', '').replace('\r', '').replace('\t',
                                                                                                             '').strip()
                        if info == 'Date First Available':
                            data = self.date_first_available(data, self.countryCode)
                        product_info[info] = data
                except:
                    pass
        return product_info

    @property
    def compare_info(self):
        selector = self.html_selector
        asin_list = selector.xpath('//div[@id="HLCXComparisonWidget_feature_div"]/table/tr/th/@data-asin')
        # info_list = selector.xpath('//div[@id="HLCXComparisonWidget_feature_div"]/table/tbody/tr/th/span/text()')
        # product_list = selector.xpath('//div[@id="HLCXComparisonWidget_feature_div"]/table/tbody/tr')
        product_list = selector.xpath('//div[@id="HLCXComparisonWidget_feature_div"]/table/tr')
        result = {}
        for asin in asin_list:
            endchirld = {}
            result[asin] = endchirld
        for product_data in product_list:
            info_list = product_data.xpath('./th/span/text()')
            data_list = product_data.xpath('./td/a/text()')
            # print('-----', info_list)
            # print('====1===',data_list)
            if len(data_list) < len(asin_list):
                data_list += product_data.xpath('./td/span/text()')
                data_list += product_data.xpath('./td/span/span/text()')
            i = 0
            # print('=====', data_list)
            if len(info_list) != 0 and len(data_list) != 0:
                if info_list[0] == 'Customer Rating':
                    pass
                else:
                    for asin_data in result.keys():
                        result[asin_data][info_list[0]] = data_list[i].replace('\n', '').strip()
                        i += 1
        return result

    @property
    def product_descript(self):
        result = {}
        result['product_info'] = {}
        result['product_dict'] = {}
        result['other_info'] = []
        selector = self.html_selector
        info_list = selector.xpath('//div[@id="aplus"]//table/tr/td')
        name_list = selector.xpath('//div[@id="aplus"]//table//th/a/text()')
        asinstr_list = selector.xpath('//div[@id="aplus"]//table//th/a/text()/../@href')
        other_info_list = selector.xpath('//div[@id="aplus"]//div/div/p/text()')
        for other_info in other_info_list:
            if other_info.strip() != '':
                result['other_info'].append(other_info.strip())
        new_other_info_list = selector.xpath('//div[@id="productDescription_feature_div"]//p/text()')
        for other_info in new_other_info_list:
            if other_info.strip() != '':
                result['other_info'].append(other_info.strip())
        new_other_info_list = selector.xpath('//div[@id="important-information"]/div//p/text()')
        for other_info in new_other_info_list:
            if other_info.strip() != '':
                result['other_info'].append(other_info.strip())
        # result['other_info'] = other_info
        print(info_list)
        if info_list != []:
            for product_info in info_list:
                try:
                    info = product_info.xpath('./div/h4/text()')
                    if len(info) > 0:
                        info = info[0].strip()
                    else:
                        info = info_list.index(product_info)
                    data = product_info.xpath('./div/p/text()')
                    if len(data) > 0:
                        data = data[0].strip()
                    else:
                        data = info_list.index(product_info)
                    result['product_info'][info] = data
                except Exception as e:
                    print(e)
        new_name_list = []
        for name in name_list:
            if name != '\n':
                neme = name.replace('\n', '')
                new_name_list.append(neme)
        if len(name_list) != 0 and len(asinstr_list) != 0:
            asin_list = []
            index = int(len(asinstr_list) / 2)
            for asin_data in asinstr_list[:index]:
                asin = asin_data.split('/')[2]
                asin_list.append(asin)
            # for asin in asin_list
            for data in zip(asin_list, new_name_list):
                # result['product_list'].append({data[0]: {}})
                result['product_dict'][data[0]] = {'name': data[-1]}
            info_list = selector.xpath('//div[@id="aplus"]//table/tbody/tr')
            for product_data in info_list:
                try:
                    info = product_data.xpath('./th/span/text()')[0].strip()
                    data_list = product_data.xpath('./td/span/text()')  # [0].strip()
                    for data in zip(result['product_dict'].keys(), data_list):
                        result['product_dict'][data[0]][info] = data[-1].strip()
                except:
                    pass
        return result

    # @property


def date_first_available(self, review_time, countrycode):
    try:
        us_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                    "November", "December"]
        # selector = self.html_selector
        # review_time = selector.xpath("//*[@id='productDetails_detailBullets_sections1']//tr/td/text()")[-1].strip()
        # countrycode = self.countryCode
        if review_time != '':
            if countrycode in ['us', 'jp', 'ca', 'fr']:
                review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%B %d, %Y"))
            elif countrycode == 'fr':
                fr_month = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                            "septembre", "octobre", "novembre", "décembre"]
                review_time = review_time.split('le ')[-1]  # .decode('utf-8').encode("latin-1")
                for each in range(12):
                    if self.fr_month[each] in review_time:
                        review_time = review_time.replace(self.fr_month[each], self.us_month[each])
                        break
                review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
            elif countrycode == 'de':
                de_month = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September",
                            "Oktober", "November", "Dezember"]
                # review_time = review_time.split('vom ')[-1]  # .decode('utf-8').encode("latin-1")
                print(review_time)
                for each in range(12):
                    if de_month[each] in review_time:
                        review_time = review_time.replace(de_month[each], us_month[each])
                        break

                review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d. %B %Y"))
            elif countrycode == 'es':
                self.es_month = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                 "septiembre", "octubre", "noviembre", "diciembre"]
                review_time = review_time.split('el ')[-1].replace('de ', '')  # .decode('utf-8').encode("latin-1")
                for each in range(12):
                    if self.es_month[each] in review_time:
                        review_time = review_time.replace(self.es_month[each], self.us_month[each])
                        break
                review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
            elif countrycode == 'it':
                it_month = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
                            "settembre", "ottobre", "novembre", "dicembre"]
                review_time = review_time.split('il ')[-1]  # .decode('utf-8').encode("latin-1")
                for each in range(12):
                    if self.it_month[each] in review_time:
                        review_time = review_time.replace(self.it_month[each], self.us_month[each])
                        break
                review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
            # elif countrycode == 'jp':
            #     review_time = '-'.join(re.findall('\d+', review_time))
            #     review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%Y-%m-%d"))
            elif countrycode == 'uk' or countrycode == 'au' or countrycode == 'jp':
                # review_time = review_time.split('on ')[-1]
                review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%B %d, %Y"))
            # elif countrycode == 'uk' or countrycode == 'au':
            #     review_time = review_time.split('on ')[-1]
            #     review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
        return review_time
    except:
        return ''


if __name__ == "__main__":
    import pprint
    import requests
    import sys

    s = requests.session()
    asin = sys.argv[1]
    country = sys.argv[2]
    temp_site = {'us': 'com', 'jp': 'co.jp', 'de': 'de', 'fr': 'fr', 'es': 'es', 'it': 'it', 'uk': 'co.uk',
                 'au': 'com.au', 'ca': 'ca', "ae": "ae", "mx": "com.mx", "tr": "com.tr"}
    url = 'https://www.amazon.%s/dp/%s?&language=en_US' % (temp_site[country], asin)
    print(url)
    '''cat = s.get(url=url)
    response = etree.HTML(cat.text)
    cat1 = ['industrial','wireless','toys-and-games','sporting-goods','photo',
    'pet-supplies','pc','office-products','musical-instruments',
    'lawn-garden','kitchen','appliances','hpc','home-garden','hi',
    'arts-crafts','fashion','electronics','automotive','baby-products',
    'beauty','grocery']
    asins = {}'''
    # 蘑菇代理的隧道订单
    appKey = "ZFFxMVUzUTZRNURDVnRKNzoxbWpDVVJiMjl0eXNIQlZv"

    # 蘑菇隧道代理服务器地址
    ip_port = 'transfer.mogumiao.com:9001'
    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
    headers = {
        "cookie": 'session-id=257-2400340-3507963; ubid-acbuk=260-3151265-2626524; lc-acbuk=en_GB; x-acbuk="4GtIjYqwRxe0RdWUZ3BWYOrboncKzfQ280ZWuIUrD1qIAHfXiR7jjcQ5az?5Dqri"; at-acbuk=Atza|IwEBIG84asQwzChoCjYkmjrGTivPAprJP_vbn5B8maV0lrFY1K288JK8PqZkR80jLiih8gsP4V2NE-8bLjQL-2X_fp0w7o9OMn9UIAKyelpl5Dvzd3MIYqCcbgOeixzFDSlLsHwPwS29AFdQLr8dAnZ1E17SpTTrqHFfsfxDA7p7wmHob6oxaIUbN-fv5iwhh72LimT8Ta1adJyLBzOiymRg0LKS1IxZbKzriu5MP6t_ZyrgHEo0ix7OLXij8Qxuqk4BQfE; sess-at-acbuk="wDMRYe3M4YpvVaDG4uE8ypTofhPwwiWbuLBX5GinhdQ="; sst-acbuk=Sst1|PQEFjTFC1rbTL9rpewsRfn5wCbYwRazRZe9Nk9hr9_p5ytzyUKydUbxaxQnX7e8v-jQPSx3ko-vEw-smO4ufmi91KXWfoUvBfHr_hHbb25eRJ5aEoT-xUoNX2xkTGNqxCy_n0i0zBqpn-j0TqGhtgSPUPVCXMG8Y44p4sXKSGaarpIiSb4h3RrxKPEHpwmSF-m1N5qcH0HfoWzrDqV64WTyMPCWoS7i4FD1VZdphJwkUGFMXu6uV796SIGtzYeEB2Qpo-EG-rb_ke77-Jf5ycBLWoCJNRkIAhQLj3cMXB6N_TU4; i18n-prefs=GBP; session-token=1zEsPCQ6GjleA9lL45NonmpmdAzSW0aTPBDPWDEZzrxtd9mSEmTALLmFH9mGBqlIXJ980BRqD4jcinn1KnRhuXtRUdrOP4enwbBNk5uHLgdHW3iNpnCs7O4kbX5I+PiB9stSk+SeT5gZKjLI37djZ9oWIApFJ1YkC3eFamXisbY/SszqJESPY9wJNOVLxKHT9cnAg0pO49VqM6YWuGoupIdUsjrBmQreH9QJLBt7otVmnS6gSvqkTqqXHJ6BCjSpb69SvgRoE9aw+nVi7OlY4c1SuJqJTTEP; session-id-time=2082758401l',
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,und;q=0.8,en;q=0.7,ja;q=0.6",
        "cache-control": "max-age=0",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        # "Proxy-Authorization": 'Basic '+ appKey,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }


    def IsChineseCharInside(sentence):
        for uchar in sentence:
            if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
                return True
        return False


    cookies = {"lc-main": "en_US", "sp-cdn": '"L5Z9:US"'}
    r = s.get(url=url, headers=headers, verify=False, allow_redirects=False)  # proxies=proxy,
    print(r.status_code, "===", len(r.text))
    if r.status_code == 200 and len(r.content) > 10000:
        with open('test.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
    # with open('test.html','r', encoding='utf-8') as f:
    #     r = f.read()
    product = productDetailParse()
    product.initial_data = r.text
    product.country = country
    pprint.pprint(product.variant_list)
    print(product.get_parentasin_var)
    product.best_seller_rank()
    product.seller_info()
    product.revews_rating()
    # print("rank",product.rank,product.category,product.catId)
    print('seller', product.seller_type)
    print('seller_num', product.seller_num)
    print('price', product.price)
    # print('reivews',product.reviews,product.rating,product.rating_ratio)
    # print('title',IsChineseCharInside(product.title))
    # print('title',product.title)
    # print('stock_status',product.availability)
    # print('QA',product.QA_num)
    # # print('mentioned words',product.reviewMentionedWords)
    # print('brand',product.brand)
    # print('img',product.img_url)
    # print('imgs',product.img_list)
    # print('------------------')
    # # print('aplus',product.alpus_page)
    # print('------------------')
    # print('variant',product.variant_list)
    print('rank_list', product.rank_list)
    # print('merchantName',product.merchantName)
    # print('merchantUrl',product.merchantUrl)
    # print 'frequently_bought_asins',product.frequently_bought_asins
    # print 'also_viewed_asins',product.also_viewed_asins
    # print 'also_bought_asins',product.also_bought_asins
    # print 'sponsored_asins_1',product.sponsored_asins_1
    # print 'sponsored_asins_2',product.sponsored_asins_1
    # print 'similar_asins',product.similar_asins
    # print('desc',product.description)
    # print('=====')
    print("product_descript", product.product_descript)
    # print("date_first_available", product.date_first_available())
    print('========')
    print('product_info', product.product_info)
    # print('=====')
    print('compare_list', product.compare_info)
    print('other', product.other_info)
    # print('viewed_bought_other_asins',product.viewed_bought_other_asins)
