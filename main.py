import os
from dotenv import load_dotenv
from autogen import ConversableAgent, LLMConfig, GroupChat, GroupChatManager, register_function, UserProxyAgent
from reddit_client import RedditClient

coordinator_message = """You are a social media project coordinator.
You manage the workflow between research, strategy, content adaptation, and posting teams.
Your responsibilities:
- Direct researchers to gather data from specific subreddits
- Ensure content strategists have the data they need
- Guide content adapters to create viral-ready posts
- Coordinate with posting agent for human approval workflow
- Coordinate the overall project timeline
- Summarize final deliverables

The workflow should be: Research -> Strategy -> Content Adaptation -> Human Approval -> Posting
When posting is complete with human approval, output "PROJECT COMPLETE!" """

researcher_message = """You are a Reddit research specialist.
Your job is to analyze trending topics and community culture on Reddit.
When asked to research subreddits, use your Reddit tools to:
- Fetch trending posts from specified subreddits
- Identify key themes and engagement patterns
- Summarize what content performs well

Always provide data-driven insights based on real Reddit data."""

strategist_message = """You are a social media content strategist.
You create actionable content strategies based on trending data.
When provided with Reddit research, analyze it to suggest:
- Specific content ideas based on trending topics
- Optimal posting strategies for each community
- Community-specific content adaptations
- Engagement optimization tactics

Make all recommendations specific and actionable."""

adapter_message = """You are a content adaptation agent that creates a single viral-ready post based on research data.
Your job is to take trending Reddit data and research insights and create actual post designed to trend.
You should:
- Analyze what makes content viral on each platform/subreddit
- Create specific post content (titles, body text, hashtags) optimized for engagement
- Adapt messaging to match the tone and style of each community
- Focus on creating posts that will generate discussion and shares

Always create concrete, ready-to-post content rather than just suggestions."""

poster_message = """You are a Reddit posting agent with human-in-the-loop approval.
Your responsibilities:
- Present finalized posts to humans for approval before posting
- Handle the technical posting process once approved
- Track posting results and engagement
- NEVER post content without explicit human approval
- AUTOMATICALLY choose the most appropriate flair when posting

WORKFLOW:
1. When you receive posts to publish, first use get_available_flairs to check what flairs are available
2. Analyze the post content and automatically select the most appropriate flair based on:
   - Post topic/subject matter
   - Content type and purpose
3. Present the post clearly with: title, content, target subreddit, and your selected flair
4. Ask the human: "Should I post this to r/[subreddit] with flair '[selected_flair]'? (yes/no/modify)"
5. If they say yes/approve/post/go ahead, immediately use the post_to_reddit function with the pre-selected flair
6. If they say no/reject, acknowledge and don't post
7. If they ask for modifications, wait for the updated content

Only ask for input ONCE per post for approval. After approval, post immediately without asking again."""

load_dotenv()

if not os.getenv("GOOGLE_GEMINI_API_KEY"):
    print("Please set GOOGLE_GEMINI_API_KEY environment variable")
    exit(1)

# Configure for Google Gemini
llm_config = LLMConfig(api_type="google", model="gemini-2.5-flash")

reddit_client = RedditClient()


# Create agents with Gemini configuration
research_agent = ConversableAgent(
    name="research_agent",
    system_message=researcher_message,
    llm_config=llm_config,
)

content_strategist = ConversableAgent(
    name="content_strategist", 
    system_message=strategist_message,
    llm_config=llm_config,
)

adapter = ConversableAgent(
    name="content_adapter",
    system_message=adapter_message,
    llm_config=llm_config,
)

poster = ConversableAgent(
    name="reddit_poster",
    system_message=poster_message,
    llm_config=llm_config,
)

coordinator = ConversableAgent(
    name="project_coordinator",
    system_message=coordinator_message,
    llm_config=llm_config,
    is_termination_msg=lambda x: "PROJECT COMPLETE!" in (x.get("content", "") or "").upper(),
)

human = UserProxyAgent(
    name="human",
    human_input_mode="ALWAYS",
    code_execution_config=False,
    description="Human approval agent for post reviews and decisions."
)


