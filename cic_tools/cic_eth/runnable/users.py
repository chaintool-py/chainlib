#!/usr/bin/python

# standard imports
import json
import time
import datetime
import random
import logging
import os
import base64
import hashlib
import sys
import uuid
import argparse

# third-party imports
import redis
import vobject
import celery
from faker import Faker
import cic_registry
import confini
from cic_eth.api import Api

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

fake = Faker(['sl', 'en_US', 'no', 'de', 'ro'])

#f = open('cic.conf', 'r')
#config = json.load(f)
#f.close()
#

default_config_dir = os.environ.get('CONFINI_DIR', '/usr/local/etc/cic')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-c', type=str, default=default_config_dir, help='config root to use')
argparser.add_argument('-q', type=str, default='cic-eth', help='Task queue')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, help='chain spec')
argparser.add_argument('--redis-host-callback', dest='redis_host_callback', default='localhost', type=str, help='redis host to use for callback')
argparser.add_argument('--redis-port-callback', dest='redis_port_callback', default=6379, type=int, help='redis port to use for callback')
argparser.add_argument('--timeout', default=1.0, type=int, help='timeout to wait for account create callback')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', help='be more verbose', action='store_true')
argparser.add_argument('count', help='Number of users to generate', type=int)
args = argparser.parse_args()

if args.v == True:
    logging.getLogger().setLevel(logging.INFO)
elif args.vv == True:
    logging.getLogger().setLevel(logging.DEBUG)

config_dir = os.path.join(args.c)
config = confini.Config(config_dir, os.environ.get('CONFINI_ENV_PREFIX'))
config.process()
args_override = {
        'ETH_PROVIDER': getattr(args, 'p'),
        'CIC_CHAIN_SPEC': getattr(args, 'i'),
}
config.dict_override(args_override, 'cli flag')
logg.debug('config loaded from {}:\n{}'.format(config_dir, config))


dt_now = datetime.datetime.utcnow()
dt_then = dt_now - datetime.timedelta(weeks=150)
ts_now = int(dt_now.timestamp())
ts_then = int(dt_then.timestamp())

queue = args.q

celery_app = celery.Celery(broker=config.get('CELERY_BROKER_URL'), backend=config.get('CELERY_RESULT_URL'))

redis_host = config.get('REDIS_HOST')
redis_port = config.get('REDIS_PORT')
redis_db = config.get('REDIS_DB')
redis_channel = str(uuid.uuid4())
r = redis.Redis(redis_host, redis_port, redis_db)
ps = r.pubsub()
ps.subscribe(redis_channel)
ps.get_message()

api = Api(
        config.get('CIC_CHAIN_SPEC'),
        queue=args.q,
        callback_param='{}:{}:{}:{}'.format(args.redis_host_callback, args.redis_port_callback, redis_db, redis_channel),
        callback_task='cic_eth.callbacks.redis.redis',
        callback_queue=queue,
        )

gift_max = 10000
gift_factor = (10**9)

user_count = args.count

categories = [
        "food/water",
        "fuel/energy",
        "education",
        "health",
        "shop",
        "environment",
        "transport",
        "farming/labor",
        "savingsgroup",
        ]

phone_idx = []


def genPhoneIndex(phone):
    h = hashlib.new('sha256')
    h.update(phone.encode('utf-8'))
    h.update(b'cic.msisdn')
    return h.digest().hex()


def genId(addr, typ):
    h = hashlib.new('sha256')
    h.update(bytes.fromhex(addr[2:]))
    h.update(typ.encode('utf-8'))
    return h.digest().hex()


def genDate():

    logg.info(ts_then)
    ts = random.randint(ts_then, ts_now)
    return datetime.datetime.fromtimestamp(ts).timestamp()


def genPhone():
    return fake.msisdn()


def genPersonal(phone):
    fn = fake.first_name()
    ln = fake.last_name()
    e = fake.email()

    v = vobject.vCard()
    first_name = fake.first_name()
    last_name = fake.last_name()
    v.add('n')
    v.n.value = vobject.vcard.Name(family=last_name, given=first_name)
    v.add('fn')
    v.fn.value = '{} {}'.format(first_name, last_name)
    v.add('tel')
    v.tel.typ_param = 'CELL'
    v.tel.value = phone
    v.add('email')
    v.email.value = fake.email()

    vcard_serialized = v.serialize()
    vcard_base64 = base64.b64encode(vcard_serialized.encode('utf-8'))

    return vcard_base64.decode('utf-8')


def genCats():
    i = random.randint(0, 3)
    return random.choices(categories, k=i)


def genAmount():
    return random.randint(0, gift_max) * gift_factor


def gen():
    old_blockchain_address = '0x' + os.urandom(20).hex()
    t = api.create_account(register=True)

    ps.get_message()
    m = ps.get_message(timeout=args.timeout)
    new_blockchain_address = json.loads(m['data'])
    
    #new_blockchain_address = t.get()
    gender = random.choice(['female', 'male', 'other'])
    phone = genPhone()
    v = genPersonal(phone)
    o = {
        'date_registered': genDate(),
        'vcard': v,
        'gender': gender,
        'key': {
            'ethereum': [
                old_blockchain_address,
                new_blockchain_address,
                ],
            },
        'location': {
            'latitude': str(fake.latitude()),
            'longitude': str(fake.longitude()),
            'external': { # add osm lookup
                }
            },
        'selling': genCats(),
            }
    uid = genId(new_blockchain_address, 'cic.person')

    return (uid, phone, o)


def prepareLocalFilePath(datadir, address):
    parts = [
                address[:2],
                address[2:4],
            ]
    dirs = '{}/{}/{}'.format(
            datadir,
            parts[0],
            parts[1],
            )
    os.makedirs(dirs, exist_ok=True)
    return dirs


if __name__ == '__main__':

    os.makedirs('data/person', exist_ok=True)
    os.makedirs('data/phone', exist_ok=True)

    fa = open('./data/amounts', 'w')
    fb = open('./data/addresses', 'w')

    #for i in range(10):
    for i in range(int(user_count)):
    
        (uid, phone, o) = gen()
        eth = o['key']['ethereum'][1]

        print(o)

        d = prepareLocalFilePath('./data/person', uid)
        f = open('{}/{}'.format(d, uid), 'w')
        json.dump(o, f)
        f.close()

        pidx = genPhoneIndex(phone)
        d = prepareLocalFilePath('./data/phone', uid)
        f = open('{}/{}'.format(d, pidx), 'w')
        f.write(eth)
        f.close()

        amount = genAmount()
        fa.write('{},{}\n'.format(eth,amount))
        fb.write('{}\n'.format(eth))
        logg.debug('pidx {}, uid {}, eth {}, amount {}'.format(pidx, uid, eth, amount))

    fb.close()
    fa.close()
