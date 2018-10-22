from textwrap import dedent

from trading_calendars.utils.memoize import lazyval

class ShogunError(Exception):
    msg = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @lazyval
    def message(self):
        return str(self)

    def __str__(self):
        msg = self.msg.format(**self.kwargs)
        return msg

    __unicode__ = __str__
    __repr__ = __str__


class SymbolsNotFound(ShogunError):
    """
    Raised when a retrieve_asset() or retrieve_all() call contains a
    non-existent sid.
    """
    @lazyval
    def plural(self):
        return len(self.sids) > 1

    @lazyval
    def sids(self):
        return self.kwargs['exchange_symbols']

    @lazyval
    def msg(self):
        if self.plural:
            return "No instruments found for exchange symbols: {exchange_symbols}."
        return "No instrument found for exchange_symbol: {exchange_symbols[0]}."
