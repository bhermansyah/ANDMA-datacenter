import logging
import weakref
import gc

from django.db import models, connection, transaction

signalnames = [
    'class_prepared',
    'm2m_changed',
    'post_delete',
    'post_init',
    'post_save',
    'post_syncdb',
    'pre_delete',
    'pre_init',
    'pre_save',
]
signals_store = {}

id_none = id(None)

logger = logging.getLogger("geonode.utils")

def id_to_obj(id_):
    if id_ == id_none:
        return None

    for obj in gc.get_objects():
        if id(obj) == id_:
            return obj
            break
    raise Exception("Not found")

def printsignals():
    for signalname in signalnames:
        logger.debug("SIGNALNAME: %s" % signalname)
        signaltype = getattr(models.signals, signalname)
        print 'signalname', signalname
        signals = signaltype.receivers[:]
        for signal in signals:
            print signal
            logger.debug(signal)

def designals():
    global signals_store

    for signalname in signalnames:
        # if signalname in signals_store:
        # print signalname
        try:
            signaltype = getattr(models.signals, signalname)
        except BaseException:
            continue
        logger.debug("RETRIEVE: %s: %d" %
                        (signalname, len(signaltype.receivers)))
        signals_store[signalname] = []
        signals = signaltype.receivers[:]
        for signal in signals:
            uid = receiv_call = None
            sender_ista = sender_call = None
            # first tuple element:
            # - case (id(instance), id(method))
            if not isinstance(signal[0], tuple):
                raise "Malformed signal"

            lookup = signal[0]

            if isinstance(lookup[0], tuple):
                # receiv_ista = id_to_obj(lookup[0][0])
                receiv_call = id_to_obj(lookup[0][1])
            else:
                # - case id(function) or uid
                try:
                    receiv_call = id_to_obj(lookup[0])
                except BaseException:
                    uid = lookup[0]

            if isinstance(lookup[1], tuple):
                sender_call = id_to_obj(lookup[1][0])
                sender_ista = id_to_obj(lookup[1][1])
            else:
                sender_ista = id_to_obj(lookup[1])

            # second tuple element
            if (isinstance(signal[1], weakref.ReferenceType)):
                is_weak = True
                receiv_call = signal[1]()
            else:
                is_weak = False
                receiv_call = signal[1]

            signals_store[signalname].append({
                'uid': uid, 'is_weak': is_weak,
                'sender_ista': sender_ista, 'sender_call': sender_call,
                'receiv_call': receiv_call,
            })

            signaltype.disconnect(
                receiver=receiv_call,
                sender=sender_ista,
                weak=is_weak,
                dispatch_uid=uid)


def resignals():
    global signals_store

    for signalname in signalnames:
        if signalname in signals_store:
            # print signalname
            signals = signals_store[signalname]
            signaltype = getattr(models.signals, signalname)
            for signal in signals:
                try:
                    signaltype.connect(
                        receiver=signal['receiv_call'],
                        sender=signal['sender_ista'],
                        weak=signal['is_weak'],
                        dispatch_uid=signal['uid'])
                except BaseException as identifier:
                    print 'Error reactivate signal (%s): %s\nsignal_store: %s' % (signalname, identifier, signal)
                    print 'Restart Django/Apache to restore signals'
                    continue
