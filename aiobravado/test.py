# -*- coding: utf-8 -*-
# import logging
# from asyncio import get_event_loop, Task, ensure_future, wait_for
# from asyncio import set_event_loop
# from asyncio import wait
# from asyncio import coroutine
# from asyncio import sleep as aiosleep
# from sys import stdout
#
# from time import sleep
# from inspect import currentframe, getargvalues
#
# from random import shuffle
#
# import uvloop
#
#
# def configure_loop():
#     set_event_loop(loop=uvloop.new_event_loop())
#
#
# @coroutine
# def sync_print(sleep_time):
#     args = getargvalues(currentframe())[3]
#     name = currentframe().f_code.co_name
#     print('start {} - {}'.format(name, args))
#     sleep(sleep_time)
#     print('end {} - {}'.format(name, args))
#
#
# async def async_print(sleep_time):
#     args = getargvalues(currentframe())[3]
#     name = currentframe().f_code.co_name
#     print('{} - start {} - {}'.format(get_event_loop().time(), name, args))
#     await aiosleep(sleep_time)
#     print('{} - end {} - {}'.format(get_event_loop().time(), name, args))
# #
# #
# # class Foo(object):
# #     def _inner_sleep(self, sleep_time):
# #         sleep(sleep_time)
# #
# #     def sleep(self, sleep_time):
# #         self._inner_sleep(sleep_time)
# #
# #     def sync_print(self, sleep_time):
# #         args = getargvalues(currentframe())[3]
# #         name = currentframe().f_code.co_name
# #         print('{} - start {} - {}'.format(get_event_loop().time(), name, args))
# #         self.sleep(sleep_time)
# #         print('{} - end {} - {}'.format(get_event_loop().time(), name, args))
#
#
# class AIOFoo():
#     @coroutine
#     async def _inner_sleep(self, sleep_time):
#         await ensure_future(aiosleep(sleep_time))
#         return 1
#
#     # @coroutine
#     def sleep(self, sleep_time):
#         # async def aa():
#         #     print('---', await ensure_future(self._inner_sleep(sleep_time)))
#         #     return await ensure_future(self._inner_sleep(sleep_time))
#         return wait_for(ensure_future(self._inner_sleep(sleep_time)), timeout=10, loop=get_event_loop())
#
#     def sync_print(self, sleep_time):
#         args = getargvalues(currentframe())[3]
#         name = currentframe().f_code.co_name
#         print('{} - start {} - {}'.format(get_event_loop().time(), name, args))
#         print(self.sleep(sleep_time))
#         print('{} - end {} - {}'.format(get_event_loop().time(), name, args))
#
#     # async def _inner_sleep(self, sleep_time):
#     #     return await aiosleep(sleep_time)
#     #
#     # async def sleep(self, sleep_time):
#     #     return await self._inner_sleep(sleep_time)
#     #
#     # async def sync_print(self, sleep_time):
#     #     args = getargvalues(currentframe())[3]
#     #     name = currentframe().f_code.co_name
#     #     print('{} - start {} - {}'.format(get_event_loop().time(), name, args))
#     #     await self.sleep(sleep_time)
#     #     print('{} - end {} - {}'.format(get_event_loop().time(), name, args))
#
#
# async def main():
#     foo = AIOFoo()
#     sleep_times = list(range(4))
#     shuffle(sleep_times)
#     print(get_event_loop().time())
#     print('{} - start {}'.format(get_event_loop().time(), currentframe().f_code.co_name))
#     tasks = [
#         foo.sync_print(sleep_time)
#         # ensure_future(async_print(sleep_time), loop=get_event_loop())
#         for sleep_time in sleep_times
#     ]
#     # await wait(tasks)
#     print('{} - end {}'.format(get_event_loop().time(), currentframe().f_code.co_name))
#     return tasks
#
#
# if __name__ == '__main__':
#     try:
#         configure_loop()
#         logging.getLogger('asyncio').addHandler(logging.StreamHandler())
#         logging.getLogger('asyncio').setLevel(logging.NOTSET)
#         get_event_loop().run_until_complete(main())
#     finally:
#         get_event_loop().close()
