from scrapy import Item, Field


class UserItem(Item):
    collection = 'users'
    
    id = Field()  # 用户ID
    name = Field()  # 用户名
    url = Field()  # 微博地址
    avatar = Field()  # 头像地址
    cover = Field()  # 背景地址
    gender = Field()  # 性别
    description = Field()  # 简介
    fans_count = Field()  # 粉丝数
    follows_count = Field()  # 关注数
    weibos_count = Field()  # 微博数
    verified = Field()  # 是否认证
    verified_reason = Field()  # 认证理由
    verified_type = Field()  # 认证类型
    follows = Field()  # 关注者列表
    fans = Field()  # 粉丝列表
    crawled_at = Field()  # 爬取时间


class UserRelationItem(Item):
    collection = 'users'
    
    id = Field()  # 用户ID
    follows = Field()  # 关注者列表
    fans = Field()  # 粉丝列表


class WeiboItem(Item):
    collection = 'weibos'
    
    id = Field()
    attitudes_count = Field()  # 点赞数
    comments_count = Field()  # 评论数
    reposts_count = Field()  # 转发数
    picture = Field()  # 多张图片博文连接在一起的地址
    pictures = Field()  # 各张图片地址
    source = Field()  # 来源
    text = Field()  # 微博内容
    raw_text = Field()  # 转发时的添加内容
    textLength = Field()  # 微博长度
    user = Field()  # 作者
    created_at = Field()  # 微博创建时间
    crawled_at = Field()  # 微博爬取时间


