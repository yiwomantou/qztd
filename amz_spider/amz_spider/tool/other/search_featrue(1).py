# coding=utf-8
# 用于数据汇总，提取出固定格式的数据
# 分两种情况：1、市场调研时需要根据关键词提取数据
#           2、产品调研时需要根据asin提取数据
import json
import re
import pandas as pd
import pymysql
import pymongo
from DBUtils.PooledDB import PooledDB

class Mysql_server:
    def __init__(self):
        self.host = '172.80.28.146'
        self.user = 'root'
        self.passwd = 'qztdmysql'
        self.db = 'qztd'
        self.port = 3306
        self.charset = 'utf8mb4'
        self.pool = PooledDB(pymysql, 10, host=self.host, user=self.user, passwd=self.passwd, db=self.db,
                             port=self.port, charset=self.charset)  # 5为连接池里的最少连接数

        self.conn = self.pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了

    def get_cursor(self):
        try:
            self.conn.ping()
        except:
            try:
                self.conn = self.pool.connection()
            except:
                self.pool = PooledDB(pymysql, 10, host=self.host, user=self.user, passwd=self.passwd, db=self.db,
                                     port=self.port, charset=self.charset)  # 5为连接池里的最少连接数
                self.conn = self.pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
                self.conn = self.pool.connection()
        cursor = self.conn.cursor()
        return cursor

    def close(self):
        self.conn.close()

class MongoDBserver():
    def __init__(self):
        # self.client = pymongo.MongoClient('172.80.28.146', 27020, username='root', password='qztdmongodb', maxPoolSize=100)
        # self.db = self.client.amazon
        # self.collection = self.db.detail_info
        host = '172.80.28.146'
        self.client = pymongo.MongoClient(host, 27017)
        db = self.client.amazon
        db.authenticate("root", "qztdmongodb", mechanism='SCRAM-SHA-1')  # 让admin数据库去认证密码登录，好>    吧，既然成功>了，
        self.collection = db.detail_info  # myset集合，同上解释

    def get_collection(self):
        return self.collection

    def close(self):
        self.client.close()

class SearchFeature():
    def __init__(self):
        # 建立数据库连接
        self.mongodb = MongoDBserver()
        self.collection = self.mongodb.get_collection()
        self.mysql = Mysql_server()
        self.cursor =self.mysql.get_cursor()

    def get_asin(self):
        # 根据条件搜索出相应的asin
        self.cursor.execute('select asin from product where product="" and state=4 and country="us"')
        asin_list = self.cursor.fetchall()
        result_list = []
        i = 0
        data_list = []
        for asin in asin_list:
            result = self.collection.find_one({"asin": asin[0], "country":"us"})
            if result != None:
                data_list.append(result)
                i +=1
                data = str(result)
                word = "minute"
                result_test = re.findall("(([^\s]+ ){0,5}(water).*? ?(,|\.))",data)
                if result_test != []:
                    data_dict = {"asin": result['asin'], "data": result_test[0][0]}
                    result_list.append(data_dict)
        self.mongodb.close()
        self.mysql.close()
        for i in result_list:
            with open('test.txt', 'a', encoding='utf-8') as f:
                f.write(str(i))
                f.write('\n')
        df = pd.DataFrame(result_list)
        df.to_csv('test.xlsx')
        # df = pd.DataFrame(result_list)
        # df.to_csv('test.xlsx')

