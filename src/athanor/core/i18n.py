def _gettext(message:str):return message
def _(message:str)->str:return _gettext(message)


def setup_i18n():
    import os
    import gettext
    import locale
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import GLib #type:ignore
    from athanor.config import APP_ID,LOCALE_DIR
    import logging
    logger=logging.getLogger()

    if not os.path.exists(LOCALE_DIR):
        logger.warning(f"Locale directory not found at: {LOCALE_DIR}")

    locale.setlocale(locale.LC_ALL, '')

    gettext.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.textdomain(APP_ID)

    locale.bindtextdomain(APP_ID, LOCALE_DIR)
    locale.textdomain(APP_ID)

    global _
    _=gettext.gettext
    global _gettext
    _gettext=gettext.gettext

    logger.info(f"I18n initialized for {APP_ID} at {LOCALE_DIR}")
    logger.info(_("i18n ok"))
