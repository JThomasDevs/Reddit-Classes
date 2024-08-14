class Comment:
    def __init__(self, parent_post: str, comment_id: str, depth: int, author_id: str, upvotes: int, comment_text: str):
        self.parent_post: str = parent_post
        self.id: str = comment_id
        self.depth: int = depth
        self.author_id: str = author_id
        self.upvotes: int = upvotes
        self.text: str = comment_text

    def __str__(self):
        return f'Comment on Post: {self.parent_post} by [{self.author_id}]\n' \
               f'{self.upvotes} upvotes - Depth: {self.depth} - COMMENT ID: {self.id}\n' \
               f'{self.text}'
    
    def to_dict(self):
        return {
            'parent_post': self.parent_post,
            'id': self.id,
            'depth': self.depth,
            'author_id': self.author_id,
            'upvotes': self.upvotes,
            'text': self.text.replace("\u2019", "'")
        }
