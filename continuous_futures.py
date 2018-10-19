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
    future_chain_predicates : dict
        A dict mapping root symbol to a predicate function which accepts a contract
    as a parameter and returns whether or not the contract should be included in the
    chain.
    """

    def __init__(self, root_symbol=None):
        self.root_symbol = root_symbol

        @property
        def contracts:
            return 
