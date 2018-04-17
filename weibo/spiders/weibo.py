import json
import re

from scrapy import Request, Spider

from weibo.items import *


class WeiboSpider(Spider):
    name = 'weibo'
    
    allowed_domains = ['m.weibo.cn']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'

    start_user = 3217179555
    
    def start_requests(self):
        yield Request(self.user_url.format(uid=self.start_user), callback=self.parse_user)
    
    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id': 'id', 'name': 'screen_name', 'url': 'profile_url', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item
            # 关注
            # 使用正则匹配过滤掉
            # uid=1022:100808e4ce58deae132199baf91c96cfc0b608
            # 等格式的问题
            uids = user_info.get('id')
            match_obj = re.match("1022:.*", str(uids))
            if match_obj:
                return
            else:
                uid = uids
            yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
                          meta={'page': 1, 'uid': uid})
            # 粉丝
            yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
                          meta={'page': 1, 'uid': uid})
            # 微博
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})
    
    def parse_follows(self, response):
        """
        解析用户关注
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get(
            'card_group'):
            # 解析用户
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    #使用正则匹配过滤掉
                    #uid=1022:100808e4ce58deae132199baf91c96cfc0b608
                    #等格式的问题
                    uids = follow.get('user').get('id')
                    match_obj = re.match("1022:.*", str(uids))
                    if match_obj:
                        return
                    else:
                        uid = uids
                    yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            
            uids = response.meta.get('uid')
            match_obj = re.match("1022:.*", str(uids))
            if match_obj:
                return
            else:
                uid = uids
            # 关注列表
            user_relation_item = UserRelationItem()
            follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')} for follow in
                       follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item
            # 下一页关注
            page = response.meta.get('page') + 1
            yield Request(self.follow_url.format(uid=uid, page=page),
                          callback=self.parse_follows, meta={'page': page, 'uid': uid})
    
    def parse_fans(self, response):
        """
        解析用户粉丝
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get(
            'card_group'):
            # 解析用户
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            # 使用正则匹配过滤掉
            # uid=1022:100808e4ce58deae132199baf91c96cfc0b608
            # 等格式的问题
            uids = response.meta.get('uid')
            match_obj = re.match("1022:.*", str(uids))
            if match_obj:
                return
            else:
                uid = uids
            # 粉丝列表
            user_relation_item = UserRelationItem()
            fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')} for fan in
                    fans]
            user_relation_item['id'] = uid
            user_relation_item['fans'] = fans
            user_relation_item['follows'] = []
            yield user_relation_item
            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield Request(self.fan_url.format(uid=uid, page=page),
                          callback=self.parse_fans, meta={'page': page, 'uid': uid})
    
    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    # weiboitem = WeiboItem()
                    # weiboitem["weibo_url"] = weibos["scheme"]
                    field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'picture': 'original_pic', 'pictures': 'pics',
                        'created_at': 'created_at', 'source': 'source', 'text': 'text', 'raw_text': 'raw_text',
                        'textLength': 'textLength',
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item
            # 下一页微博
            # 使用正则匹配过滤掉
            # uid=1022:100808e4ce58deae132199baf91c96cfc0b608
            # 等格式的问题
            uids = response.meta.get('uid')
            match_obj = re.match("1022:.*", str(uids))
            if match_obj:
                return
            else:
                uid = uids
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})
