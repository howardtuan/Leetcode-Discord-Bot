import discord
import random
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import datetime
import asyncio
import pytz

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 設定固定的頻道 ID，用於發送每日挑戰
DAILY_CHALLENGE_CHANNEL_ID = 你的頻道ID

# GraphQL 查詢隨機題目
def get_all_titles():
    url = "https://leetcode.com/api/problems/all/"
    slugs = []
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        r_json = response.json()
        for slug in r_json["stat_status_pairs"]:
            slugs.append({
                "title_slug": slug["stat"]["question__title_slug"],
                "difficulty": slug["difficulty"]["level"]  # 1: Easy, 2: Medium, 3: Hard
            })
    return slugs

def get_quest_info(title):
    query = """
    query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    libraryUrl\n    __typename\n  }\n}\n
    """
    body = {"operationName":"questionData",
            "variables":{"titleSlug":title},
            "query":query}

    url = "https://leetcode.com/graphql"
    try:
        response = requests.post(url, json=body)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        r_json = response.json()
        return r_json["data"]["question"]

def parseContent(content):
    if content is None:
        return None
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()

def parseTags(tags):
    return ", ".join([tag['name'] for tag in tags])

# 取得隨機 LeetCode 題目的詳細信息
def get_random_leetcode_question(difficulty=None):
    slugs = get_all_titles()
    if not slugs:
        return None

    # 根據難度篩選題目，如果沒有指定難度就抽取所有題目
    if difficulty:
        filtered_slugs = [slug['title_slug'] for slug in slugs if slug['difficulty'] == difficulty]
    else:
        filtered_slugs = [slug['title_slug'] for slug in slugs]

    if not filtered_slugs:
        return None

    random_slug = random.choice(filtered_slugs)
    quest_json = get_quest_info(random_slug)
    
    if quest_json:
        id = quest_json['questionFrontendId']
        title = quest_json['title']
        titleSlug = quest_json['titleSlug']
        content = parseContent(quest_json['content'])
        isPaidOnly = quest_json['isPaidOnly']
        difficulty = quest_json['difficulty']
        likes = quest_json['likes']
        dislikes = quest_json['dislikes']
        tags = parseTags(quest_json['topicTags'])
        question_url = f"https://leetcode.com/problems/{titleSlug}/description/"
        return {
            "id": id,
            "title": title,
            "content": content,
            "isPaidOnly": isPaidOnly,
            "difficulty": difficulty,
            "likes": likes,
            "dislikes": dislikes,
            "tags": tags,
            "question_url": question_url
        }
    else:
        return None

