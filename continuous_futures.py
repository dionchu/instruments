from functools import partial

from numpy import array, empty, iinfo
from pandas import Timestamp
from .trading_calendars import get_calendar
import warnings

def delivery_predicate(codes, contract):
    # This relies on symbols that are construct following a pattern of
    # root symbol + delivery code + year, e.g. PLF16
    # This check would be more robust if the future contract class had
    # a 'delivery_month' member.
    delivery_code = contract.symbol[-3]
    return delivery_code in codes

class ContractNode(object):
    def __init__(self, contract):
        self.contract = contract
        self.prev = None
        self.next = None

        def __rshift__(self, offset):
            i = 0
            curr = self
            while i < offset and curr is not None:
                curr = curr.next
                i += 1
            return curr

        def __lshift__(self, offset):
            i = 0
            curr = self
            while i < offset and curr is not None:
                curr = curr.prev
                i += 1
            return curr

class OrderedContracts(object):
    """
    A container for aligned values of a future contract chain, in sorted order
    of their occurrence.
    Used to get answers about contracts in relation to their auto close
    dates and start dates.
    Members
    -------
    root_symbol : str
        The root symbol of the future contract chain.
    contracts : deque
        The contracts in the chain in order of occurrence.
    start_dates : long[:]
        The start dates of the contracts in the chain.
        Corresponds by index with contract_sids.
    auto_close_dates : long[:]
        The auto close dates of the contracts in the chain.
        Corresponds by index with contract_sids.
    chain_predicates : dict
        A dict mapping root symbol to a predicate function which accepts a contract
    as a parameter and returns whether or not the contract should be included in the
    chain.
    """

    def __init__(self, root_symbol, contracts, active=True):
        self._future_contract_listing = pd.read_csv(dirname + "\..\_FutureRootContractListingTable.csv")

        self.root_symbol = root_symbol

        self.exchange_symbol_to_contract = {}

        self._start_date = iinfo('int64').max
        self._end_date = 0

        # assumes that root_symbol is in table, need a check here
        if active:
            chain_predicate = partial(delivery_predicate,
                set(self._future_contract_listing[
                    (self._future_contract_listing['root_id'] == self.root_symbol) &
                    (self._future_contract_listing['active'] == 1)
                    ]['delivery_month']))
        else:
            chain_predicate = partial(delivery_predicate,
                set(self._future_contract_listing[
                    (self._future_contract_listing['root_id'] == self.root_symbol)
                    ]['delivery_month']))

        self._head_contract = None
        prev = None
        while contracts:
            contract = contracts.popleft()

            # It is possible that the first contract in our list has a start
            # date on or after its auto close date. In that case the contract
            # is not tradable, so do not include it in the chain.
            if prev is None and contract.start_date >= contract.auto_close_date:
                continue

            if not chain_predicate(contract):
                continue

            self._start_date = min(contract.start_date.value, self._start_date)
            self._end_date = max(contract.end_date.value, self._end_date)

            curr = ContractNode(contract)
            self.exchange_symbol_to_contract[contract.exchange_symbol] = curr
            if self._head_contract is None:
                self._head_contract = curr
                prev = curr
                continue
            curr.prev = prev
            prev.next = curr
            prev = curr

    def contract_before_auto_close(self, dt_value):
        """
        Get the contract with next upcoming auto close date.
        """
        curr = self._head_contract
        while curr.next is not None:
            if curr.contract.auto_close_date > dt_value:
                break
            curr = curr.next
        return curr.contract.root_symbol

    def contract_at_offset(self, exchange_symbol, offset, start_cap):
        """
        Get the exchange_symbol which is the given exchange_symbol plus the offset distance.
        An offset of 0 should be reflexive.
        """
        curr = self.exchange_symbol_to_contract[exchange_symbol]
        i = 0
        while i < offset:
            if curr.next is None:
                return None
            curr = curr.next
            i += 1
        if curr.contract.start_date.value <= start_cap:
            return curr.contract.exchange_symbol
        else:
            return None

    def active_chain(self, starting_exchange_symbol, dt_value):
        curr = self.exchange_to_contract[starting_exchange_symbol]
        contracts = []

        while curr is not None:
            if curr.contract.start_date.value <= dt_value:
                contracts.append(curr.contract.exchange_symbol)
            curr = curr.next

        return array(contracts, dtype='str')

    @property
    def start_date(self):
        return Timestamp(self._start_date, tz='UTC')

    @property
    def end_date(self):
        return Timestamp(self._end_date, tz='UTC')
