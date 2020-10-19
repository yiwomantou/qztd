# 用于对评论进行谷歌翻译
# 已弃用


import json
import urllib.request
import urllib.parse
# from HandleJs import Py4Js
import execjs
from mysql_server import Mysql_server


class Py4Js():

    def __init__(self):
        self.ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 

        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 

        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 

    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)

    def getTk(self, text):
        return self.ctx.call("TL", text)


def open_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(req)
    data = response.read().decode('utf-8')
    return data


def translate(content, tk):
    if len(content) > 4891:
        print("翻译的长度超过限制！！！")
        return

    content = urllib.parse.quote(content)

    url = "http://translate.google.cn/translate_a/single?client=t" \
          "&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca" \
          "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1" \
          "&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&q=%s" % (tk, content)

    # 返回值是一个多层嵌套列表的字符串形式，解析起来还相当费劲，写了几个正则，发现也很不理想，
    # 后来感觉，使用正则简直就是把简单的事情复杂化，这里直接切片就Ok了
    result = open_url(url)
    result = json.loads(result)
    result_str = ''
    for data in result[0]:
        # print(data)
        try:
            result_str += data[0]
        except:
            pass
    return result_str
    # print(result_str)

def main():
    js = Py4Js()

    my = Mysql_server()
    cursor = my.get_cursor()
    # cursor.execute('select reviewID, review_title,review_body from product_reviews where state=0 LIMIT 2000')
    cursor.execute("""SELECT b.reviewID, b.review_title, b.review_body
                      FROM product as a JOIN product_reviews as b on a.asin=b.asin
                      where a.id>39 and b.state = 0
                      limit 2000""")
    data = cursor.fetchall()
    for task in data:
        update_sql = """update product_reviews set state=1 where reviewID=%s"""
        parse = (task[0],)
        cursor.execute(update_sql, parse)
        my.conn.commit()
        # print('---')
    for task in data:
        title = task[1]
        body = task[-1]
        reviewID = task[0]
        content = title
        tk = js.getTk(content)
        title = translate(content, tk)
        content = body
        tk = js.getTk(content)
        body = translate(content, tk)
        # print(title)
        update_sql = """update product_reviews set body_CN=%s, title_CN=%s, state=1 where reviewID=%s"""
        parmas = (body, title, reviewID)
        cursor.execute(update_sql, parmas)
        my.conn.commit()
        # print(task)
    # print(data)
    cursor.close()
    my.close()
    # if 1:
        # content_str = 'With all the teleworking surely needed this. It is surely cheaper than what I have purchased. This is really nice hasone hdmi port, one ethernet , 3 usb ports and one usb-c . I am not using the Ethernet port. No lag in the display port as Hdmi. The price is the major win.Material is not cheap. A light shows its working. Plus you get 24 months warranty.'
        # content = 'With all the teleworking surely needed this. It is surely cheaper than what I have purchased. This is really nice hasone hdmi port, one ethernet , 3 usb ports and one usb-c . I am not using the Ethernet port. No lag in the display port as Hdmi. The price is the major win.Material is not cheap. A light shows its working. Plus you get 24 months warranty.'
        # content = 'With all the teleworking surely needed this. It is surely cheaper than what I have purchased. This is really nice hasone hdmi port, one ethernet , 3 usb ports and one usb-c . I am not using the Ethernet port. No lag in the display port as Hdmi. The price is the major win.Material is not cheap. A light shows its working. Plus you get 24 months warranty.'
        # content = "I like it. Because a when u turn it on it's real quiet. And I like the smooth cut on it."
        # content = 'Disappointed, No rechargable battery. Works on regular AA battery.'
        # tk = js.getTk(content)
        # translate(content, tk)


if __name__ == "__main__":
    # for i in range(5):
    main()
        # print('----')
