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
            'parent_post': self.parent_post,
            'id': self.id,
            'depth': self.depth,
            'author_id': self.author_id,
            'upvotes': self.upvotes,
            'text': replace_unicode_symbols(self.text)
        }
