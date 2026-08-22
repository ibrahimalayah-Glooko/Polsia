from app.agents.base_agent import BasePolsiaAgent
from app.services.company_service import build_context_prompt


class SocialMediaAgent(BasePolsiaAgent):
    agent_type = "social_media"

    def run(self, task: dict, context: dict) -> dict:
        prompt = (
            f"You are the social media agent.\n{build_context_prompt(context)}\n\n"
            f"Task: {task.get('title')}\n{task.get('description') or ''}\n"
            "Draft a single tweet (280 characters max, no hashtags spam) promoting the company. "
            "Reply with the tweet text only."
        )
        draft = self.call_claude(prompt).strip().strip('"')[:280]

        from app.integrations.twitter_client import post_tweet

        post_result = post_tweet(draft)

        return {
            "summary": f"Drafted and {'posted' if not post_result['simulated'] else 'simulated'} a tweet: {draft}",
            "social_post": {
                "platform": "twitter",
                "content": draft,
                "status": "draft" if post_result["simulated"] else "published",
                "tweet_id": post_result["tweet_id"],
            },
        }
