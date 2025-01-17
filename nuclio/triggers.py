from os import environ


class NuclioTrigger:
    kind = ''

    def __init__(self, struct={}):
        self._struct = struct

    def to_dict(self):
        return self._struct

    def disable(self, disabled=True):
        self._struct['disabled'] = disabled
        return self

    def workers(self, workers=4):
        self._struct['maxWorkers'] = workers
        return self


class HttpTrigger(NuclioTrigger):
    kind = 'http'

    def __init__(self, workers=8, port=0,
                 host=None, paths=None, canary=None):
        self._struct = {
            'kind': self.kind,
            'maxWorkers': workers,
            'attributes': {'ingresses': {}},
            'annotations': {},
        }
        if port:
            self._struct['attributes']['port'] = port
        if host:
            self._ingress(host, paths, canary)

    def ingress(self, host, paths=None, canary=None, name='0'):
        return self._ingress(host, paths, canary, name)

    def _ingress(self, host, paths=None, canary=None, name='0'):
        if paths and not isinstance(paths, list):
            raise ValueError('paths must be a list of paths e.g. ["/x"]')
        if not paths:
            paths = ['/']
        if 'IGZ_NAMESPACE_DOMAIN' in environ:
            host = '{}.{}'.format(host, environ['IGZ_NAMESPACE_DOMAIN'])
        self._struct['attributes']['ingresses'][name] = {'host': host,
                                                         'paths': paths}
        if canary is not None:
            if not isinstance(canary, int) or canary > 100 or canary < 0:
                raise ValueError('canary must ve an int between 0 to 100')
            self._struct['annotations'][
                'nginx.ingress.kubernetes.io/canary'] = 'true'
            self._struct['annotations'][
                'nginx.ingress.kubernetes.io/canary-weight'] = str(host)
        return self


class CronTrigger(NuclioTrigger):
    kind = 'cron'

    def __init__(self, interval='', schedule='', body='', headers={}):
        self._struct = {
            'kind': self.kind,
            'attributes': {},
        }
        if interval:
            self._struct['attributes']['interval'] = interval
        elif schedule:
            self._struct['attributes']['schedule'] = schedule
        else:
            raise ValueError('interval or schedule must be specified')
        if body or headers:
            self._struct['attributes']['event'] = {'body': body,
                                                   'headers': headers}


class KafkaTrigger(NuclioTrigger):
    kind = 'kafka'

    def __init__(self, url, topic, partitions=[]):
        self._struct = {
            'kind': self.kind,
            'url': url,
            'attributes': {'topic': topic},
        }
        if partitions:
            self._struct['attributes']['partitions'] = partitions

    def sasl(self, user='', password=''):
        self._struct['attributes']['sasl'] = {'enable': True,
                                              'user': user,
                                              'password': password}
        return self
