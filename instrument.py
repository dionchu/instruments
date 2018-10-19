from trading_calendars import get_calendar

class Instrument(object):
    """
    An Instrument represents the metadata of a symbol
    """
    _kwargnames = frozenset({
        'symbol_id',
        'instrument_name',
        'instrument_country_id',
        'asset_class_id',
        'settle_start',
        'settle_end',
        'settle_method',
        'settle_timezone',
#        'first_traded',
        'auto_close_date',
        'quote_currency_id',
        'multiplier',
        'tick_size',
        'start_date',
        'end_date',
    })

    def __init__(self,
                symbol_id="",
                instrument_name="",
                instrument_country_id="",
                asset_class_id="",
                settle_start=None,
                settle_end=None,
                settle_method=None,
                settle_timezone=None,
                exchange_info=None,
#                first_traded=None,
                auto_close_date=None,
                quote_currency_id="",
                multiplier=1,
                tick_size=0.01,
                start_date=None,
                end_date=None):

        self.symbol_id = symbol_id
        self.instrument_name = instrument_name
        self.instrument_country_id = instrument_country_id
        self.asset_class_id = asset_class_id
        self.settle_start = settle_start
        self.settle_end = settle_end
        self.settle_method = settle_method
        self.settle_timezone = settle_timezone
#        self.first_traded = first_traded
        self.auto_close_date = auto_close_date
        self.quote_currency_id = quote_currency_id
        self.multiplier = multiplier
        self.tick_size = tick_size
        self.start_date = start_date
        self.end_date = end_date

    @property
    def exchange(self):
        return self.exchange_info.canonical_name

    @property
    def exchange_full(self):
        return self.exchange_info.name

    @property
    def exchange_country_id(self):
        return self.exchange_info.exchange_country_id

    @property
    def exchange_financial_center(self):
        return self.exchange_info.exchange_financial_center

    @property
    def exchange_timezone(self):
        return self.exchange_info.exchange_timezone

    ## Quantopian has some equality checkers not implements here

    def __repr__(self):
        if self.symbol:
            return '%s(%s [%s])' % (type(self).__name__, self.symbol_id, self.instrument_name)
        else:
            return '%s(%s)' % (type(self).__name__, self.symbol_id
            )

    ## Quantopian has some function used by pickle to determine how to serialize/deserialized this class

    def to_dict(self):
        """
        Convert to a python dict.
        """
        return {
            'symbol_id': self.symbol,
            'instrument_name': self.instrument_name,
            'instrument_country_id': self.instrument_country_id
            'asset_class_id': self.asset_class_id,
            'settle_start': self.settle_start,
            'settle_end': self.settle_end,
            'settle_timezone': self.settle_timezone,
#            'first_traded': self.first_traded,
            'auto_close_date': self.auto_close_date,
            'quote_currency_id': self.quote_currency_id,
            'multiplier': self.price_multiplier,
            'tick_size': self.tick_size,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'exchange_info': self.exchange_info,
            'exchange': self.exchange,
            'exchange_full': self.exchange_full,
            'exchange_financial_center': self.exchange_financial_center,
            'exchange_country_id': self.exchange_country_id,
            'exchange_timezone': self.exchange_financial_center,
        }

    @classmethod
    def from_dict(cls, dict_):
        """
        Build an Asset instance from a dict.
        """
        return cls(**{k: v for k, v in dict_.items() if k in cls._kwargnames})

    def is_alive_for_session(self, session_label):
        """
        Returns whether the asset is alive at the given dt.
        Parameters
        ----------
        session_label: pd.Timestamp
            The desired session label to check. (midnight UTC)
        Returns
        -------
        boolean: whether the asset is alive at the given dt.
        """

        ref_start = self.start_date.value
        ref_end = self.end_date.value

        return ref_start <= session_label.value <= ref_end

    def is_exchange_open(self, dt_minute):
        """
        Parameters
        ----------
        dt_minute: pd.Timestamp (UTC, tz-aware)
            The minute to check.
        Returns
        -------
        boolean: whether the asset's exchange is open at the given minute.
        """
        calendar = get_calendar(self.exchange)
        return calendar.is_open_on_minute(dt_minute)

class Future(Instrument):

    _kwargnames = frozenset({
        'symbol_id',
        'root_symbol',
        'instrument_name',
        'instrument_country_id',
        'asset_class_id',
        'settle_start',
        'settle_end',
        'settle_method',
        'settle_timezone',
        'final_settle_start',
        'final_settle_end',
        'final_settle_method',
        'final_settle_timezone',
        'last_trade_time'
#        'first_traded',
        'quote_currency_id',
        'multiplier',
        'tick_size',
        'start_date',
        'end_date',
        'first_trade',
        'last_trade',
        'first_position',
        'last_position',
        'first_notice_date',
        'last_notice_date',
        'first_delivery_date',
        'last_delivery_date',
        'settlement_date',
        'volume_switch_date',
        'open_interest_switch_date',
        'auto_close_date',
        'delivery_month',
        'delivery_year',
    })
