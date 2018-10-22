import pandas as pd
from collections import deque
from trading_calendars.utils.memoize import lazyval
from .financial_center_info import FinancialCenterInfo
from .exchange_info import ExchangeInfo
from .country_info import CountryInfo
from .errors import (
    SymbolsNotFound
)

import os
dirname = os.path.dirname(__file__)

FUT_CODE_TO_MONTH = dict(zip('FGHJKMNQUVXZ', range(1, 13)))
MONTH_TO_FUT_CODE = dict(zip(range(1, 13), 'FGHJKMNQUVXZ'))

class InstrumentFinder(object):
    """
    An InstrumentFinder is an interface to a database of Asset metadata written by
    an ``AssetDBWriter``.
    This class provides methods for looking up assets by unique integer id or
    by symbol.  For historical reasons, we refer to these unique ids as 'sids'.
    Parameters
    ----------
    engine : str or SQLAlchemy.engine
        An engine with a connection to the asset database to use, or a string
        that can be parsed by SQLAlchemy as a URI.
    future_chain_predicates : dict
        A dict mapping future root symbol to a predicate function which accepts
    a contract as a parameter and returns whether or not the contract should be
    included in the chain.
    See Also
    --------
    :class:`zipline.assets.AssetDBWriter`
    """

    def __init__(self):
        self._country_code = pd.read_csv(dirname + "\..\shogun_database\_CountryCode.csv", keep_default_na=False)
        self._asset_class = pd.read_csv(dirname + "\..\shogun_database\_AssetClass.csv")
        self._currency_code = pd.read_csv(dirname + "\..\shogun_database\_CurrencyCode.csv")
        self._exchange_code = pd.read_csv(dirname + "\..\shogun_database\_ExchangeCode.csv")
        self._financial_center = pd.read_csv(dirname + "\..\shogun_database\_FinancialCenter.csv")
        self._future_contract_listing = pd.read_csv(dirname + "\..\shogun_database\_FutureRootContractListingTable.csv")
        self._future_root = pd.read_csv(dirname + "\..\shogun_database\_FutureRootTable.csv")
        self._future_instrument = pd.read_csv(dirname + "\..\shogun_database\_FutureInstrument.csv")
        self._instrument_cache = {}
        self.get_ordered_contracts = {}

    @lazyval
    def country_info(self):
        out = {}
        for index, row in self._country_code.iterrows():
            out[row['country_name']] = CountryInfo(row['country_name'], row['country_code'], row['country_code3'], row['region'])
        return out

    @lazyval
    def financial_center_info(self):
        out = {}
        for index, row in self._financial_center.iterrows():
            out[row['financial_center']] = FinancialCenterInfo(row['financial_center'], self.country_info[row['country_id']], row['timezone'])
        return out

    @lazyval
    def exchange_info(self):
        out= {}
        for index, row in self._exchange_code.iterrows():
            out[row['exchange_full']] = ExchangeInfo(row['exchange_full'], row['mic'], self.financial_center_info[row['financial_center_id']])
        return out

    def get_ordered_contracts(self, root_symbol, active=1):
        try:
            return self.get_ordered_contracts[root_symbol]
        except KeyError:
            contract_exchange_symbols = self._get_contract_exchange_symbols(root_symbol)
            contracts = deque(self.retrieve_all(contract_exchange_symbols))
            oc = OrderedContracts(root_symbol, contracts, active)
            self._ordered_contracts[root_symbol] = oc
            return oc

    # May need to implement some sorting
    def _get_contract_exchange_symbols(self, root_symbol):
        return list(self._future_instrument[
                self._future_instrument['root_symbol'] == root_symbol
                ]['exchange_symbol'])

    def retrieve_all(self, exchange_symbols, default_none=False):
        """
        Retrieve all assets in `exchange_symbols`.
        Parameters
        ----------
        exchange_symbols : list of strings
            Assets to retrieve.
        default_none : bool
            If True, return None for failed lookups.
            If False, raise `SymbolsNotFound`.
        Returns
        -------
        instruments : list[Instrument or None]
            A list of the same length as `exchange_symbols` containing Instruments (or Nones)
            corresponding to the requested exchange symbols.
        Raises
        ------
        SymbolsNotFound
            When a requested exchange_symbol is not found and default_none=False.
        """
        hits, missing, failures = {}, set(), []
        for exchange_symbol in exchange_symbols:
            try:
                instrument = self._instrument_cache[exchange_symbol]
                if not default_none and instrument is None:
                    # Bail early if we've already cached that we don't know
                    # about an asset.
                    raise SymbolsNotFound(exchange_symbols=[exchange_symbol])
                hits[exchange_symbol] = instrument
            except KeyError:
                missing.add(exchange_symbol)

        # All requests were cache hits. Return requested exchange_symbols in order.
        if not missing:
            return [hits[exchange_symbol] for exchange_symbol in exchange_symbols]

        update_hits = hits.update

        # Look up cache misses by type.


    def group_by_type(self, exchange_symbols):
        """
        Group a list of exchange_symbols by instrument type.
        Parameters
        ----------
        exchange_symbols : list[str]
        Returns
        -------
        types : dict[str or None -> list[str]]
            A dict mapping unique instrument types to lists of exchange_symbols
            drawn from exchange_symbols. If we fail to look up an asset, we
            assign it a key of None.
        """
        return invert(self.lookup_instrument_types(exchange_symbols))

    def lookup_instrument_types(self, exchange_symbols):
        """
        Retrieve instrument types for a list of exchange_symbols.
        Parameters
        ----------
        exchange_symbols : list[str]
        Returns
        -------
        types : dict[exchange_symbols -> str or None]
            Instrument types for the provided exchange_symbols.
        """
        found = {}
        missing = set()

        for exchange_symbol in exchange_symbols:
            try:
                found[exchange_symbol] = self._instrument_type_cache[exchange_symbol]
            except KeyError:
                missing.add(exchange_symbol)

        if not missing:
            return found

        
