from .Comment import Comment
import json

class Post:
    def __init__(self, host_reddit: str, upvote_count: int, comment_count: int, post_title: str, post_id: str, author_id: str, post_date: str):
        self.host_reddit: str = host_reddit
        self.id: str = post_id
        self.title: str = post_title
        self.content: str = ''
        self.upvotes: int = upvote_count
        self.comments: int = comment_count
        self.author_id: str = author_id
        self.date: str = post_date
        self.top_comments: list[Comment] = []

    def __str__(self):
        return f'{self.title} - {self.upvotes} upvotes - {self.comments} comments\n' \
               f'Posted on: {self.date} by [{self.author_id}] - POST ID: {self.id}'
    
    def to_dict(self):
        return {
            'host_reddit': self.host_reddit,
            'id': self.id,
            'title': self.title,
            'content': self.content.replace("\u2019", "'"),
            'upvotes': self.upvotes,
            'comments': self.comments,
            'author_id': self.author_id,
            'date': self.date,
            'top_comments': [comment.to_dict() for comment in self.top_comments]
        }
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)
