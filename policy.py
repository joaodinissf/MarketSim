import abc
from market import Market
from period_constants import *


class Policy(abc.ABC):

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        self.STARTING_BALANCE = 10000
        self.balance = self.STARTING_BALANCE
        self.monthly_income = 3500
        self.monthly_ratio_invest = 0.15
        self.num_shares = 0

    def buy(self, market: Market, day: int, value: float):
        share_value = market.get_share_value(day)
        if value > self.balance or value <= 0:
            return

        self.balance -= value
        self.num_shares += value / share_value

    def sell(self, market: Market, day: int, num_shares: float):
        share_value = market.get_share_value(day)
        if num_shares > self.num_shares or num_shares <= 0:
            return

        self.balance += share_value * num_shares
        self.num_shares -= num_shares

    def pay_salary(self) -> None:
        self.balance += self.monthly_income

    def get_name(self) -> str:
        return self.name

    def get_total_balance(self, share_value: float):
        return self.balance + self.num_shares * share_value

    def decide(self, market: Market, day: int):
        if self.pre_decide(market, day):
            self.post_decide(market, day)

    def pre_decide(self, market: Market, day: int):
        # Decide whether to skip this day
        if market.get_share_value(day) <= 0:
            return False

        return True

    @abc.abstractmethod
    def post_decide(self, market: Market, day: int):
        pass
