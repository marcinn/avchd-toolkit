AVAILABLE_TAGS = (
        ('reel', 'Reel ID'),
        ('shot', 'Shot'),
        ('scene', 'Scene'),
        ('comments', 'Comments'),
    )


class UnsupportedMetaTag(KeyError):
    pass


class MetaTagInfo(object):
    def __init__(self, key, name=None, raw_key=None):
        self.key = key
        self.name = name or key
        self.raw_key = raw_key

    @classmethod
    def factory(cls, key):
        try:
            name = dict(AVAILABLE_TAGS)[key]
        except KeyError:
            raise UnsupportedMetaTag(key)
        else:
            return cls(key, name)


class MetaDataHandler(object):
    tagsmap = {
            'reel': 'comment_TapeID',
            'scene': 'comment_Scene',
            'shot': 'comment_Take',
            'comments': 'comment_Comments',
            }

    def set_tags(self, container, tags_dict):
        for tag, value in tags_dict.items():
            self.set_tag(container, tag, value)

    def set_tag(self, container, tag, value):
        self._do_write_tag(container, self.raw_key(tag), value, False)
        if tag=='reel':
            self._do_write_tag(container, 'reel_name', value, True)

    def raw_key(self, key):
        return self.tagsmap[key]

    def _do_write_tag(self, container, dest_name, value, to_stream):
        if to_stream:
            for video in container.videos:
                video.meta[dest_name]=value
        else:
            container.meta[dest_name]=value


def metadatahandler_factory(profile):
    return MetaDataHandler()


