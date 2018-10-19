import pandas as pd
from trading_calendars.utils.memoize import lazyval
from .financial_center_info import FinancialCenterInfo
from .exchange_info import ExchangeInfo

CountryCode = pd.read_csv(".\shogun\shogun\database\CountryCode.csv")
AssetClass = pd.read_csv(".\shogun\shogun\database\AssetClass.csv")
CurrencyCode = pd.read_csv(".\shogun\shogun\database\CurrencyCode.csv")
ExchangeCode = pd.read_csv(".\shogun\shogun\database\ExchangeCode.csv")
FinancialCenter = pd.read_csv(".\shogun\shogun\database\FinancialCenter.csv")
FinancialInstrumentTableDirectory = pd.read_csv(".\shogun\shogun\database\FinancialInstrumentTableDirectory.csv")
Forex = pd.read_csv(".\shogun\shogun\database\Forex.csv")
FutureRootContractListingTable = pd.read_csv(".\shogun\shogun\database\FutureRootContractListingTable.csv")
FutureRootTable = pd.read_csv(".\shogun\shogun\database\FutureRootTable.csv")

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
        self._country_code = pd.read_csv(".\database\CountryCode.csv", keep_default_na=False)
        self._asset_class = pd.read_csv(".\database\AssetClass.csv")
        self._currency_code = pd.read_csv(".\database\CurrencyCode.csv")
        self._exchange_code = pd.read_csv(".\database\ExchangeCode.csv")
        self._financial_center = pd.read_csv(".\database\FinancialCenter.csv")
        self._future_contract_listing = pd.read_csv(".\database\FutureRootContractListingTable.csv")
        self._future_root = pd.read_csv(".\database\FutureRootTable.csv")

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
