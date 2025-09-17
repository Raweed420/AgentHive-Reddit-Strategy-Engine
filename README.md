# AgentHive — Reddit Strategy Engine

AgentHive is a Python-based multi-agent system built with AutoGen (AG2) that automates the entire Reddit content strategy pipeline. Multiple coordinated agents research trending topics, craft actionable strategies, generate engaging posts, and handle the posting process with a human-in-the-loop approval step.

## Features

- **Research Agent**: Analyzes trending topics and community engagement patterns on Reddit
- **Content Strategist**: Creates actionable content strategies based on research data
- **Content Adapter**: Transforms strategies into viral-ready Reddit posts
- **Reddit Poster**: Handles posting with human-in-the-loop approval
- **Project Coordinator**: Manages the entire workflow between agents

## Prerequisites

- Python 3.12+
- Reddit API credentials
- Google Gemini API key
- Reddit account with posting permissions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ag2-demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with the following:
```bash
# Google Gemini API
GOOGLE_GEMINI_API_KEY=your_gemini_api_key

# Reddit API credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name/1.0
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

## Usage

Run the main script to start the multi-agent workflow:

```bash
python main.py
```

The system will:
1. Research trending posts in the target subreddit (default: r/LLM)
2. Develop content strategy based on the research
3. Create a viral-ready post
4. Request human approval before posting
5. Post to Reddit upon approval

## Project Structure

```
ag2-demo/
├── main.py              # Main application with agent definitions
├── reddit_client.py     # Reddit API client wrapper
├── requirements.txt     # Python dependencies
├── example.txt          # Sample execution output
└── .env                # Environment variables (create this)
```

## Configuration

The target subreddit can be modified in `main.py` by changing the message in the `main()` function:

```python
message="""Today we need to analyze Reddit trends for content strategy.
Our target communities is r/YOUR_SUBREDDIT
Let's gather trending data and create actionable content strategies for the community.
To make a viral post."""
```

## Dependencies

- `ag2[gemini]` - AutoGen framework with Google Gemini support
- `python-dotenv` - Environment variable management
- `praw` - Python Reddit API Wrapper

## How It Works

1. **Research Phase**: The research agent fetches trending posts from the specified subreddit
2. **Strategy Phase**: The content strategist analyzes the data and creates content recommendations
3. **Adaptation Phase**: The content adapter creates a specific, ready-to-post content piece
4. **Approval Phase**: The system presents the post to a human for approval
5. **Posting Phase**: Upon approval, the post is submitted to Reddit

## Example Output

The system successfully creates and posts content like the example shown in `example.txt`, which demonstrates a complete workflow resulting in a live Reddit post.

## License

This project is for demonstration purposes. Ensure compliance with Reddit's API terms and community guidelines when using.
