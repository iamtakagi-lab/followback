import logging
import asyncio
import tweepy
import os
from aiohttp import ClientSession
from discord import AsyncWebhookAdapter, Webhook

logger = logging.getLogger("followback")
format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=format)

TWITTER_CK = os.environ["TWITTER_CK"]
TWITTER_CS = os.environ["TWITTER_CS"]
TWITTER_AT = os.environ["TWITTER_AT"]
TWITTER_ATS = os.environ["TWITTER_ATS"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

auth = tweepy.OAuthHandler(TWITTER_CK, TWITTER_CS)
auth.set_access_token(TWITTER_AT, TWITTER_ATS)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def cursor_gen(cursor):
    while True:
        yield cursor.next()


def output_log(user, me):
    logger.info(f'@{user.screen_name} をフォローバックしました')
    logger.info(f'現在のフォロワー数: {me.followers_count}')
    logger.info(f'現在のフォロイー数: {me.friends_count}')


async def post_discord_webhook(user, me):
    async with ClientSession(raise_for_status=True) as session:
        webhook = Webhook.from_url(
            DISCORD_WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))

        await webhook.send(
            content=f'@{user.screen_name} をフォローバックしました\n現在のフォロワー数: {me.followers_count} / 現在のフォロイー数: {me.friends_count}\nhttps://twitter.com/{user.screen_name}'
        )


async def handle():
    for follower in cursor_gen(tweepy.Cursor(api.followers).items()):
        me = api.me()
        friends = api.friends_ids(me.id)
        if follower.id != me.id:
            if not follower.id in friends and not follower.protected:  # 鍵垢は無視
                follower.follow()
                output_log(follower, me)
                await post_discord_webhook(follower, me)
                await asyncio.sleep(5)  # 毎回5秒待機


async def main():
    logger.info('開始中...')
    await handle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
