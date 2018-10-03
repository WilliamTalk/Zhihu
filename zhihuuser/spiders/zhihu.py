# -*- coding: utf-8 -*-
import scrapy
import json
from zhihuuser.items import ZhihuuserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user="excited-vczh"
    user_url='https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query='allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    followees_url='https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followees_include='data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_url='https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_include='data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    def start_requests(self):
         yield scrapy.Request(url=self.user_url.format(user=self.start_user,include=self.user_query),callback=self.parse_user)
         #yield scrapy.Request(url=self.followees_url.format(user=self.start_user,include=self.followees_include,offset=0,limit=20),callback=self.parse_followee)
    def parse_user(self, response):
        # print(response.text)
        result=json.loads(response.text)
        item= ZhihuuserItem()
        for field in item.fields:
            if field in result.keys():
                item[field]=result[field]
        yield item

        yield scrapy.Request(
            url=self.followees_url.format(user=item['url_token'], include=self.followees_include, offset=0, limit=20),
            callback=self.parse_followee)
        yield scrapy.Request(
            url=self.followers_url.format(user=item['url_token'], include=self.followers_include, offset=0, limit=20),
            callback=self.parse_follower)


    def parse_followee(self, response):
        result=json.loads(response.text)
        if 'data' in result.keys():
            for item in result['data']:
                yield scrapy.Request(url=self.user_url.format(user=item['url_token'], include=self.user_query),callback=self.parse_user)
        if 'paging' in result.keys() and result['paging']['is_end']==False:
            next_page=result['paging']['next']
            yield scrapy.Request(url=next_page,callback=self.parse_followee)

    def parse_follower(self, response):
        result=json.loads(response.text)
        if 'data' in result.keys():
            for item in result['data']:
                yield scrapy.Request(url=self.user_url.format(user=item['url_token'], include=self.user_query),callback=self.parse_user)
        if 'paging' in result.keys() and result['paging']['is_end']==False:
            next_page=result['paging']['next']
            yield scrapy.Request(url=next_page,callback=self.parse_follower)


