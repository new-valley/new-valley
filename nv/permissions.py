from sqlalchemy.orm import class_mapper
import sqlalchemy


def _get_attributes(cls):
    return {prop.key for prop in class_mapper(cls).iterate_properties
        if isinstance(prop, sqlalchemy.orm.ColumnProperty)}


def _get_roles(user):
    return {r.strip() for r in user.roles.split(',') if r.strip()}


def _is_active(user):
    return user is not None and user.status == 'active'


def _is_admin(user):
    return user is not None and 'admin' in _get_roles(user)


def _is_active_admin(user):
    return _is_active(user) and _is_admin(user)


def _is_moderator(user):
    return user is not None and 'moderator' in _get_roles(user)


def _is_active_moderator(user):
    return _is_active(user) and _is_moderator(user)


def _is_admin_or_moderator(user):
    return _is_admin(user) or _is_moderator(user)


def _is_active_admin_or_moderator(user):
    return _is_active(user) and _is_admin_or_moderator(user)


def _same_users(user_a, user_b):
    return user_a is not None and user_b is not None \
        and user_a.user_id == user_b.user_id


def _is_post_author(user, post):
    return user is not None and post is not None \
        and user.user_id == post.user_id


def _is_active_post_author(user, post):
    return _is_active(user) and _is_post_author(user, post)


def _is_topic_author(user, topic):
    return user is not None and topic is not None \
        and user.user_id == topic.user_id


def _is_active_topic_author(user, topic):
    return _is_active(user) and _is_topic_author(user, topic)


def _is_pinned(topic):
    return topic is not None and topic.status == 'pinned'


def _is_published(topic_or_post):
    return topic_or_post is not None and topic_or_post.status == 'published'


def _is_postable(topic):
    return _is_pinned(topic) or _is_published(topic)


class Permission:
    def is_granted(self, user):
        return False

    def check(self, user):
        if not self.is_granted(user):
            raise PermissionError('user not allowed to perform action')


class PermissionOnTarget(Permission):
    def __init__(self, target):
        self.target = target


class EditTarget(PermissionOnTarget):
    def __init__(self, target, attributes='any'):
        super().__init__(target)
        if isinstance(attributes, str):
            assert attributes in {'any'}
            attributes = _get_attributes(target.__class__)
        self.attributes = attributes


class DeleteTarget(PermissionOnTarget):
    pass


class CreateInTarget(PermissionOnTarget):
    pass


_USER_PARAMS_ONLY_FOR_ADMIN = {
    'created_at',
    'roles',
    'status',
    'n_posts',
    'n_topics',
}


class CreateUser(Permission):
    def __init__(self, attributes):
        self.attributes = attributes

    def is_granted(self, user=None):
        return not _USER_PARAMS_ONLY_FOR_ADMIN & self.attributes


class EditUser(EditTarget):
    def is_granted(self, user):
        if not _is_active(user):
            return False
        elif _same_users(user, self.target):
            return not _USER_PARAMS_ONLY_FOR_ADMIN & self.attributes
        else:
            return _is_admin(user)


class DeleteUser(DeleteTarget):
    def is_granted(self, user):
        return _same_users(user, self.target) or _is_active_admin(user)


class CreateAvatar(Permission):
    def is_granted(self, user):
        return _is_active_admin(user)


class EditAvatar(EditTarget):
    def is_granted(self, user):
        return _is_active_admin(user)


class DeleteAvatar(DeleteTarget):
    def is_granted(self, user):
        return _is_active_admin(user)


class CreateSubforum(Permission):
    def is_granted(self, user):
        return _is_active_admin(user)


class EditSubforum(EditTarget):
    def is_granted(self, user):
        return _is_active_admin(user)


class DeleteSubforum(DeleteTarget):
    def is_granted(self, user):
        return _is_active_admin(user)


class CreateTopicInSubforum(CreateInTarget):
    def is_granted(self, user):
        return _is_active(user)


class EditTopic(EditTarget):
    def is_granted(self, user):
        if not _is_active(user):
            return False
        elif _is_topic_author(user, self.target):
            return _is_postable(self.target)
        else:
            return _is_admin_or_moderator(user)


class DeleteTopic(DeleteTarget):
    def is_granted(self, user):
        if not _is_active(user):
            return False
        elif _is_topic_author(user, self.target):
            return True
        else:
            return _is_admin_or_moderator(user)


class CreatePostInTopic(CreateInTarget):
    def is_granted(self, user):
        if not _is_active(user):
            return False
        else:
            return _is_postable(self.target) or _is_admin_or_moderator(user)


class EditPost(EditTarget):
    def is_granted(self, user):
        if not _is_active(user):
            return False
        elif _is_post_author(user, self.target):
            return _is_published(self.target)
        else:
            return _is_admin_or_moderator(user)


class DeletePost(DeleteTarget):
    def is_granted(self, user):
        if not _is_active(user):
            return False
        elif _is_post_author(user, self.target):
            return True
        else:
            return _is_admin_or_moderator(user)


class BypassAntiFlood(Permission):
    def is_granted(user):
        return _is_active_admin_or_moderator(user)
