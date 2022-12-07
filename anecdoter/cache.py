from collections import OrderedDict

from aiogram.contrib.fsm_storage.memory import MemoryStorage
import typing

from anecdoter.consts import SIZE_OF_CASH, END_WARNING, \
    NEEDLESS_KEYS
from anecdoter.contoller import Combiner, RatingFill
from anecdoter.tools import dic_shortener


class Cache(MemoryStorage):
    def __init__(self):
        super().__init__()
        self.data = OrderedDict()

    def check_cache_dict_fill(self):
        """
            Push to db first user cache when SIZE_OF_CASH full.
        """
        if len(self.data) == SIZE_OF_CASH:
            user_cache = self.data.popitem(last=False)
            self._drop_cache_to_db(user_cache[1])

    def drop_all_cache_to_db(self):
        users_cache = self.data
        if not users_cache:
            return 'Nothing_to_drop_cache_is_empty'
        try:
            for num, user_cache in enumerate(users_cache.values()):
                self._drop_cache_to_db(user_cache)
            return f'Dropped_cache_of_{num + 1}_users'
        except Exception as e:
            return f'Fail because {e}'

    @staticmethod
    def _drop_cache_to_db(user_cache):
        combiner = Combiner(**dic_shortener(user_cache.items(),
                                            NEEDLESS_KEYS))
        combiner.sync_db(change_word=True)

    def set_user_grade(self, uid, message):
        user_cache = self.get_user_cache(uid)

        rating = RatingFill(word=user_cache['word'],
                            joke=user_cache['joke'],
                            grade=len(message))
        rating.update_db()

    def last_user_word_function(self, user_data):
        """
            Run joke generator.
            Create new user_cache and recall himself when generator is over.
         """
        if not user_data['jokes_len']:
            # by the word bot doesn`t find any joke, clear the user cache
            # self.data[uid] = {}
            user_data = {}
            return
        try:
            joke = next(user_data['word_f'])
            user_data['joke_index'] += 1
            user_data['joke'] = joke
        except StopIteration:
            # jump on new page
            print('except StopIteration')
            user_data['page_num'] += 1
            # reset because new page
            user_data['joke_index'] = 0
            if user_data['page_num'] <= user_data['amount_pages']:
                print("if user_data['page_num'] <= user_data['amount_pages']:")
                self.set_data(data=dict(user_data=user_data))
                # recursion!
                self.get_data()
            else:
                # jokes ends case
                user_data['page_num'] = 1
                # joke = self.last_user_word_function(uid)
                # joke = END_WARNING + '\n' + '\n' + joke
                self.set_data(data=dict(user_data=user_data))
                # recursion!
                self.get_data()
        # todo add warning when jokes over

        return joke

    @staticmethod
    def process_joke_coordinate(uid, input_word, user_data, old_data):
        if user_data:
            # recall from last_user_word_function when jokes over on page
            # start parser with updated joke_index and page_num
            user_data = dic_shortener(user_data.items(), NEEDLESS_KEYS)
            combiner = Combiner(uid=uid, **user_data)
            combiner.run_parser()
            user_data['word_f'] = combiner.jokefunc()
            return user_data
        print("exists_data -- ", old_data)
        if not old_data:
            # create or read db record
            combiner = Combiner(uid=uid, word=input_word)
            combiner.sync_db()
        else:
            # new word from user
            # save joke_index and page_num old word to db
            old_data = dic_shortener(old_data.items(), NEEDLESS_KEYS)
            combiner = Combiner(uid=uid, **old_data)
            combiner.sync_db(change_word=True)
            # start parser and add new word to db
            combiner = Combiner(uid=uid, word=input_word)
            combiner.sync_db()
        user_data.update(dic_shortener(combiner.__dict__.items(),
                                       ('jokes', 'joke', 'uid')))
        user_data['word_f'] = combiner.jokefunc()
        return user_data

    async def set_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       data: typing.Dict = None):
        """
            Rewrite set_data from basic class MemoryStorage
            deepcope don`t take gen func as arg
        """
        if not data:
            return
        print(f'chat {chat}, user {user}')
        chat, user = self.resolve_address(chat=chat, user=user)
        self.check_cache_dict_fill()
        input_word = data.get('word', None)
        user_data = data.get('user_data', {}) if not input_word else {}
        old_data = self.data[chat][user].get('data', {}) \
            if not user_data else None
        # temporary measure in db chat_id int field
        user_data = self.process_joke_coordinate(uid=int(user),
                                                 input_word=input_word,
                                                 user_data=user_data,
                                                 old_data=old_data)

        '''
        if user_data:
            # recall from last_user_word_function when jokes over on page
            # start parser with updated joke_index and page_num
            user_data = dic_shortener(user_data.items(), NEEDLESS_KEYS)
            combiner = Combiner(uid=int_user, **user_data)
            combiner.run_parser()
            user_data['word_f'] = combiner.jokefunc()
            self.data[chat][user]['data'] = user_data
            return
        exists_data = self.data[chat][user].get('data', {})
        print("exists_data -- ", exists_data)
        if not exists_data:
            # create or read db record
            combiner = Combiner(uid=int_user, word=input_word)
            combiner.sync_db()
        else:
            # new word from user
            # save joke_index and page_num old word to db
            exists_data = dic_shortener(exists_data.items(), NEEDLESS_KEYS)
            combiner = Combiner(uid=int_user, **exists_data)
            combiner.sync_db(change_word=True)
            # start parser and add new word to db
            combiner = Combiner(uid=int_user, word=data['word'])
            combiner.sync_db()
        user_data.update(dic_shortener(combiner.__dict__.items(),
                                       ('jokes', 'joke', 'uid')))
        user_data['word_f'] = combiner.jokefunc()
        '''
        self.data[chat][user]['data'] = user_data
        self._cleanup(chat, user)

    async def get_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       default: typing.Optional[str] = None):
        """
            Rewrite get_data from basic class MemoryStorage
            deepcope don`t take gen func as arg
        """
        chat, user = self.resolve_address(chat=chat, user=user)
        # get next joke and update counter

        # return self.last_user_word_function(self.data[chat][user]['data'])
        return self.data[chat][user]['data']


cache = Cache()
