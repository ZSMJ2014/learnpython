import orm,asyncio
from models import User,Blog,Comment
def test(loop):
    yield from orm.create_pool(loop,user='www-data',password='www-data',db='awesome')
    u=User(name='Test',email='12@12.com',passwd='123456',image='about:blank')
    yield from u.save()
loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
