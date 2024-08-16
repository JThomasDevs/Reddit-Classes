import os
from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementLostError, NoRectError
from .Post import Post
from .Comment import Comment

class RedditHarvester:
    valid_timeframes = ['hour', 'day', 'week', 'month', 'year', 'all']

    def __init__(self, target='popular', timeframe='day', data_dir=os.path.join(os.getcwd(), 'data')):
        self.target = target
        if timeframe not in self.valid_timeframes:
            raise ValueError(f'Invalid timeframe: {timeframe}. Valid timeframes are: {self.valid_timeframes}')
        self.timeframe = timeframe
        self.data_dir = data_dir

    def _get_post_ids(self, dir=None):
        if dir is None:
            dir = self.data_dir
        data_dir = os.path.join(os.getcwd(), dir, self.target)
        for file in os.listdir(data_dir):
            yield file.replace('.json', '')

    def gather_n_posts(self, n: int = 50, close_on_finish: bool = True) -> list[Post]:
        url = f'https://www.reddit.com/r/{self.target}/top/?t={self.timeframe}'
        page = ChromiumPage()
        page.set.window.mini()
        print('Browser started')
        page.get(url)
        print('Page loaded\n')
        page.scroll.to_bottom()
        page.wait.eles_loaded('tag:faceplate-batch') # Container for posts beyond the top 3-7

        post_objs = []
        post_ids = set(self._get_post_ids())
        done = False
        print('Gathering posts...')
        total = 0
        while not done:
            posts = page.eles('tag:shreddit-post', timeout=10)
            for post in posts:
                upvotes = int(post.attr('score'))
                post_id = post.attr('id')[3:]
                if post_id in post_ids: # Prevent duplicates
                    continue
                else:
                    post_ids.add(post_id)
                href = post.ele('@slot=full-post-link').attr('href')
                comments = int(post.attr('comment-count'))
                title = post.attr('post-title')
                author_id = post.attr('author-id')
                if author_id is not None: # If an author deletes their account, the author-id attribute is None
                    author_id = author_id[3:]
                else:
                    author_id = 'deleted'
                date = post.attr('created-timestamp')[:10]
                post_obj = Post(self.target, post_id, title, href, upvotes, comments, author_id, date)
                if len(post_objs) == n:
                    done = True
                else:
                    post_objs.append(post_obj)
            if total < len(post_objs): # Prevent console spam and needless reassignment
                total = len(post_objs)
                print(f'Gathered {total} posts so far\n')
                print('Scrolling to bottom...') if not done else print('Done gathering posts\n')
            if done:
                continue
            else:
                page.scroll.to_bottom()
                page.wait(0.2)

        if close_on_finish or len(post_objs) == 0:
            page.quit()
        return post_objs

    def gather_threshold_posts(self, threshold: int = 1000, close_on_finish: bool = True) -> list[Post]:
        url = f'https://www.reddit.com/r/{self.target}/top/?t={self.timeframe}'
        page = ChromiumPage()
        page.set.window.mini()
        print('Browser started')
        page.get(url)
        print('Page loaded\n')
        page.scroll.to_bottom()
        page.wait.eles_loaded('tag:faceplate-batch') # Container for posts beyond the top 3-7

        post_objs = []
        post_ids = set(self._get_post_ids())
        done = False
        print('Gathering posts...')
        total = 0
        while not done:
            posts = page.eles('tag:shreddit-post', timeout=10)
            for post in posts:
                upvotes = int(post.attr('score'))
                if upvotes < threshold:
                    done = True
                    break
                post_id = post.attr('id')[3:]
                if post_id in post_ids: # Prevent duplicates
                    continue
                else: 
                    post_ids.add(post_id)
                href = post.ele('@slot=full-post-link').attr('href')
                comments = int(post.attr('comment-count'))
                title = post.attr('post-title')
                author_id = post.attr('author-id')
                author_id = author_id[3:] if author_id is not None else 'deleted'
                date = post.attr('created-timestamp')[:10]
                post_obj = Post(self.target, post_id, title, href, upvotes, comments, author_id, date)
                post_objs.append(post_obj)
            if total < len(post_objs):
                total = len(post_objs)
                print(f'Gathered {total} posts so far\n')
                print('Scrolling to bottom...') if not done else print(f'Done gathering {total} posts\n')
                page.scroll.to_bottom()
                page.wait(0.2)
            if done:
                continue

        if close_on_finish:
            page.quit()
        return post_objs
    
    def harvest_threshold_comments(self, post: Post, threshold: int = 1000, close_on_finish: bool = True):
        url = f'{post.href}?sort=top'
        page = ChromiumPage()
        page.set.window.mini()
        page.get(url)
        page.wait.doc_loaded()

        post_container = page.ele('tag:shreddit-post').ele('@slot=text-body')
        post.content = '\n\n'.join([p.text for p in post_container.eles('tag:p')])

        page.scroll.to_bottom()
        print(f'Harvesting comments above {threshold} upvotes for post: {post.id}')
        page.wait.eles_loaded('@@tag:shreddit-comment-tree@@id=comment-tree', timeout=5)

        comment_objs = []
        comment_ids = []
        done = False
        total = 0
        comments = []
        while not done:
            comments.clear()
            comments = [ele for ele in page.eles('tag:shreddit-comment') if ele.attr('depth') == '0' and ele.attr('thingid')[3:] not in comment_ids]
            if len(comments) == 0:
                continue
            if comments[0].attr('score') is None:
                break
            elif int(comments[0].attr('score')) < threshold:
                done = True
            else:
                print(f'{len(comments)} new comments found this cycle')
            for comment in comments:
                if not comment.ele('@slot=comment'): # Skip comments removed my moderators
                    continue
                upvotes = comment.attr('score')
                if upvotes is not None: # Deleted comments' upvotes are None
                    upvotes = int(comment.attr('score'))
                else:
                    continue
                if upvotes < threshold:
                    done = True
                    break
                parent = post.id
                comment_id = comment.attr('thingid')[3:]
                comment_ids.append(comment_id)
                depth = int(comment.attr('depth'))
                author_id = comment.ele('tag:shreddit-comment-action-row').ele('tag:shreddit-overflow-menu').attr('author-id')
                author_id = author_id[3:] if author_id is not None else 'deleted'
                text = '\n\n'.join([p.text for p in comment.ele('@slot=comment').eles('tag:p')])
                comment_obj = Comment(parent, comment_id, depth, author_id, upvotes, text)
                comment_objs.append(comment_obj)
            if total < len(comment_objs):
                total = len(comment_objs)
                print(f'\nHarvested {total} comments so far')
                page.scroll.to_see(page.ele('@noun=load_more_comments'))
                try:
                    page.ele('@noun=load_more_comments').click() # load more comments
                except ElementLostError:
                    print('Element lost error')
                    break
                except NoRectError:
                    print('No rect error')
                    break
            if done:
                print('\nDone harvesting comments')
                print(f'Harvested {total} comments above {threshold} upvotes for post: {post.id}\n')
                continue
        if close_on_finish:
            page.quit()
        post.top_comments = comment_objs
        return comment_objs

    def write_posts(self, posts: list[Post], path: str = '.'):
        for post in posts:
            if post.content == '' or post.top_comments == []:
                continue
            post_id = post.id
            parent = post.host_reddit
            post = post.to_json()
            directory = f'{path}/{parent}'
            filename = f'{directory}/{post_id}.json'
            # Create path if it does not exist
            os.makedirs(directory, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(post)
            print(f'Post {post_id} written to {filename}')