def get_trending_posts_wrapper(subreddit_name: str, limit: int = 5, filter: str = "hot"):
    try:
        posts = reddit_client.get_trending_posts(subreddit_name, min(limit, 5), filter)
        if not posts:
            return f"No posts found for r/{subreddit_name}"
        
        result = f"Trending posts from r/{subreddit_name} ({filter}):\n\n"
        for i, post in enumerate(posts, 1):
            result += f"{i}. {post.title}\n"
            result += f"   Score: {post.score} | Comments: {post.num_comments} | Ratio: {post.upvote_ratio}\n"
            result += f"   Body: {post.content}\n"
            result += f"   Author: {post.author}\n\n"
        return result
    except Exception as e:
        return f"Error fetching posts from r/{subreddit_name}: {str(e)}"

def get_available_flairs(subreddit_name: str) -> str:
    try:
        flairs = reddit_client.get_available_flairs(subreddit_name)
        if not flairs:
            return f"No flairs available for r/{subreddit_name}"
        
        output = f"Available flairs for r/{subreddit_name}:\n"
        for flair in flairs:
            output += f"- '{flair['text']}' (editable: {flair['editable']})\n"

        return output
    except Exception as e:
        return f"Error fetching flairs for r/{subreddit_name}: {str(e)}"

def post_to_reddit(subreddit_name: str, title: str, content: str, post_type: str = "text", 
                   flair_type: str = None) -> str:
    try:
        flair_id = None
        if flair_type:
            available_flairs = reddit_client.get_available_flairs(subreddit_name)
            for flair in available_flairs:
                if flair["text"].lower() == flair_type.lower():
                    flair_id = flair["id"]
                    break
                
                if not flair_id:
                    return f"Failed to post to r/{subreddit_name}: Flair '{flair_type}' not found. Available flairs: {[f['text'] for f in available_flairs]}"
        
        result = reddit_client.post_to_subreddit(subreddit_name, title, content, post_type, flair_id=flair_id)
        
        if result["status"] == "success":
            return f"Successfully posted to r/{subreddit_name}!\n" + \
                   f"Post URL: {result['post_url']}\n" + \
                   f"Post ID: {result['post_id']}\n" + \
                   f"Monitor engagement at: {result['post_url']}"
        else:
            return f"Failed to post to r/{subreddit_name}: {result['message']}"
    
    except Exception as e:
        return f"Error posting to r/{subreddit_name}: {str(e)}"

# trending_data = reddit_client.get_trending_posts("AutoGenAI", limit=5)
register_function(
    # reddit_client.get_trending_posts
    get_trending_posts_wrapper,
    caller=research_agent,
    executor=research_agent,
    description="Get trending posts from ONE subreddit. Use subreddit name without r/ prefix (e.g., 'technology' not 'r/technology'). Valid time_filters: 'hot', 'new', 'top', 'rising', 'best'."
)

register_function(
    get_available_flairs,
    caller=poster,
    executor=poster,
    description="Get list of available flairs for a subreddit. Use subreddit name without r/ prefix"
)

register_function(
    post_to_reddit,
    caller=poster,
    executor=poster,
    description="Post content to Reddit after human approval. Requires subreddit_name (without r/ prefix), title, content, post_type ('text' or 'link'), and optional flair_type (exact text match of available flair)"
)

# Create GroupChat
groupchat = GroupChat(
    agents=[coordinator, research_agent, content_strategist, adapter, poster, human],
    speaker_selection_method="auto",
    messages=[],
    max_round=20
)

# Create GroupChatManager
manager = GroupChatManager(
    name="social_orchestration_manager",
    groupchat=groupchat,
    llm_config=llm_config,
)

def main():
    with llm_config:
        coordinator.initiate_chat(
            recipient=manager,
            message="""Today we need to analyze Reddit trends for content strategy.
            Our target communities is r/LLM
            Let's gather trending data and create actionable content strategies for the community.
            To make a viral post."""
        )

if __name__ == "__main__":
    main()