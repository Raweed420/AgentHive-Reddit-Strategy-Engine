import os
import praw
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TrendingPost:
    """Data class for trending Reddit posts"""
    id: str
    title: str
    score: int
    upvote_ratio: float
    num_comments: int
    url: str
    subreddit: str
    author: str
    created_utc: datetime
    content: Optional[str] = None

@dataclass
class Flair:
    """Data class for Reddit flairs"""
    id: str
    text: str
    editable: bool

    
class RedditClient:    
    def __init__(self):

        if not all([os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_CLIENT_SECRET")]):
            raise ValueError("Reddit API credentials not found in environment variables")

        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
    
    def get_trending_posts(self, subreddit_name: str, limit: int = 5, filter: str = "hot") -> List[TrendingPost]:
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            if filter == "hot":
                posts = subreddit.hot(limit=limit)
            elif filter == "new":
                posts = subreddit.new(limit=limit)
            elif filter == "top":
                posts = subreddit.top(time_filter="day", limit=limit)
            elif filter == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid filter: {filter}")
            
            trending_posts = []
            for post in posts:
               
                trending_post = TrendingPost(
                    id=post.id,
                    title=post.title,
                    score=post.score,
                    upvote_ratio=post.upvote_ratio,
                    num_comments=post.num_comments,
                    url=post.url,
                    subreddit=post.subreddit.display_name,
                    author=str(post.author) if post.author else "[deleted]",
                    created_utc=datetime.fromtimestamp(post.created_utc),
                    content=post.selftext if post.is_self else None
                )
                trending_posts.append(trending_post)
            
            return trending_posts
            
        except Exception as e:
            print(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
            return []

    def post_to_subreddit(self, subreddit_name: str, title: str, content: str, post_type: str = "text", 
                         flair_id: Optional[str] = None, flair_text: Optional[str] = None) -> Dict[str, str]:
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            submit_kwargs = {"title": title}
            
            if flair_id:
                submit_kwargs["flair_id"] = flair_id
                if flair_text:
                    submit_kwargs["flair_text"] = flair_text
            
            if post_type == "text":
                submit_kwargs["selftext"] = content
                submission = subreddit.submit(**submit_kwargs)
            elif post_type == "link":
                submit_kwargs["url"] = content
                submission = subreddit.submit(**submit_kwargs)
            
            return {
                "status": "success",
                "post_id": submission.id,
                "post_url": f"https://reddit.com{submission.permalink}",
                "message": f"Successfully posted to r/{subreddit_name}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error posting to r/{subreddit_name}: {str(e)}"
            }

    def get_available_flairs(self, subreddit_name: str) -> List[Flair]:
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            flair_templates = list(subreddit.flair.link_templates.user_selectable())
            
            flairs = []
            for template in flair_templates:
                flair = Flair(
                    id=template["flair_template_id"],
                    text=template["flair_text"],
                    editable=template["flair_text_editable"],
                )
                flairs.append(flair)
            
            return flairs
            
        except Exception as e:
            print(f"Error fetching flairs from r/{subreddit_name}: {str(e)}")
            return []
