from django.conf import settings
import tess_core.settings as core_settings

# COVER_PLACEHOLDER_IMG = 'media/assets/no-book.jpg'
DEFAULT_COVER_PLACEHOLDER_IMG = f'{settings.MEDIA_ROOT}assets/no-book.jpg'
DEFAULT_COVERS_FOLDER = 'covers'
DEFAULT_PREVIEW_FOLDER = 'previews'
DEFAULT_PREVIEW_PREFIX = 'preview'
DEFAULT_TMP_DIR = '/tmp'
DEFAULT_LEASE_DURATION = 7


def get_setting(name):
    """
    Get configured Django setting or the app's builtin.
    :param name: setting name without the `ROUTER_` prefix.
    :return: value for setting: ROUTER_*.
    """

    from django.conf import settings

    return {
        'COVER_PLACEHOLDER_IMG': getattr(settings, 'BOOKS_COVER_PLACEHOLDER_IMG', DEFAULT_COVER_PLACEHOLDER_IMG),
        'COVERS_FOLDER': getattr(settings, 'BOOKS_COVERS_FOLDER', DEFAULT_COVERS_FOLDER),

        'PREVIEW_FOLDER': getattr(settings, 'BOOKS_PREVIEW_FOLDER', DEFAULT_PREVIEW_FOLDER),
        'PREVIEW_PREFIX': getattr(settings, 'BOOKS_PREVIEW_PREFIX', DEFAULT_PREVIEW_PREFIX),
        'TMP_DIR': getattr(settings, 'BOOKS_TMP_DIR', DEFAULT_TMP_DIR),
        'LEASE_DURATION': getattr(settings, 'BOOKS_LEASE_DURATION', DEFAULT_LEASE_DURATION),
        'SYNOPSIS_LEN': core_settings.SYNOPSIS_LEN

    }.get(name)
