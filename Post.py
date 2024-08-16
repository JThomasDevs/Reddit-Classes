from .Comment import Comment
import json

class Post:
    def __init__(self, host_reddit: str, post_id: str, post_title: str, href: str, upvote_count: int, comment_count: int, author_id: str, post_date: str):
        self.host_reddit: str = host_reddit
        self.id: str = post_id
        self.title: str = post_title
        self.href: str = href
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
        unicode_replacements = {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u2026": "...",
            "\u00A0": " ",
            "\u00AD": "-",
            "\u2122": "(TM)",
            "\u00AE": "(R)",
            "\u00B0": "°"
        }

        def replace_unicode_symbols(text):
            for unicode_char, replacement in unicode_replacements.items():
                text = text.replace(unicode_char, replacement)
            return text
        
        return {
            'host_reddit': self.host_reddit,
            'id': self.id,
            'title': replace_unicode_symbols(self.title),
            'href': self.href,
            'content': replace_unicode_symbols(self.content),
            'upvotes': self.upvotes,
            'comments': self.comments,
            'author_id': self.author_id,
            'date': self.date,
            'top_comments': [comment.to_dict() for comment in self.top_comments]
        }
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
