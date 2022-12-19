from collections import OrderedDict

from aiogram.contrib.fsm_storage.memory import MemoryStorage
import typing

from anecdoter.consts import SIZE_OF_CASH
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
                data = (tuple(user_cache.values()))[0]['data']
                uid = int((tuple(user_cache.keys()))[0])
                self._drop_cache_to_db(uid, data)
            return f'Dropped_cache_of_{num + 1}_users'
        except Exception as e:
            return f'Fail because {e}'

    @staticmethod
    def _drop_cache_to_db(uid, user_cache):
        combiner = Combiner(uid=uid, **dic_shortener(user_cache.items(),
                                                     ('word_f', 'joke')))
        combiner.sync_db(change_word=True)

    @staticmethod
    def process_joke_coordinate(uid, input_word, user_data, old_data, username):
        if user_data:
            # call from process_user_joke when jokes over on page
            # start parser with updated joke_index and page_num
            user_data = dic_shortener(user_data.items(), ('word_f', 'joke'))
            combiner = Combiner(uid=uid, username=username, **user_data)
            combiner.run_parser()
            user_data['word_f'] = combiner.jokefunc()
            return user_data
        if not old_data:
            # create or read db record
            combiner = Combiner(uid=uid, username=username, word=input_word)
            combiner.sync_db()
        else:
            # new word from user
            # save joke_index and page_num old word to db
            old_data = dic_shortener(old_data.items(), ('word_f', 'joke'))
            combiner = Combiner(uid=uid, **old_data)
            combiner.sync_db(change_word=True)
            # start parser and add new word to db
            combiner = Combiner(uid=uid, username=username, word=input_word)
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
        uid = user
        chat, user = self.resolve_address(chat=chat, user=user)
        self.check_cache_dict_fill()
        username = data.get('username', None)
        input_word = data.get('word', None)
        user_data = data.get('user_data', {}) if not input_word else {}
        old_data = self.data[chat][user].get('data', {}) \
            if not user_data else None
        user_data = self.process_joke_coordinate(uid=uid,
                                                 input_word=input_word,
                                                 user_data=user_data,
                                                 old_data=old_data,
                                                 username=username)
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
        return self.data[chat][user]['data']


cache = Cache()