# 獲取當天的 LeetCode 每日挑戰
def get_daily_leetcode_challenge():
    query = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            userStatus
            link
            question {
                questionId
                questionFrontendId
                boundTopicId
                title
                titleSlug
                content
                translatedTitle
                translatedContent
                isPaidOnly
                difficulty
                likes
                dislikes
                isLiked
                similarQuestions
                contributors {
                    username
                    profileUrl
                    avatarUrl
                    __typename
                }
                langToValidPlayground
                topicTags {
                    name
                    slug
                    translatedName
                    __typename
                }
                companyTagStats
                codeSnippets {
                    lang
                    langSlug
                    code
                    __typename
                }
                stats
                hints
                solution {
                    id
                    canSeeDetail
                    __typename
                }
                status
                sampleTestCase
                metaData
                judgerAvailable
                judgeType
                mysqlSchemas
                enableRunCode
                enableTestMode
                envInfo
                libraryUrl
                __typename
            }
        }
    }
    """
    
    url = "https://leetcode.com/graphql"
    try:
        response = requests.post(url, json={"query": query})
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None
    else:
        r_json = response.json()
        if 'data' in r_json and r_json['data'] and 'activeDailyCodingChallengeQuestion' in r_json['data']:
            daily_data = r_json['data']['activeDailyCodingChallengeQuestion']
            question = daily_data['question']
            
            return {
                "id": question['questionFrontendId'],
                "title": question['title'],
                "content": parseContent(question['content']),
                "isPaidOnly": question['isPaidOnly'],
                "difficulty": question['difficulty'],
                "likes": question['likes'],
                "dislikes": question['dislikes'],
                "tags": parseTags(question['topicTags']),
                "question_url": f"https://leetcode.com{daily_data['link']}",
                "date": daily_data['date']
            }
        return None

# 根據難易度返回顏色
def get_difficulty_color(difficulty):
    if difficulty == "Easy":
        return 0x00FF00  # 綠色
    elif difficulty == "Medium":
        return 0xFFFF00  # 黃色
    elif difficulty == "Hard":
        return 0xFF0000  # 紅色
    else:
        return 0xFFFFFF  # 預設為白色

# 創建 LeetCode 題目的嵌入訊息
def create_leetcode_embed(question_data, is_daily=False):
    # 根據難度設置顏色
    embed_color = get_difficulty_color(question_data['difficulty'])
    
    title_prefix = "LeetCode 每日挑戰" if is_daily else "LeetCode 隨機抽題"
    
    # 建立嵌入訊息
    embed = discord.Embed(
        title=f"{title_prefix}：{question_data['title']}",
        url=question_data['question_url'],
        description=f"ID: {question_data['id']}",
        color=embed_color
    )

    embed.add_field(name="難度", value=question_data['difficulty'], inline=True)
    embed.add_field(name="是否付費題", value="是" if question_data['isPaidOnly'] else "否", inline=True)
    embed.add_field(name="喜歡", value=question_data['likes'], inline=True)
    embed.add_field(name="不喜歡", value=question_data['dislikes'], inline=True)
    embed.add_field(name="Tags", value=question_data['tags'], inline=False)
    
    if 'date' in question_data and is_daily:
        embed.add_field(name="日期", value=question_data['date'], inline=False)
        
    embed.add_field(
        name="題目內容", 
        value=(question_data['content'][:500] + "...") if question_data['content'] and len(question_data['content']) > 500 else (question_data['content'] or "無內容"), 
        inline=False
    )
    
    return embed

# 每日定時發送 LeetCode 每日挑戰
# 每日定時發送 LeetCode 每日挑戰
async def send_daily_challenge():
    await client.wait_until_ready()
    
    # 記錄上次發送日期，避免重複發送
    last_send_date = None
    
    while not client.is_closed():
        try:
            # 獲取台灣時間
            taiwan_tz = pytz.timezone('Asia/Taipei')
            now = datetime.datetime.now(taiwan_tz)
            current_date = now.date()
            
            # 如果今天還沒發送且時間在早上10點之後
            if (last_send_date != current_date and 
                (now.hour > 10 or (now.hour == 10 and now.minute >= 0))):
                
                print(f"Attempting to send daily challenge at {now}")
                
                # 獲取每日挑戰
                daily_challenge = get_daily_leetcode_challenge()
                
                if daily_challenge:
                    embed = create_leetcode_embed(daily_challenge, is_daily=True)
                    
                    # 發送到指定的頻道
                    channel = client.get_channel(DAILY_CHALLENGE_CHANNEL_ID)
                    if channel:
                        await channel.send(embed=embed)
                        print(f"Sent daily challenge to channel {DAILY_CHALLENGE_CHANNEL_ID}")
                        # 更新發送日期
                        last_send_date = current_date
                    else:
                        print(f"Channel {DAILY_CHALLENGE_CHANNEL_ID} not found")
                else:
                    print("Failed to get daily challenge, will retry in 5 minutes")
            
            # 計算等待時間 - 如果今天已發送，等到明天早上 10 點
            if last_send_date == current_date:
                tomorrow = now + datetime.timedelta(days=1)
                target = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
            else:
                # 如果今天還沒發送且時間還沒到10點，等到今天10點
                if now.hour < 10:
                    target = now.replace(hour=10, minute=0, second=0, microsecond=0)
                else:
                    # 如果已經過了10點但還沒發送，立即重試（等待5分鐘）
                    await asyncio.sleep(300)
                    continue
            
            wait_seconds = (target - now).total_seconds()
            
            # 避免等待太久，定期檢查（最多等待1小時）
            wait_seconds = min(wait_seconds, 3600)
            
            print(f"Waiting {wait_seconds:.2f} seconds until next check for daily challenge")
            await asyncio.sleep(wait_seconds)
                
        except Exception as e:
            print(f"Error in send_daily_challenge task: {e}")
            # 錯誤發生時等待 5 分鐘後重試
            await asyncio.sleep(300)
            
@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    # 啟動發送每日挑戰的任務
    client.loop.create_task(send_daily_challenge())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 獲取當前時間
    now = datetime.datetime.now()
    current_hour = now.hour

    guild = message.guild
    
    # 如果訊息內容是 "抽"
    if message.content in ['抽', '抽e', '抽m', '抽h']:
        # 早上 2~6 強制休息
        if current_hour >= 2 and current_hour < 6:
            emoji = discord.utils.get(guild.emojis, name = 'ian_sleep_2')
            await message.channel.send(f"別再卷了，該睡覺囉~ {emoji}")
            return
        
        difficulty_map = {
            '抽e': 1,  # Easy
            '抽m': 2,  # Medium
            '抽h': 3   # Hard
        }
        difficulty = difficulty_map.get(message.content, None)
        question_data = get_random_leetcode_question(difficulty)
        
        if question_data:
            embed = create_leetcode_embed(question_data)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("抱歉，無法獲取題目。請稍後再試！")
    
    # 獲取每日挑戰命令
    elif message.content == '每日挑戰':
        daily_challenge = get_daily_leetcode_challenge()
        if daily_challenge:
            embed = create_leetcode_embed(daily_challenge, is_daily=True)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("抱歉，無法獲取每日挑戰。請稍後再試！")
    
    # 手動發送每日挑戰到指定頻道
    elif message.content == '發送每日挑戰':
        if message.author.guild_permissions.administrator:  # 只有管理員可以執行
            daily_challenge = get_daily_leetcode_challenge()
            if daily_challenge:
                embed = create_leetcode_embed(daily_challenge, is_daily=True)
                channel = client.get_channel(DAILY_CHALLENGE_CHANNEL_ID)
                if channel:
                    await channel.send(embed=embed)
                    await message.channel.send(f"已成功發送每日挑戰到 <#{DAILY_CHALLENGE_CHANNEL_ID}>")
                else:
                    await message.channel.send(f"找不到指定的頻道 {DAILY_CHALLENGE_CHANNEL_ID}")
            else:
                await message.channel.send("抱歉，無法獲取每日挑戰。請稍後再試！")
        else:
            await message.channel.send("只有管理員可以使用此命令")

# 請替換為你自己的 Discord Bot Token
client.run('您的機器人Token')
