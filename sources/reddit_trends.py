import praw
import pandas as pd
from datetime import datetime
import logging
from config.settings import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT
)

logger = logging.getLogger(__name__)

class RedditTrendSource:

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def get_trending_posts(self, subreddits=None, limit=20):
        if subreddits is None:
            subreddits = ["technology", "marketing", "business"]

        try:
            posts_data = []
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            for sub in subreddits:
                subreddit = self.reddit.subreddit(sub)

                for post in subreddit.hot(limit=limit):
                    if post.stickied:  # ← filtrar posts fijados
                        continue

                    posts_data.append({
                        "trend": post.title,
                        "score": post.score,
                        "comments": post.num_comments,
                        "region": sub,
                        "date": current_time,
                        "source": "reddit"
                    })

            return pd.DataFrame(posts_data)

        except Exception as e:
            logger.error(f"Error obteniendo tendencias Reddit: {e}")
            return pd.DataFrame(
                columns=["trend", "score", "comments", "region", "date", "source"]
            )