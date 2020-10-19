# -*- coding: utf-8 -*-
import scrapy
import time
import random
import requests
import json
import re
import base64
from amz_spider.tool.db.mysql_server import Mysql_server, RedisDBserver
from amz_spider.tool.parse.productDetailParse import productDetailParse


class DetailParseSpider(scrapy.Spider):
    name = 'detail_parse'
    allowed_domains = ['www.amazon.com']
    start_urls = ['http://www.amazon']

    custom_settings = {
        "LOG_LEVEL": "ERROR",
        'RETRY_TIMES': 3,  # 重试次数，代理可用性差，商品为虚拟商品都会报错    #Todo: 区分出虚拟商品不进行重试
        'CONCURRENT_REQUESTS': 20,
        "COOKIES_ENABLED": False,
        'HTTPERROR_ALLOWED_CODES': [404, 503],
        'ITEM_PIPELINES': {
            'amz_spider.pipelines.AmzProductPipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'amz_spider.middlewares.DynamicForwardMiddleware': 399,
            'amz_spider.middlewares.ProxyMiddleware': 400,
        },
    }
    # 各站点月份数据
    us_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"]
    fr_month = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                "novembre", "décembre"]
    de_month = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
                "November", "Dezember"]
    es_month = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
                "noviembre", "diciembre"]
    it_month = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
                "ottobre", "novembre", "dicembre"]
    # 各站点网址后缀
    country_site = {"de": "de", "fr": "fr", "uk": "co.uk", "jp": "co.jp", "us": "com", "it": "it", "es": "es",
                    'in': "in", 'br': 'com.br', 'au': "com.au", 'ca': "ca"}

    def __init__(self):
        # keepa的API密钥
        self.keepa_key = "6q2g1drpvk3jar5ai0kh38g7e8v9rle661aq36468t65q5ht91n6gifo96juhgqf"
        # keepa的站点代号
        self.domain = {
            "us": 1,
            "uk": 2,
            "de": 3,
            "fr": 4,
            "jp": 5,
            "ca": 6,
            "it": 8,
            "es": 9,
            "in": 10,
        }
        # 各站点账号cookie，需要对应站点的正确收货地址才能获得想要的数据
        self.cookie_dict = {
            "us": "session-id=145-5209209-9478023; i18n-prefs=USD; ubid-main=133-8276981-7688751; x-wl-uid=1PCOyx0JI1kz7vWchZyMhRWJtqj1XoQoE0UNJPLhOT/Q8+kepq170hFhtVj1OBOSit46HW9f+Rz8=; lc-main=en_US; session-id-time=2082787201l; session-token=3TtwIpr/LCK/R5dUusiKqRfu1FQJmG80o4BC0knm7brPg8aelaJ+f/B16GedWlTyDSjn8qQo3s3PmGmw5mHywT8RWHthFHuduD76fCQKbeUHR0G/OJ4sj2eZxXUoxgcWn+a+xbKm+Rpj5ciXMPsk4ObS1HmuF5NFMFttjbT4ZsWQBxh5Ak9x1hxbsqNIrrrW; csm-hit=tb:0YBA58R18R2BQ1H4SWX6+b-0YBA58R18R2BQ1H4SWX6|1592453272955&t:1592453272955&adb:adblk_yes",
            "de": 'csm-hit=tb:s-Z4Z7WMBFVQ0ABCH6XK9S|1577677545204&t:1577677546441&adb:adblk_no; session-id=259-1276401-2743829; sst-acbde=Sst1|PQEPu0o5eYZUxJGuxJwpfg_WC6_bhWJ58B127R4E-yVlmzUncDHGVJEuvPcdeTSFLCr46FxTTBBmENyJHWXYL3G5ZNj0D8yw2JKzOscAj-L4k94mfh6PqxWdsBYizdtsfoJpA51JpyBi_nycjfwglJvTChnJJ789gwmxWlVCIZ45zc5oL9OOsWxo53FGYLqbW23xoQbXz60hzCaXsjfomUidzCkwYwSgZh7UZzZPp40dK7crXymBRUybkIeer8MaIcjLyRssvMq5xJHrdzcML4Lnc_sY_TXrC1S_2tJ9KenioWDczquh0hdcQG0vtaW5ZBywiQPCRRKxoR0Gjl4ZGgYLxA; lc-acbde=de_DE; sess-at-acbde="b2S0EPtbWAfDnsA6h/u1FCbd/2dZfWrriHRXzfr8Is0="; x-wl-uid=1WBHwWw4gIrICoU3vGJuxvGDY9h8lOehRIx/VCFzCHf9saT0o5up8lKpjD43ymXBJZM2m9qGBH8ueagjJA2JMKA==; i18n-prefs=EUR; at-acbde=Atza|IwEBIL3EQOtfB1lRuzuOe_tivj4Q_EE0Sn-x9ev5FGMcw0I_gZ6wQq28Q4pYExxPHzGFeA1VgJSQ_lWYjZO0thv7v29K0VIeDGlISMwjDFfw6vhxYKB7p4ChXoLyT2o-CO29oM0gN1wDBuaH4t_5Mf5di-6dh8mLVHeMPUlGOzHgwXzcJqOaiAQqKmlXiBSYrRvbXAWlkzHh_TB3NmL95BXGmHXvAuVdSNmQUftPujljoEKO5I-sDT83z4zQha3XgVCVAFcb91aYfQT2m4KCwF-1I9IJFjXEEJMN3lIQ-j8pwECFgdaSfyEV4fiq9ehEeBYZV0N2lpZF2CUt4Fa7_ayCKMrFLa2nlPTDlMRoXgHC5OOXVPsPN38L1zPe998RKC_QVus0vIFGqI2qOogybAfDqeJe; x-acbde="lnVyhTjvVGupfpMDC2vcQzkQOxyKLNYHZ?my0SNcOdsNjI878GYs4rGWtKNBVB1i"; a-ogbcbff=1; ubid-acbde=260-9492100-9469503; session-token="q19Fd14pFnO2DrmpQAzP8+PCdDYVmqKArAkwcYmHuAqo6dcD3NIgHcfSs3BvjywBr/Pym23U0uMYMHtDzP9xdChIh+n5JbxtkVRXSryLbiAPiWubkb8SXLrRMr7IB4PRbbZrhcbuyQRuuWTOxGpMtH6dawrAPlFYZDVhMLX6sIQ+gbQjWLOvyB9xaVpUpXMg/OqMIbNYPw9GMFoVliBOLug+47+yPca8Oce0KLb27mXubnKG1wVOCICEXrA8icugvMwrBvelPcwOfMiO8QUB3w=="; csm-hit=tb:s-3M7T2VFQGW3D918SHH2E|1593589245196&t:1593589257471&adb:adblk_no; session-id-time=2082754801l',
            "uk": 'csm-hit=tb:s-TXAS0E0D6KJE2VDWT9QF|1577677831398&t:1577677832885&adb:adblk_no; x-acbuk="qUA5lgVTaBle9QjwEqwBKkeUx9JIC39ro3Muj01D6ThKXdKk8IpTu@23XKRCXbjo"; i18n-prefs=GBP; lc-acbuk=en_GB; sst-acbuk=Sst1|PQGmxZNfcAKYJN0lvppkNMIkCwhyfc3GO7H0YlVKm9i3sEDvf_6MEpRdJKtqEbO_nSFI6Qwpn8t_SHgLjLZpmwdpMmrEX7mDEpLkxAmj02oCbxhS0via-Fm0Bq-u0K9qroPmrt2weKK57nKXRtpMH3gKQkFaFgLpMC284x8kacIP9kd6rRbH_vnJSP9m5vezW_U7565Ed7gXwd2D-aMAbdFcRm_t2KKX2YNj-1Q-AeOYr3TZyDj6nzozuedIgxA56PUO2jsnhwclEI3lJTEN77TcUs8-oJyNlwtEXVz3w07MP1AyiYKQ8vfIfFnsVm4wGjKiKvIJBBNLfKNMVmMfF0GsQw; sess-at-acbuk="w1+VeUFDyfy3ov+t/Ve0KwKErzOC50K1OU3sTopAenc="; at-acbuk=Atza|IwEBIBT8xYfFBQp-zHwkLG9uzAH67jrENqusAp2fViS6MZLRwnbIWK5kkJp7S-F2YUnym3W8hRw_dLfuENDiEErgBlHh1CH7m1376lFWA_Q-2XwCK7bL2FCs_Z6B8391aEKGnpp0bFF8Zt8mOKoe0rpBlq9122kzzfn0d0_Rf9vpmBjE9J46dr9n_imSDQeJ2I2H1G_019lRZO-r3zMK96Kh5ynQmPpCkfhsbRXuNXN8_n8jGsMSNnY9tEKHw3yZUIlNciXVn5rVuskuFzd5WNNxLNO8W6EERHE__-YABlyuVAlQWCMj_g1e38uekGxlt4-eQiUyy1vnObVw5uFVBxd2IsxX4k0zO8Fkt_4cB6vIMfWYl9F-Nq5z9jFdBdgGHu8e8jh7U00y4o7Nj-OUOG8rdVEP; a-ogbcbff=1; session-id=257-1255471-6821611; x-wl-uid=1m28fPT9Pp8KdgG3W1hfOjxkwgC8muaKRcj/+Ym9DU4HXCzZFH4/2+kqOo2f5QLOmBFQz59EvJxZPKOc8l3DFDg==; ubid-acbuk=260-5170770-8409944; session-token="fsd0czDZoWuzD0QTLzWL54R6QiWuI76COtqgUu5x3w2QL10r97/PJcrq4VhfGovxAJlhsCa6tjiQG85b/9I8y+5y0NXB5aCRVYeyoD0TKrTP9jAKLa1GIgs/ISIjLyEsVFW+wwSJZnDH3xIGMlqGUXT9sYUz1KF1i7/XkzqxK1enuafYuUGhsO/AVvcB3YoOkemx5LxZ9u1iyixRwnybMDSMtcb14AQ1cD6cKDs1sAuwvU1rFO+qY6PLEEKc/wLYurGbL5YKPyT18Q0qSGRhkA=="; session-id-time=2082758401l; csm-hit=tb:s-2FP155RVWD0F5WBS8Q5E|1593589148591&t:1593589152053&adb:adblk_no',
            "fr": 'csm-hit=tb:s-ZDDH6V7Z4K0TN2E1TAGJ|1577677668297&t:1577677670177&adb:adblk_no; x-wl-uid=1n0qVzT6Ht1vb3MEilzLsW/D/uRdZ0tdwHCCVjZ3098NXKPGliznHnVEBGkAAxGCEA+b7UDx6pXcCQFdC5FhtVA==; i18n-prefs=EUR; sst-acbfr=Sst1|PQG4tiiyrfz2eqyI0tnG1NUvC5DveQojoJEsGyVfWa3SIjtpYNQAa3z2Y7MAJhK1s1TPsXImWelDZBNgq2sHDDyqooD-yN78uTYKM7M9zDuF-HHWe4QaSiyR7EGFZD58HrZJsoPBiwOaCpf-jgmP4_-tpv4v271VlN3334WS8gps6dguWs2_PlQYAIV71pHKleeC4I1VMP-OUn_uUZ-7aZ4LRjOMWMn9sG7_MyISALOHbmIT6LafB1OA-H8xujzmwHQbfLw6QAX51des_mtdZe6bDtX73AQVFl2fxOiQaZctlc_7y9DbwjaMmpFYsdMysZuYx1Zp7ZUez6wEXGsY-wNETw; sess-at-acbfr="epT0K3YIgbfHd1Ao3BCPgk6Ilre3Fn9aJaKnyHJ/CIc="; session-id=260-1443667-2624466; at-acbfr=Atza|IwEBIDwewhuE8eregxrhPaQA6DY39pDb2jtft7b5qE8RbG8xyxzH1128_CkUK-c4X6RNrz9ftJxadeA2QUfO5AZ7UMxOybcam6wtMXtZkn9RBJYsHs20XUKIPLI7mtrbmTlfyxEe3ZoV5EAvSrZeYgT55H86QwC1r_bSYjxpD3EgwH0n-YR77kUbhl2eaOkK4xR35fVq-vCZHqCseT6kDxkwYDOiZlfTlHVxW6mmezw8kgW3v6dXn2FnbAk1iHKRArvx3yymgk4e5JzTlTzEk4G3JGWZjfegGuKaEvwz6BYxXYviimd4eqHW4OB7DbW8eDMHjMX0Hs8WR9pJlPAxtRO4LFOFo8u4GvUJ9xxif_7R8lcrvPaJRTaanU5NOz2avedb38kAcXyDTAX4vWQEl9qFWldj; x-acbfr="IisFXgALr0nZm3hCjGeKXa?CkwwD2nlqwmKLwYjPRBeX@79WPmSwTl3i17MO52D7"; ubid-acbfr=262-7600607-6817130; lc-acbfr=fr_FR; a-ogbcbff=1; csm-hit=tb:FTT1S8C3SGRACJFDBCN2+s-N70NK3256R8BST8HY7WA|1593589408582&t:1593589408582&adb:adblk_no; session-token=MQjl+KQcaoeMXa6VMpFqKCRVM9A2JXIHbpRbOSYa0m4MUxNPTidh7NHdcoC8PV3EMvFwVlrHJy4/Q3TSozudu2dY6d/1x9xkVEp6/Uy87io7WZYcVYE6i2oA0fDQJqPl1AfutDBmc1T2T9AQPxFWZHEjDFDWrovAhX8qy+lnDS1G5bsQ6ge2ZoxhK9aA9P/M+mdRYYhTJ0NT7GKElrFcMdZQNA4ulUh1TTXCffxCfaVOneu/PmK5Iw+ejcx6NqtyONwILPzJeFjU5xoFnC3UzoU/wFgFaUuW; session-id-time=2082754801l',
            "it": 'i18n-prefs=EUR; csm-hit=tb:s-502BH0EQDWNHQ13G9TG6|1577677608085&t:1577677609373&adb:adblk_no; session-id=260-4113858-9506138; x-acbit="gC5RyqlcCAFzDUyrl6k5gJui8X@gGPCYu8jnQoSUwyl74tPShyYXuz1stGVvP0eI"; lc-acbit=it_IT; sst-acbit=Sst1|PQEzpzpLJ_MrCJmoepDy1MtVCyTRuXA7YzZ8WImqZu_9ZkSCUgxgx_2iEzJCsjXIJKr6rZasDN3z2y6oyhNQZR09srdP-WeW-pZAb-tGliQ40jDxF9EbFxTfguqWQre0HEBel8enG-gndbKyp1kpGNLrU-VukYzIwFxR-fMNzc7Noyv-hb1C7Ktb5L4T38yRJn99mPHgaLTJkG9uGa3ebU9KbexNff8h-yiLdKhXKE_upHkZRbCWPU2niqH4PH6DDpeuimQPDZoMv93fUcD-Hm-WCQUSrhXFx-4ng98xKISK_6KkkoEYi1QzkvARqkKfUO8rt3G9onve-zu2--FezZSTBw; at-acbit=Atza|IwEBIMNl1h0jJA4QwlfndhPwGP_9_qjHlJkfA1m3BJfshusdsTcbUddMyiEUE-za-Cj4B71m8bZUEeGhj7ZPHh51JPAa16myrMGhKblKCHGt0sKzaUjD3g8Ex-dAOf1FGle1g6C8l9WUsXEG4PBhgB2PanrbWEoecP2uD5eRwzs2Dxsm9Ut5N7XeKuE6dlJVziGEC3jkSECd3Ww7wF_c5fNgkLbYRUbiGinVi1fz0dEvR6fqbfcaQ6IQ-0r9rS5RvWMFzmDgH4gm5ASMrogC92K_cwqYf52wltkRorJIFEGWZXYalUCOKfisw-RhkSokpjy9KSA6X2Tp9gw3Fx5cx35wpnXsr0COC8uwUg4fqlFZuNNcgcQMvaT8BOF_qFOY3RQCaAYFRia3EByAi_lyQm5uC6VN; sess-at-acbit="O+Jd5SFL2tIAnahQfIhDqOFzQpcgCMOeyrNj29WIpe4="; a-ogbcbff=1; ubid-acbit=258-9552575-1587721; x-wl-uid=1x7VDdcaVLANI7a9ZkGukZbfYABHrzevgPRcLp6qBkJWCWA17synOS3NlNQo6iCo7q59n2imeTZUHiLq+o23t6w==; session-token="tDxaLVHODnYvs0ykjduzWbMb24lxwWX9n74Cql4Zm7fzodwNPNrBboZAkjqd23umdJ4QxQzXHVxHM16+kicibDZHOv/2pWrI9kpC0JecieBQV7qocvaF+7wzCbzBNiOV+58CrwdvuyJlYfpnDb7ieaTYnKtHtWLD9k2Ju5qCJebB+zaPgrTCYY+JAXj4gYHaLCjlhVAb9MvXLS/jH4j0O1q60voiquYkLaV0QNfERx4gPmQxww3ctjHcvO14eCnDGtroJrl8yxfCD8jurp82Mw=="; csm-hit=tb:MPPG39M8GWCSDK57NXW9+s-06WPTW104GASGPHFAWDG|1593589527599&t:1593589527599&adb:adblk_no; session-id-time=2082787201l',
            "jp": 'session-id=357-6319383-5209943; x-wl-uid=1CZcX031MIY5z1U98RatTCCdgqIYs+1AaDSvKvm/1nXyIcoIl72ucvSZN52NlK4wsNMeds78jvBLMIOTIT+4rNg==; csm-hit=tb:s-NMPSRD78YVHMTSH07BJD|1576134237508&t:1576134239442&adb:adblk_no; i18n-prefs=JPY; sst-acbjp=Sst1|PQH34JNzxCReiHt1S7inLeQSCy9CSSvgq6wJGo2wgcQhKE_doSzUAsSa_0MI2sC3v0cdtnnWi3bHyE5eG5CGWysrZPEaVR4mDtTm7zlRtgM_CdSW1ivd8I4HhHD27R4K7HYdg6ovtXG-NlXCYvW64u-Ia4JufLQrhhtCOMpRVAdySp9uZq9xpyCye7aKDsQHhZTNEC-RnvQYnSQca0QxTIKLA9yvZbKqfoXkSQTPBk8Pqx9d_9ZC5MvfUG3T8EWXKR8m9SeYa7UlsWoeIolL3w2g_kj8JzYB9rs2v9XfA1wjrZ2F8gtBvqtZ4VWEPP6hVqfVXcND65fyBmjHBFXK4mECVw; lc-acbjp=ja_JP; at-acbjp=Atza|IwEBIPK3I5PvbJWXOp-o3zD6Y-3tYdUTceLdb79YIlREyRkbiQE32brB82lSRSMWaGvyeNL1MCg3cxHktLiIb7z5pnCc4dds2QiqP2CV_4vvmfVf4DqpoALy_qZhHwaoRZcUqZmMtHPtjTI9BX8fWdVzWnPkEe4kEKGAzTSB8w9B-PJz1qE806mzea2ex1774yn7LUZWHcGE4lO748WUC-DgIJ_BqAQubX6UTSjQiAEzTL4moKN6OLUgfDmU2E2Yzo9YePKi0JOopwaATI1sVNzczZ9rDfSlm6WeSFPzyocaw6wLK6Fk0pEj7mSnM7puRA-0K66l8BTQ_G_rVDSNoFsyGogBy4O4olQsc76Pab0lhIAO5W8JBP3m58lr90J7C_51WYrQs-6QNvzUtFbRsrTcfgot; sess-at-acbjp="IhokEOq3OQWhDlqZkHeNP0ZI/M/vWB8R9quFcOaEC6k="; skin=noskin; ubid-acbjp=358-4048879-7145210; x-acbjp="UrEw3363c0HaCQafMS92tlpcTy@pXvjV4QmhiqYC1yq7ilaRSJdah9fyopkDypR7"; a-ogbcbff=1; session-token="kw6/1LnZ4/yz9fY7031seOaGQPzHpC8Xk4wrCN1LSvTEsboLGQY6rTFETt8MKuBMw9zxXG4b/oerLZmBcVXgF9yI00hz9PHBx0sHW0SARNoLbmkDovIgcXCR0owIGxFe7jp5Jl8kVQvvz1+Cvhr7ejYTedCTvOBa/kYzFfV8nli7rIvbUEiVaImsxUZTU/NLSbrejxEZ4CJ2kmNW+U1K1Y08T0SdkLSU+23TocNIlU/Np3uaRxJcg2djr5TqWWED3PJb1yd0wKjYD5EhWq0WhA=="; csm-hit=tb:s-6AK6VR4DKFD24K2VK55R|1593590619642&t:1593590622954&adb:adblk_no; session-id-time=2082787201l',
            "es": 'csm-hit=tb:s-ADVQVFAYFRZ6NR7FZEC1|1577677725852&t:1577677727027&adb:adblk_no; lc-acbes=es_ES; at-acbes=Atza|IwEBIPHtzCfrI60y1yZSIJ4ynHKsRTFRjK8QMEIdekROKz8kG0qk05Q97whjhitpkDHp7KRCMhiRN-kbH5RT5y0sGq4lg7peSjuLahvTj07eapIXS2rFA7dd0Bd6J6tkaaS9cOeSmTZCZtibAZDoqOkYJhGpTdSksk1PRNby4DHrZgCcXimXidjB1Bt0hUL-svRpkNkGUIwvHmgZPpe1tiLXFyNt2C1d443STR-sh8T7Zi5UUUM7zDvkC98dX4w6J7oJ2W0cvxZoSvYIeMGoK_LW7-YFsf-pApuJkHEC2DXJUPI9rKbgXI20XEtK8zLcL5jVsatBH8E9K_1Lk1H551lAq82PatEFcdb9IJwkYMs14IRoObxMghR6OCLfkhzjo2cVC-3guwtW9BCPjC16cysqgEZc; sst-acbes=Sst1|PQFwy6KHoyYK5oOcTYw0dudvC_ld61tQjW9IbyxWV3YMeUGifccycODSmNSPldd595j0NS8IS1zesY-mEdYHkm3baTneFSPW6sRQdYoITT33GNrc3c70P6EE25PrgvKwGgwNklmrGd2rxuLIDQEvSx5HzqhskDH6K8nTA1dGo4XI3cvJKgPZfDBBfNJNQ1KQCRRtmBXr-NhtiUsVk42QaSVikMy6jlj92p0x5HlZr-SmvnKbfcGtjXCZMyhELMSppRSeLugiWfsSbwzqWbrmi9RJi3QRQ0Gs8d7OHtuyrXE8oo0xXdOGWI9nak5E4XqXs-0tR8HFbM_tJuwQc4Q6eD9eNw; a-ogbcbff=1; x-wl-uid=1c8abccv3r6xDbmZT6Srh7WbPRMqE8Bv9cEBOwjIYJOGB7WV1ptG0A/zgdL13uU1kZHn3ptwlIYJjfz4WWc55aQ==; i18n-prefs=EUR; ubid-acbes=259-7546150-3362905; sess-at-acbes="9wOdBMkF3xIRBr30uj9Sa0A1laDLKI4d24/z3uAAyzs="; x-acbes="lQSUAwJ@78iUORhUv9q7pmg7m138n4qzMHZpnjkxt6RUq0fgf28lu6thAm5EERtP"; session-id=260-9549251-6557741; csm-hit=tb:90Y8WCZ78ZTQBRBF4C0F+s-B90CWS4JJ3EMAHSBGH4T|1593589666333&t:1593589666333&adb:adblk_no; session-token="FaPR2oWRBDTcKl8I3xsOU2M57Dbb3MsKB8P1M8SH35H1rWN4SV/jpuohIh1fU8RSQPRKbOtWhndYZU1zlcKxTH01w1KtlRhax4qJqp4YJvJl+1BOal5HctjvLMrNYABAlbEY1AcCrJzvg540uBRcY7EL3yinzeKHX0UiaI+oOlF8nqdGOxK/CfaoxRfFbKMs5dUtOImlOgejL7tb8FEv5cPqjH+tqX+dp54Ah+1B+lReIb3pwnAXMzBVdWv4R/263WIj5vcz6CHtm0Twb2ASRg=="; session-id-time=2082787201l',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            "cookie": "session-id=145-5209209-9478023; i18n-prefs=USD; ubid-main=133-8276981-7688751; x-wl-uid=1PCOyx0JI1kz7vWchZyMhRWJtqj1XoQoE0UNJPLhOT/Q8+kepq170hFhtVj1OBOSit46HW9f+Rz8=; lc-main=en_US; session-id-time=2082787201l; session-token=3TtwIpr/LCK/R5dUusiKqRfu1FQJmG80o4BC0knm7brPg8aelaJ+f/B16GedWlTyDSjn8qQo3s3PmGmw5mHywT8RWHthFHuduD76fCQKbeUHR0G/OJ4sj2eZxXUoxgcWn+a+xbKm+Rpj5ciXMPsk4ObS1HmuF5NFMFttjbT4ZsWQBxh5Ak9x1hxbsqNIrrrW; csm-hit=tb:0YBA58R18R2BQ1H4SWX6+b-0YBA58R18R2BQ1H4SWX6|1592453272955&t:1592453272955&adb:adblk_yes"
        }

        # 各站点地址
        self.countryCodeArr = {"de": "www.amazon.de", "fr": "www.amazon.fr", "uk": "www.amazon.co.uk",
                               "jp": "www.amazon.co.jp",
                               "us": "www.amazon.com", "it": "www.amazon.it", "es": "www.amazon.es",
                               "ca": "www.amazon.ca",
                               "au": "www.amazon.com.au"}

        # 实例化解析对象
        self.product_object = productDetailParse()
        # self.cookies = dict()
        # self.cookiejars = dict()
        # self.proxy_server = {}

        # 任务站点列表
        self.country_list = ["es"]  # ["us", "uk", "de", "fr", "it", "es", "jp"]

        # redis服务
        r = RedisDBserver()
        self.collection = r.get_collection()

    def start_requests(self):
        # 取出各站点任务asin，并把状态从0改为1表示正在爬取
        for country in self.country_list:
            mysql_server = Mysql_server()
            cursor = mysql_server.get_cursor()
            table_name = country + '_asins'
            cursor.execute(f"select asin from {table_name} where state=0 limit 10")
            task_list = cursor.fetchall()
            print(task_list)
            for task in task_list:
                task = {'asin': task[0], 'country': country}
                parmas = (task['asin'],)
                update_sql = f"""update {table_name} set state=1 where asin=%s"""
                cursor.execute(update_sql, parmas)
            mysql_server.conn.commit()
            mysql_server.close()
            # 测试用例
            # print(task_list)
            # asin_list = [{'country': 'it', 'asin': 'B07VB8WXNF'}]
            # asin_list = [{'countrycode': 'us', 'asin': 'B07FJGGWJL'}, {'countrycode': 'de', 'asin': 'B00Y211AFM'},
            #              {'countrycode': 'fr', 'asin': 'B00GS19NWG'}, {'countrycode': 'uk', 'asin': 'B0000E5SEQ'},
            #              {'countrycode': 'it', 'asin': 'B07VMRB2K1'}, {'countrycode': 'es', 'asin': 'B07FPFKL4X'},
            #              {'countrycode': 'ca', 'asin': 'B00XMD7KPU'}, {'countrycode': 'au', 'asin': 'B075FQY5BN'},]
            # {'countrycode': 'jp', 'asin': 'B07RPVQY62'}]

            # 整理数据，发送请求
            for task in task_list:
                task = {'asin': task[0], 'country': country}
                if len(task['asin']) > 10 and '?' in task['asin']:
                    asin = task['asin'].split('/')[-1].split('?')[0]
                    if len(asin) == 10:
                        asin = asin.upper()
                elif len(task['asin']) == 10:
                    asin = task['asin'].upper()
                url = "https://www.amazon.%s/dp/" % self.country_site[task['country']] + task[
                    'asin'] + '?th=1&psc=1&language=en_US'
                # https://www.amazon.co.uk/dp/B071GYJTST?th=1&psc=1&language=en_US
                # self.headers['Referer'] = url
                # self.headers['cookie'] = self.cookie_dict[country]
                yield scrapy.Request(url, meta={'country': task['country'], 'asin': task['asin'], 'type': "init",
                                                'retry_number': 0, 'table_name': table_name},
                                     callback=self.parse, dont_filter=True)

    def parse(self, response):
        # 代理状态更新, 如果代理可用，则给一个高分数令其至前，否则给一个低分数置后
        proxy = response.meta.get('proxy', '').replace('https://', '').replace('http://', '')
        proxy_data = {"proxy": proxy,
                      "fail_count": 0, "region": "", "type": "",
                      "source": "spider",
                      "check_count": 20, "last_status": 0,
                      "last_time": ""}
        retry_number = response.meta["retry_number"]

        # 当页面10次都未成功提取数据则停止任务
        if retry_number > 10:
            return
        table_name = response.meta["table_name"]
        status = response.status
        url = response.url
        asin = response.meta["asin"]
        country = response.meta['country']
        if status == 200 or status == 503:
            try:
                # 判断是否为验证码，若是则更新代理状态并重试
                if len(response.body) < 10000 or status == 503:
                    proxy_data['fail_count'] = 18
                    self.collection.hset(name="useful_proxy", key=proxy, value=json.dumps(proxy_data))
                    yield scrapy.Request(url, meta={'country': country, 'asin': asin, 'type': "init",
                                                    'retry_number': retry_number, 'table_name': table_name},
                                         callback=self.parse, dont_filter=True)
                    return

                # 不是代理则解析数据
                self.product_object.initial_data = response.text
                self.product_object.countryCode = country
                item = {}
                item['asin'] = asin
                item['country'] = country
                self.product_object.best_seller_rank()
                self.product_object.seller_info()
                self.product_object.revews_rating()
                item['frequently_bought_asins'] = self.product_object.frequently_bought_asins  # 关联购买
                # item['rank_list'] = self.product_object.rank_list
                item['seller_type'] = int(self.product_object.seller_type)  # 卖家类型
                item['seller_num'] = int(self.product_object.seller_num)  # 卖家数量，跟卖数
                # item['merchant'] = self.product_object.merchant
                item['brand'] = self.product_object.brand  # 品牌
                item['price'] = float(self.product_object.price)  # 价格
                item['ratings'] = int(self.product_object.reviews)  # 评分人数
                item['listing_rating'] = float(self.product_object.rating)  # 商品评分
                item['title'] = str(self.product_object.title)  # 标题
                item['stock_status'] = int(self.product_object.availability[0])  # 库存状态
                item['QA_num'] = int(self.product_object.QA_num)  # QA数
                item['img_list'] = self.product_object.img_list  # 图片地址列表
                variant_data = self.product_object.variant_list
                if len(variant_data) == 3:
                    item['variant_list'] = variant_data[0]  # 变体列表
                    item['parentasin'] = variant_data[1]  # 父asin
                    item['vari_num'] = variant_data[-1]  # 变体数
                else:
                    item['variant_list'] = ''
                    item['parentasin'] = ''
                    item['vari_num'] = ''
                item['rank_list'] = self.product_object.rank_list  # 排名信息
                item['feature'] = self.product_object.description['feature']  # 五点描述
                item['sellerName'] = self.product_object.merchantName  # 卖家名称
                item['sellerID'] = self.product_object.merchantUrl  # 卖家ID
                item['product_info'] = self.product_object.product_info  # 产品A+ 页面信息
                item['compare_info'] = self.product_object.compare_info  # 产品比较信息
                item['product_descript'] = self.product_object.product_descript  # 产品技术信息
                item['other_info'] = self.product_object.other_info  # 其他信息
                # 亚马逊反爬手段之一，不给下列字段信息，其余信息完整无误，此时需要重新爬取,但是有的商品确实没有这些信息,如虚拟商品，所以重试一定次数截止
                if len(item['product_descript']['product_dict']) == 0 and len(
                        item['product_descript']['product_info']) == 0 and len(
                    item['product_descript']['other_info']) == 0 and retry_number < 1:
                    raise Exception
                else:
                    url = f"https://www.amazon.{self.country_site[item['country']]}/product-reviews/{item['asin']}?formatType=current_format"
                    yield scrapy.Request(url, meta={'country': item['country'], 'asin': item['asin'], 'type': "init",
                                                    'retry_number': retry_number, 'table_name': table_name,
                                                    "item": item,
                                                    "flag": 0},
                                         callback=self.parse_reviews, dont_filter=True)

            except Exception as e:
                # 提取信息出错则重试
                print('提取信息出错则重试', e)
                retry_number += 1
                yield scrapy.Request(url, meta={'country': country, 'asin': asin, 'type': "init",
                                                'retry_number': retry_number, "table_name": table_name},
                                     callback=self.parse, dont_filter=True)
            finally:
                # 更新代理信息
                self.collection.hset(name="useful_proxy", key=proxy, value=json.dumps(proxy_data))

        elif status == 404:
            # 商品已下架或更改,则改变商品状态
            self.collection.hset(name="useful_proxy", key=proxy, value=json.dumps(proxy_data))
            mysql_server = Mysql_server()
            cursor = mysql_server.get_cursor()
            params = (asin,)
            update_sql = f"""update {table_name} set state=-1 where asin=%s"""
            cursor.execute(update_sql, params)
            mysql_server.conn.commit()

    def parse_reviews(self, response):
        # 爬取评论人数相关数据          #Todo: 考虑是否拆分出去
        proxy = response.meta.get('proxy', '').replace('https://', '').replace('http://', '')
        proxy_data = {"proxy": proxy,
                      "fail_count": 0, "region": "", "type": "",
                      "source": "spider",
                      "check_count": 20, "last_status": 0,
                      "last_time": ""}
        retry_number = response.meta["retry_number"]
        item = response.meta["item"]
        table_name = response.meta["table_name"]
        status = response.status
        url = response.url
        asin = response.meta["asin"]
        country = response.meta['country']
        flag = response.meta['flag']
        if status == 200 or status == 503:
            try:
                if len(response.body) < 10000 or status == 503:
                    proxy_data['fail_count'] = 18
                    self.collection.hset(name="useful_proxy", key=proxy, value=json.dumps(proxy_data))
                    yield scrapy.Request(url, meta={'country': country, 'asin': asin, 'type': "init",
                                                    'retry_number': retry_number, 'table_name': table_name,
                                                    "item": item,
                                                    'flag': flag},
                                         callback=self.parse_reviews, dont_filter=True)
                    return
                try:
                    # 提取评论数
                    # m_add:新增实际评论人数
                    actual_reviews_count = 0
                    if country == 'fr':
                        reviews_count = \
                            response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',',
                                                                                                                   '').replace(
                                '.', '')
                        reviews_count = re.findall('sur ([0-9]+)', reviews_count)[0]
                    elif country == 'it':
                        reviews_count = \
                            response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',',
                                                                                                                   '').replace(
                                '.', '')
                        # print(reviews_count, '------')
                        reviews_count = re.findall('su ([0-9]+)', reviews_count)[0]
                    elif country == 'de':  # or countrycode == 'uk':
                        reviews_count = \
                            response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',',
                                                                                                                   '').replace(
                                '.', '')
                        # print(reviews_count, '------')
                        reviews_count = re.findall('von ([0-9]+)', reviews_count)[0]
                    elif country == 'uk':
                        reviews_count = \
                            response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',',
                                                                                                                   '').replace(
                                '.', '')
                        # print(reviews_count, '------')
                        reviews_count = re.findall('of ([0-9]+)', reviews_count)[0]
                    elif country == 'es':
                        reviews_count = \
                            response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',',
                                                                                                                   '').replace(
                                '.', '')
                        # print(reviews_count, '------')
                        reviews_count = re.findall('de ([0-9]+)', reviews_count)[0]
                    else:
                        reviews_count = \
                            response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().split(' ')[
                                -2].replace(',', '').replace('.', '')
                except:
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]//span/text()').extract()
                    if reviews_count != []:
                        actual_reviews_count = reviews_count[-1].strip().split(' ')[0]
                        reviews_count = re.findall('\| (.*?) ', reviews_count[-1])[0]
                        reviews_count = reviews_count.replace(',', '').replace('.', '').replace(' ', '')
                    else:
                        reviews_count = 0
                        actual_reviews_count = 0
                # flag=0 提取的是当前asin评论总人数
                # flag=1 asin差评数
                # flag=2 asin的VP评论数
                if flag == 0:
                    try:
                        item["reviews"] = int(reviews_count)
                    except:
                        item["reviews"] = int(''.join(reviews_count.split()))
                    try:
                        item["actual_reviews"] = int(''.join(actual_reviews_count.split('.')))
                    except:
                        try:
                            item["actual_reviews"] = int(''.join(actual_reviews_count.split(',')))
                        except:
                            item["actual_reviews"] = int(''.join(actual_reviews_count.split()))
                    flag += 1
                    url = f"https://www.amazon.{self.country_site[item['country']]}/product-reviews/{item['asin']}?filterByStar=critical&pageNumber=1&formatType=current_format"
                elif flag == 1:
                    flag += 1
                    try:
                        item["critical"] = int(reviews_count)
                    except:
                        item["critical"] = int(''.join(reviews_count.split()))
                    url = f"https://www.amazon.{self.country_site[item['country']]}/product-reviews/{item['asin']}?reviewerType=avp_only_reviews&pageNumber=1&formatType=current_format"
                elif flag == 2:
                    try:
                        item["vp_num"] = int(reviews_count)
                    except:
                        item["vp_num"] = int(''.join(reviews_count.split()))
                    try:
                        item['product_style'] = response.xpath(
                            'string(//div[@id="cm_cr-review_list"]/div/div/div/div/a[@data-hook="format-strip"])').extract_first()
                    except:
                        item['product_style'] = ''
                    url = f'https://api.keepa.com/product?key={self.keepa_key}&domain={self.domain[country]}&asin={item["asin"]}&stats=180'
                    yield scrapy.Request(url, meta={'country': country, 'asin': asin, 'type': "init",
                                                    'retry_number': retry_number, 'table_name': table_name,
                                                    "item": item,
                                                    "flag": flag},
                                         callback=self.parse_keepa, dont_filter=True)
                    return
                # 提取完总评论数、差评数、VP评论数则提取近30天排名
                yield scrapy.Request(url, meta={'country': country, 'asin': asin, 'type': "init",
                                                'retry_number': retry_number, 'table_name': table_name, "item": item,
                                                "flag": flag},
                                     callback=self.parse_reviews, dont_filter=True)
            except Exception as e:
                # 出错则重试
                print('出错则重试', e)
                url = response.url
                yield scrapy.Request(url, meta={'country': country, 'asin': asin, 'type': "init",
                                                'retry_number': retry_number, 'table_name': table_name, "item": item,
                                                "flag": flag},
                                     callback=self.parse_reviews, dont_filter=True)

    def parse_keepa(self, response):
        # 从keepa提取近30天排名
        print('从keepa提取近30天排名')
        retry_number = response.meta["retry_number"]
        item = response.meta["item"]
        table_name = response.meta["table_name"]
        status = response.status
        url = response.url
        asin = response.meta["asin"]
        country = response.meta['country']
        data = json.loads(response.body)
        # item['avg30'] = data['products'][0]["stats"].get("avg30", ['', '', '', ''])[3]
        avg_data = data['products'][0].get("stats", {})
        if avg_data != None:
            item['avg30'] = avg_data.get("avg30", ['', '', '', ''])[3]
        else:
            item['avg30'] = 0
        timedata = data['products'][0].get("trackingSince", 0)
        if timedata != 0:
            timestamp = (timedata + 21564000) * 60
            if country in ['us', 'jp', 'fr', 'uk', 'es']:
                item['product_info']["Date First Available"] = \
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)).split(' ')[0]
            else:
                item['product_info']["Im Angebot von Amazon.de seit"] = \
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)).split(' ')[0]
            yield item
        else:
            yield item
        mysql_server = Mysql_server()
        cursor = mysql_server.get_cursor()
        params = (asin,)
        update_sql = f"""update {table_name} set state=2 where asin=%s"""
        cursor.execute(update_sql, params)
        mysql_server.conn.commit()
        mysql_server.close()