class Getdata():
    def __init__(self):
        # 建立数据库连接
        self.mongodb = MongoDBserver()
        self.collection = self.mongodb.get_collection()
        self.mysql = Mysql_server()
        self.cursor =self.mysql.get_cursor()
        self.categoryIndexArr = {
            "us":{
                "Home & Kitchen":1055398,"Office Products":1064954,"Musical Instruments":11091801,
                "Amazon Launchpad":12034488011,"Kindle Store":133140011,"Kitchen & Dining":13900821,
                "Automotive":15684181,"Industrial & Scientific":16310091,"Grocery & Gourmet Food":16310101,
                "Digital Music":163856011,"Toys & Games":165793011,"Baby":165796011,
                "Electronics":172282,"Gift Cards":2238192011,"Tools & Home Improvement":228013,
                "Software":229534,"Cell Phones & Accessories":2335752011,"Apps & Games":2350149011,
                "Arts, Crafts & Sewing":2617941011,"Appliances":2619525011,"Pet Supplies":2619533011,
                "Movies & TV":2625373011,"Books":283155,"Patio, Lawn & Garden":2972638011,
                "Sports Collectibles":3250697011,"Sports & Outdoors":3375251,"Health & Household":3760901,
                "Beauty & Personal Care":3760911,"Video Games":468642,"Camera & Photo":502394,
                "Entertainment Collectibles":5088769011,"CDs & Vinyl":5174,"Computers & Accessories":541966,
                "Magazine Subscriptions":599858,"Clothing, Shoes & Jewelry":7141123011,"Collectible Coins":9003130011
            },
            "jp":{
                "Home & Kitchen":1055398,"Office Products":1064954,"Musical Instruments":11091801,
                "Amazon Launchpad":12034488011,"Kindle Store":133140011,"Kitchen & Dining":13900821,
                "Automotive":15684181,"Industrial & Scientific":16310091,"Grocery & Gourmet Food":16310101,
                "Digital Music":163856011,"Toys & Games":165793011,"Baby":165796011,
                "Electronics":172282,"Gift Cards":2238192011,"Tools & Home Improvement":228013,
                "Software":229534,"Cell Phones & Accessories":2335752011,"Apps & Games":2350149011,
                "Arts, Crafts & Sewing":2617941011,"Appliances":2619525011,"Pet Supplies":2619533011,
                "Movies & TV":2625373011,"Books":283155,"Patio, Lawn & Garden":2972638011,
                "Sports Collectibles":3250697011,"Sports & Outdoors":3375251,"Health & Household":3760901,
                "Beauty & Personal Care":3760911,"Video Games":468642,"Camera & Photo":502394,
                "Entertainment Collectibles":5088769011,"CDs & Vinyl":5174,"Computers & Accessories":541966,
                "Magazine Subscriptions":599858,"Clothing, Shoes & Jewelry":7141123011,"Collectible Coins":9003130011
            },
            "xx":{
                'ビューティー': 52374051, 'jp-stores': 579684, 'DVD': 561958, 'ゲーム': 637394, '産業・研究開発用品': 3445393051,
                'Prime Video': 2351649051, 'スポーツ＆アウトドア': 14304371, '洋書': 52033011, '食品・飲料・お酒': 57239051,
                '車＆バイク': 2017304051,'シューズ＆バッグ': 2016926051, 'ジュエリー': 85895051, '腕時計': 324025011, 'ホビー': 2277721051,
                'DIY・工具・ガーデン': 2016929051,'ペット用品': 2127212051, 'ホーム＆キッチン': 3828871, '文房具・オフィス用品': 86731051,
                '楽器・音響機器': 2123629051, 'ドラッグストア': 160384011, 'デジタルミュージック': 2128134051,'家電＆カメラ': 3210981,
                '大型家電': 2277724051,'服＆ファッション小物': 352484011, 'おもちゃ': 13299531, 'PCソフト': 637392, 'ミュージック': 561956,
                'ベビー＆マタニティ': 344845011,'パソコン・周辺機器':2127209051,'Amazonデバイス・アクセサリ':4976279051,
                'Androidアプリ': 2381130051,'Kindleストア':2250738051,'ギフト券':2351652051,'ファッション':2229202051,'本':465392
            },
            "de":{
                'Haustier': 340852031, 'DVD & Blu-ray': 284266, 'Küche, Haushalt & Wohnen': 3167641,
                'Auto & Motorrad': 78191031, 'Lebensmittel & Getränke': 340846031,
                'Prime Video': 3010075031,'Amazon Launchpad': 9418395031,
                'Musik-CDs & Vinyl': 255882, 'Bürobedarf & Schreibwaren': 192416031,
                'Beleuchtung': 213083031,'Kamera & Foto':571860,
                'Beauty': 84230031, 'Elektronik & Foto': 562066, 'Spielzeug': 12950651,
                'Schuhe & Handtaschen': 355006011, 'Baby': 355007011,
                'Elektro-Großgeräte': 908823031, 'Bekleidung': 77028031,
                'Gewerbe, Industrie & Wissenschaft': 5866098031,'Zeitschriften': 1161658,
                'Sport & Freizeit': 16435051, 'Musikinstrumente & DJ-Equipment': 340849031,
                'Bücher': 186606,'Amazon-Geräte & Zubehör': 12598632031,
                'Fremdsprachige Bücher': 52044011, 'Games': 300992, 'Handmade Produkte': 9699311031,
                'Koffer, Rucksäcke & Taschen': 2454118031,'Geschenkgutscheine': 1571256031,
                'Musik-Downloads': 77195031, 'Software': 301927, 'Sonstiges': 72921031,
                'Computer & Zubehör': 340843031,'Apps & Spiele': 1661648031,
                'Drogerie & Körperpflege': 64187031, 'Uhren': 193707031, 'Schmuck': 327472011,
                'Garten': 10925031, 'Baumarkt': 80084031,'Kindle-Shop': 530484031
            },
            "uk":{
                'Home & Garden Store': 3146281, 'DVD & Blu-ray': 283920, 'Shoes & Bags': 355005011,
                'Stationery & Office Supplies': 192413031, 'Prime Video': 3010085031,
                'CDs & Vinyl': 229816,'Garden & Outdoors': 11052671,'Handmade Products': 9699254031,
                'Large Appliances': 908798031, 'Health & Personal Care': 65801031,
                'Musical Instruments & DJ': 340837031, 'Beauty': 117332031, 'Automotive': 248877031,
                'Pet Supplies': 340840031,'Apps & Games': 1661657031,'Gift Cards': 1571304031,
                'Lighting': 213077031, 'Computers & Accessories': 340831031,
                'Sports & Outdoors': 318949011, 'Everything Else': 72911031, 'Grocery': 340834031,
                'Luggage': 2454166031,'Amazon Devices & Accessories': 12598575031,
                'Business, Industry & Science': 5866054031, 'Digital Music': 77197031,
                'DIY & Tools': 79903031, 'Software': 300435, 'Jewellery': 193716031,
                'Electronics & Photo': 560798, 'Baby Products': 59624031,'Kindle Store': 341677031,
                'Watches': 328228011, 'Toys & Games': 468292, 'Books': 266239, 'Clothing': 83450031,
                'PC & Video Games': 300703,"Amazon Launchpad":7212961031,"Home & Kitchen":11052681
            },
            "fr":{
                'Bricolage': 590748031, 'Animalerie': 1571268031, 'Hygiène et Santé': 197861031,
                'Livres': 301061, 'DVD & Blu-ray': 405322,'Boutique chèques-cadeaux': 2524127031,
                'Vêtements': 340855031, 'Fournitures de bureau': 192419031, 'Informatique': 340858031,
                'Téléchargement de Musique': 77196031, 'Chaussures et Sacs': 215934031,
                'Montres': 60649031,'Appareils Amazon et Accessoires': 12598689031,
                'Bébé & Puériculture': 206617031, 'Luminaires & Eclairage': 213080031,
                'High-Tech': 13921051,'Logiciels': 530488,'Amazon Launchpad': 10525448031,
                'Gros électroménager': 908826031, 'Jeux vidéo': 530490, 'Beauté et Parfum': 197858031,
                'Bijoux': 193710031, 'Epicerie': 3635788031, 'Auto et Moto': 1571265031,
                'Livres anglais et étrangers': 52042011, 'Instruments de musique et Sono': 340861031,
                'Jeux et Jouets': 322086011, 'Sports et Loisirs': 325614031, 'Autres': 72919031,
                'Commerce, Industrie et Science': 5866109031, 'Cuisine & Maison': 57004031,
                'CD & Vinyles': 301062,'Applis et Jeux': 1661654031,'Boutique Kindle': 672108031,
                'Bagages': 2454145031, 'Jardin': 3557027031, 'Produits Handmade': 9699368031
            },
            "it":{
                'Abbigliamento':2844433031,'Alimentari e cura della casa':6198092031,'Altro':425919031,'Auto e Moto':1571280031,
                'Bellezza':6198082031,'Cancelleria e prodotti per ufficio':3606310031,'Casa e cucina':524015031,'CD e Vinili':412600031,
                'Commercio, Industria e Scienza':5866068031,'Elettronica':412609031,'Fai da te':2454160031,'Film e TV':412606031,
                'Giardino e giardinaggio':635016031,'Giochi e giocattoli':523997031,'Gioielli':2454163031,'Illuminazione':1571292031,
                'Informatica':425916031,'Libri':411663031,'Libri in altre lingue':433842031,'Musica Digitale':1748203031,
                'Orologi':524009031,'Prima infanzia':1571286031,'Prodotti per animali domestici':12472499031,
                'Salute e cura della persona':1571289031,'Scarpe e borse':524006031,'Sport e tempo libero':524012031,
                'Strumenti Musicali':3628629031,'Valigeria':2454148031,'Videogiochi':412603031,'App e Giochi':1661660031,
                'Buoni regalo':3557017031,'Dispositivi Amazon & Accessori':12598749031,'Grandi elettrodomestici':14437356031,
                'Kindle Store':818937031,'Prodotti Handmade':9699425031,'Software':412612031
            },
            "es":{
                'Alimentación y bebidas':6198072031,'Bebé':1703495031,'Belleza':6198054031,'Bricolaje y herramientas':2454133031,
                'CDs y vinilos':599373031,'Coche y moto':1951051031,'Deportes y aire libre':2454136031,'Electrónica':599370031,
                'Equipaje':2454129031,'Hogar y cocina':599391031,'Iluminación':3564289031,'Industria, empresas y ciencia':5866088031,
                'Informática':667049031,'Instrumentos musicales':3628866031,'Jardín':1571259031,'Joyería':2454126031,
                'Juguetes y juegos':599385031,'Libros':599364031,'Libros en idiomas extranjeros':599367031,'Música Digital':1748200031,
                'Oficina y papelería':3628728031,'Otros Productos':667040031,'Películas y TV':599379031,
                'Productos para mascotas':12472654031,'Relojes':599388031,'Ropa':2846220031,'Salud y cuidado personal':3677430031,
                'Videojuegos':599382031,'Zapatos y complementos':1571262031,'Grandes electrodomésticos':4772050031,
                'Productos Handmade':9699482031,'Software':599376031,'Tienda Kindle':818936031,
                'Apps y Juegos':1661649031,'Cheques regalo':3564279031,'Dispositivos Amazon y Accesorios':12598806031
            },
            'in':
                {'Bags, Wallets and Luggage':2454169031,"Baby":1571274031,"Beauty":1355016031,"Books":976389031,"Car & Motorbike":4772060031,
                 "Clothing & Accessories":1571271031,"Computers & Accessories":976392031,"Electronics":976419031,"Grocery & Gourmet Foods":2454178031,
                 "Health & Personal Care":1350384031,"Home & Kitchen":976442031,"Home Improvement":3704992031,"Industrial & Scientific":5866078031,
                 "Jewellery":1951048031,"Movies & TV Shows":976416031,"Music":976445031,"Musical Instruments":3677697031,"Office Products":2454172031,
                 'Outdoor Living':2454175031,'Pet Supplies':2454181031,"Shoes & Handbags":1571283031,'Sports, Fitness & Outdoors':1984443031,
                 "Toys & Games":1350380031,'Video Games':976460031,"Watches":1350387031,"Software":976451031
                 },
            'br':{"Apps e Jogos":6446175011,"Bebê":17242603011,'Beleza':16194414011,'Binquedos e Jogos':16194299011,'Alimentos e Bebidas':18991079011,"Jardim e Piscina":18991021011,
                  'Casa':16191000011,"CD e Vinil":7791937011,'Computadores e Informática':16339926011,'Cozinha':16957125011,"DVD e Blu-ray":7791856011,'Eletrodomésticos':16522082011,
                  'Eletrônicos':16209062011,'Esporte':17349396011,'Ferramentas e Materiais de Construção':16957182011,'Games e Consoles':7791985011,
                  'Livros':6740748011,"Loja Kindle":5308307011,'Moda':17365811011,"Papelaria e Escritório":16957239011,"Saúde":16215417011,"Pet Shop":18991136011,"Automotivo":18914209011},

            'au':{"Alexa Skills":4931595051,"Apps & Games":2544160051,"Automotive":4851453051,"Baby":4851510051,"Beauty":4851567051,
                  "Books":4851626051,"CDs & Vinyl":4852330051,"Clothing, Shoes & Accessories":4851856051,"Computers":4851683051,"Electronics":4851799051,
                  "Everything Else":4103126051,'Health, Household & Personal Care':4851917051,'Home':4851975051,"Home Improvement":4852033051,
                  "Kindle Store":2490359051,"Kitchen & Dining":4852150051,"Lighting":4852207051,"Movies & TV":4852264051,'Pantry Food & Drinks':5547635051,
                  'Pet Supplies':5514967051,'Software':4852502051,'Sports, Fitness & Outdoors':4852559051,'Stationery & Office Products':4852445051,
                  'Toys & Games':4852617051,'Video Games':4852675051},
            'ca':{
                'Automotive':6948389011,"Baby":3561346011,"Beauty & Personal Care":6205124011,"Books":916520,"Clothing & Accessories":8604903011,"Electronics":667823011,
                'Everything Else':2356392011,"Featured Stores":916516,'Grocery & Gourmet Food':6967215011,'Health & Personal Care':6205177011,"Home":2206275011,
                'Industrial & Scientific':11076213011,'Jewelry':6205496011,'Livres':916522,'Luggage & Bags':6205505011,'Movies & TV':917972,'Music':916514,'Musical Instruments, Stage & Studio':6916844011,
                'Office Products':6205511011,'Patio, Lawn & Garden':6205499011,'Pet Supplies':6205514011,'Shoes & Handbags':8604915011,'Sports & Outdoors':2242989011,'Tools & Home Improvement':3006902011,
                'Toys & Games':6205517011,'Video':916518,'Video Games':3198031,'Watches':2235620011
            },
            'ae':{
                "Appliances":15149781031,"Automotive":11498031031,"Baby Products":11498088031,"Beauty":11497860031,
                "Books":11497689031,"Computers":11497746031,"Electronics":11601327031,"Fashion":11497632031,
                "Grocery":15150009031,"Health":11601441031,"Home":16725681031,"Kitchen":16402718031,
                "Mobile Phones & Communication Products":12303750031,"Office Products":15150351031,"Pet Supplies":15150408031,
                "Sporting Goods":11601213031,"Tools & Home Improvement":11601270031,"Toys":11497803031,"Videogames":11601384031,
            },
            "mx":{
                "Industria, Empresas y Ciencia":11076223011,"Juguetes y Juegos":11260442011,"Productos para Animales":11782336011,
                "Ropa, Zapatos y Accesorios":13848838011,"Automotriz y Motocicletas":13848848011,"Instrumentos Musicales":13848858011,
                "Tienda Kindle":6446439011,"Libros":9298576011,"Electrónicos":9482558011,"Hogar y Cocina":9482593011,
                "Salud, Belleza y Cuidado Personal":9482610011,"Música":9482620011,"Películas y Series de TV":9482630011,
                "Videojuegos":9482640011,"Bebé":9482650011,"Deportes y Aire libre":9482660011,"Herramientas y Mejoras del Hogar":9482670011,
                "Software":9482690011,"Oficina y Papelería":9673844011
            },
            "tr":{
                "Oyuncak":12467126031,"Spor ve Outdoor":12467068031,"Mutfak":12466781031,"Ofis ve Kırtasiye":12467009031,"Kitap":12466380031,
                "Yapı Market":12466724031,"Kadın Modası":13546651031,"Ev ve Yaşam":12466667031,"Elektronik":12466496031,"Erkek Modası":13546649031,
                "Bebek":12466208031,"Diğer Her Şey":12467297031,"Bilgisayarlar":12466439031,"Moda":12466553031,"Video Oyunu ve Konsol":12467183031
            }
        }
        self.country_site = {"de": "de", "fr": "fr", "uk": "co.uk", "jp": "co.jp", "us": "com", "it": "it", "es": "es",
                    'in': "in", 'br': 'com.br', 'au': "com.au", 'ca': "ca"}

    def get_asin(self, country, keyword, ad, timestamp):
        # 根据条件筛选出asin并整理去重返回
        table_name = country + '_asins'
        sql = f"select asin from {table_name} where keyword=%s and state>=2 and ad={ad} and timestamp>{timestamp}"
        params = (keyword,)
        print(sql%params)
        self.cursor.execute(sql, params)
        asin_list = []
        data_list = self.cursor.fetchall()
        # asin_data_list = []
        for data in data_list:
            asin = data[0]
            if asin.isnumeric():
                continue
            asin_list.append(asin)
        return list(set(asin_list))

    def get_data(self, asin_list, country, timestamp, ad, keyword, category_name='',category_url=''):
        # 根据asin获取并处理数据
        table_name = country + "_asins"
        data_list = []
        little_rank = []
        i = 0   # i,a只用于观察是否有asin无数据或虚拟物品过多影响结果
        a = 1
        # 遍历asin提取所有数据
        for asin in asin_list:
            print(asin)
            print(a,'==')
            print(len(data_list),'----')
            a+=1
            data = {}
            # 联表查询取出数据
            sql = f"""select a.asin as 'asin', a.keyword as 'keyword',a.pageNum as 'page', a.positionNum as 'ranking',
                            b.price as 'price', b.seller_type as 'seller_type', b.sellerName as 'sellerName', 
                            b.seller_num as 'seller_num', b.sellerID as 'sellerID', b.listing_rating as 'listing_rating', 
                            b.brand as 'brand', b.ratings as 'ratings', b.stock_status as 'stock_status', 
                            b.QA_num as 'QA_num', b.timestamp as 'time', b.country as 'country', 
                            b.reviews as 'reviews',b.critical as 'critical',b.vp_num as 'vp_num',
                            b.product_style as 'product_style' , a.ad as 'ad', b.avg30 as 'avg30'
                            from {table_name} as a left join product_detail as b on a.asin=b.asin
                            where a.asin='{asin}' and country='{country}' and b.timestamp>{timestamp} and a.ad={ad} and a.keyword='{keyword}' 
                            order by b.timestamp DESC"""
            self.cursor.execute(sql)
            detail_data = self.cursor.fetchone()
            # 整理数据
            if detail_data == None:
                continue
            country = detail_data[15]
            if category_name != '' and category_url != '':
                data['小类目'] = category_name
                data['类目链接'] = category_url
                data['小类目排名'] = ''
            data['asin'] = detail_data[0]
            data['站点'] = detail_data[15]
            data['产品链接'] = "https://www.amazon.%s/dp/" % self.country_site[country] + data['asin']
            # data['关键词'] = detail_data[1]
            result = self.collection.find_one({"asin": asin, "country": "%s"%country, "timestamp":{"$gte": timestamp}})
            if result != None:
                data['主图地址'] = "https://images-na.ssl-images-amazon.com/images/I/%s._AC_SL1000_.jpg"%result['img_list'][0] if len(result['img_list']) >0 else ''
                data['视频'] = "有" if result['other_info']['video'] else "无"
                data['所在页数'] = detail_data[2]
                data['页面排名'] = detail_data[3]
                # data['广告位'] = "是" if detail_data[20]==1 else "否"
                data['广告所在页数'] = ''
                data['广告页面排名'] = ''
                data['价格'] = max(detail_data[4], 0)
                data['变体'] = 1 if result['vari_num'] == None else result['vari_num']
                data['跟卖数'] = detail_data[7]
                data['A+'] = "有" if result['other_info']['aplus'] else "无"
                product_info = json.loads(result['product_info'])
                first_date = {
                    'us': 'Date First Available',
                    'jp': 'Date First Available',
                    'de': 'Im Angebot von Amazon.de seit',
                    'uk': 'Date First Available',
                    'fr': 'Date First Available',
                    'es': 'Date First Available',
                    'it': 'Im Angebot von Amazon.de seit',
                }
                data['上架日期'] = product_info.get(first_date[country], '') #('Im Angebot von Amazon.de seit', 0)
                # 提取出所有的类目数据并分为大类目和小类目数据
                sql = f"""select category, rank from product_rankinfo where asin = '{asin}' and country='{country}' and timestamp>{timestamp}"""
                self.cursor.execute(sql)
                rank_list = self.cursor.fetchall()
                big_rank_info = []    # 大类目列表
                little_rank_info = []  # 小类目列表
                for rank_data in rank_list:
                    if rank_data[0] in self.categoryIndexArr[country].keys():
                        rank_dict = {"category": rank_data[0], "rank": rank_data[-1]}
                        big_rank_info.append(rank_dict)
                    else:
                        rank_dict = {"category": rank_data[0], "rank": rank_data[-1]}
                        little_rank_info.append(rank_dict)
                data['大类目'] = big_rank_info[0]['category'] if len(big_rank_info) != 0 else ""
                data['大类目排名'] = big_rank_info[0]['rank'] if len(big_rank_info) != 0 else ""
                data['小类目数据'] = little_rank_info
                i +=len(little_rank_info)
                little_rank.extend(little_rank_info)
                data['近30天排名'] = '' if detail_data[21] <1 else detail_data[21]
                data['总评分人数'] = detail_data[11]
                data['listing评分'] = detail_data[9]
                # data['颜色/型号'] = detail_data[19]
                data['总评论数'] = detail_data[16]
                data['差评数'] = detail_data[17]
                data['VP评论数'] = detail_data[18]
                data['QA'] = max(detail_data[13], 0)
                data['品牌'] = detail_data[10].replace('Brand: ', '')
                sellerID = detail_data[8]
                if sellerID not in ["", '-']:
                    sql = """select negative_lifetime, count_lifetime from seller_info where sellerID='%s' order by timestamp DESC""" % sellerID
                    self.cursor.execute(sql)
                    seller_info = self.cursor.fetchone()
                    try:
                        data['feedback数'] = seller_info[-1]
                        data['feedback差评率'] = seller_info[0]/100
                    except:
                        print('===')
                        data['feedback数'] = 0
                        data['feedback差评率'] = 0
                else:
                    data['feedback数'] = ""
                    data['feedback差评率'] = ""

                if detail_data[5] == 0:
                    data['卖家类型'] = "虚拟"   # 此即为虚拟商品或书本之类的商品
                    continue
                elif detail_data[5] == 1:
                    data['卖家类型'] = "AMZ"
                elif detail_data[5] == 2:
                    data['卖家类型'] = "FBA"
                elif detail_data[5] == 3:
                    data['卖家类型'] = "MAH"
                # data['卖家类型'] = detail_data[5]
                data['店铺名称'] = detail_data[6]
                sales_sql = f"""select sales,date from product_sales where asin='{asin}'"""
                self.cursor.execute(sales_sql)
                sales_data = self.cursor.fetchall()
                # print(sales_data)
                if sales_data != []:
                    for sales in sales_data:
                        date = sales[-1]
                        sales = sales[0]
                        if date == "2020-07":
                            data['月销量'] = sales
                data['月销量'] = 0 if data.get('月销量', 0) == 0 else data['月销量']
                # data['sellerID'] = detail_data[8]
                # data['stock_status'] = detail_data[12]
                # data['time'] = detail_data[14]
                data_list.append(data)   # 将数据汇总
                # print(len(data_list), '----')
            else:
                print(f"====asin: {asin}, error: 没有抓取到详情页")

        # 将所有类目添加至一个列表中
        little_category = []
        for data in little_rank:
            little_category.append(data['category'])

        # 将列表去重赋给一个新的变量
        category_set = set(little_category)

        # 新建一个字典用于统计保存每个类目出现的次数
        category_dict = {}
        for category in category_set:
            value = little_category.count(category)
            category_dict[category] = value

        # 分情况处理，有时类目数很少只有一两个,再比较选出出现次数最多的一个大类目和两个小类目并返回结果
        if len(category_dict) >1:
            values = list(category_dict.values())
            target_values = []
            value_first = max(values)
            values.remove(value_first)
            value_next = max(values)
            for i in category_dict.items():
                if i[-1] in [value_first, value_next]:
                    target_values.append(i[0])
            category_first = target_values[0]
            category_next = target_values[1]
        elif len(category_dict) == 1:
            category_first = list(category_dict.keys())[0]
            category_next = list(category_dict.keys())[0]
        else:
            category_first = " "
            category_next = " "
        return data_list, category_first, category_next

    def save_data(self, data_list, country, ad):
        # 将结果保存为excel文件
        df = pd.DataFrame(data_list)
        if ad == 0:
            df.to_excel(f'data_{country}.xls')
        else:
            df.to_excel(f'ad_data_{country}.xls')

    def handle_data(self, data_list, category_first, category_next):
        # 根据最多的大类目和小类目数据处理一下数据,将不是这几个类目的数据置空
        result_list = []
        for data in data_list:
            if len(data['小类目数据']) > 0:
                if len(data['小类目数据']) == 1:
                    # print(data['小类目数据'][0]['category'])
                    if data['小类目数据'][0]['category'] in [category_next, category_first]:
                        if data['小类目数据'][0]['category'] == category_first:
                            data['小类目1'] = data['小类目数据'][0]['category']
                            data['小类目1排名'] = data['小类目数据'][0]['rank']
                            data['小类目2'] = ""
                            data['小类目2排名'] = ""
                        elif data['小类目数据'][0]['category'] == category_next:
                            data['小类目1'] = ""
                            data['小类目1排名'] = ""
                            data['小类目2'] = data['小类目数据'][0]['category']
                            data['小类目2排名'] = data['小类目数据'][0]['rank']
                    else:
                        data['小类目1'] = ""
                        data['小类目1排名'] = ""
                        data['小类目2'] = ""
                        data['小类目2排名'] = ""
                elif len(data['小类目数据']) > 1:
                    for category_data in data["小类目数据"]:
                        if category_data['category'] in [category_next, category_first]:
                            if category_data['category'] == category_first:
                                data['小类目1'] = category_data['category']
                                data['小类目1排名'] = category_data['rank']
                                if data.get('小类目2', "") == "":
                                    data['小类目2'] = ""
                                    data['小类目2排名'] = ""
                            elif category_data['category'] == category_next:
                                if data.get('小类目1', "") == "":
                                    data['小类目1'] = ""
                                    data['小类目1排名'] = ""
                                data['小类目2'] = category_data['category']
                                data['小类目2排名'] = category_data['rank']
                        else:
                            if data.get('小类目1', "") == "" and data.get('小类目2', "") == "":
                                data['小类目1'] = ""
                                data['小类目1排名'] = ""
                                data['小类目2'] = ""
                                data['小类目2排名'] = ""
            del data['小类目数据']
            result_list.append(data)
        return result_list

    def close(self):
        self.mysql.close()

class Bsrgata():
    # 用于整理类目数，未完成，暂时未用
    def __init__(self):
        self.mongodb = MongoDBserver()
        self.collection = self.mongodb.get_collection()
        self.mysql = Mysql_server()
        self.cursor = self.mysql.get_cursor()

    def get_category(self, category_id, level):
        params = (category_id, level)
        sql = """select category_name, category_id, level,parent_id from amz_category where category_id = %s and level=%s"""
        self.cursor.execute(sql)
        data_list = self.cursor.fetchall()
        result_list = []
        for data in data_list:
            result = {}
            result['category_name'] = data[0]
            result['category_id'] = data[1]
            result['level'] = data[2]
            result['parent_id'] = data[3]
            result_list.append(result)
        return result_list

    def close(self):
        self.mysql.close()


def keyword_data(country, keyword, category_name='', category_url=''):
    # 根据关键词提取数据
    g = Getdata()
    ad = 0
    country = country
    keyword = keyword
    # 通过时间戳提取指定时间之后爬取的数据
    timestamp = 0 #1597033933
    # 先提取不是广告位的数据，再提取是广告位的数据，最后两者联合去重之后保存位最终结果
    asin_list = g.get_asin(country=country, keyword=keyword, ad=ad, timestamp=timestamp)
    print(len(asin_list), '===')
    data_list, category_first, category_next = g.get_data(asin_list, country, timestamp, ad, keyword, category_name, category_url)
    print(len(data_list), '=====================')
    result_list = g.handle_data(data_list, category_first, category_next)
    print(category_first,"===", category_next)
    ad = 1
    ad_asin_list = g.get_asin(country=country, keyword=keyword, ad=ad, timestamp=timestamp)
    ad_data_list, first, next = g.get_data(ad_asin_list, country, timestamp, ad, keyword, category_name, category_url)
    print(len(ad_asin_list), '===')
    print(len(ad_data_list), '=======')
    g.close()
    ad_result_list = g.handle_data(ad_data_list, category_first, category_next)
    for asin in ad_asin_list:
        if asin in asin_list:
            for data in result_list:
                if data['asin'] == asin:
                    if data.get('广告页面排名', "") == "":
                        for ad_data in ad_result_list:
                            if asin == ad_data['asin']:
                                data['广告所在页数'] = ad_data['所在页数']
                                data['广告页面排名'] = ad_data['页面排名']
        else:
            for ad_data in ad_result_list:
                if asin == ad_data['asin'] :
                    if ad_data.get('广告页面排名', "") == "":
                        ad_data['广告所在页数'] = ad_data['所在页数']
                        ad_data['广告页面排名'] = ad_data['页面排名']
                        ad_data['页面排名'] = ""
                        ad_data['所在页数'] = ""
                        result_list.append(ad_data)
    g.save_data(result_list, country, ad=0)

if __name__ == '__main__':
    # bsr = Bsrgata()
    # level = 6
    # category_id = ''
    # result = []
    # while level > 1:
    #     result_list = bsr.get_category(category_id, level)
    #     print(result_list)
    #     result.append(result_list[0])
    #     category_id = result_list[0]['parent_id']
    #     level = result_list[0]['level'] - 1
    # bsr.close()
    # for result in result_list:
    #
    # keyword_data(country='us', keyword='bsr_565098', category_name='Desktops', category_url='https://www.amazon.com/Best-Sellers-Computers-Accessories-Desktop/zgbs/pc/565098/ref=zg_bs_nav_pc_1_pc/138-6908620-5007024')
    keyword_data(country='uk', keyword='External DVD Driver')
