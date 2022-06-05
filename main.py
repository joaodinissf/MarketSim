import enum
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from market import Market
from period_constants import DAYS_PER_MONTH
from policy import Policy


class MonkeyInVest(Policy):
    # Sometimes may be buy,
    # sometimes may be sell

    def __init__(self) -> None:
        super().__init__('MonkeyInVest')

    def post_decide(self, market: Market, day: int):
        if np.random.rand() < 0.5:
            self.buy(market, day, min(100, self.balance))
        else:
            self.sell(market, day, min(1, self.num_shares))


class DeltaCostAveraging(Policy):

    def __init__(self) -> None:
        super().__init__('DeltaCostAveraging')
        self.bought_amount = []
        self.bought_at = []

    def longest_average_buy_at(self, value: float) -> float:
        HAPPY_FACTOR = 1.1  # If we are winning 10% on the investment, cash out

        streak_at = np.zeros(len(self.bought_at))
        streak_amt = np.zeros(len(self.bought_amount))

        safe_to_sell = 0

        for ix, (b_at, b_amt) in enumerate(zip(self.bought_at, self.bought_amount)):
            streak_at[ix] = b_at
            streak_amt[ix] = b_amt

            average = sum(streak_at * streak_amt) / sum(streak_amt)

            if average * HAPPY_FACTOR <= value:
                safe_to_sell += b_amt
            else:
                break

        return safe_to_sell

    def post_decide(self, market: Market, day: int):
        if day == 0:
            # On the first day, buy in with 10% of the total balance
            amount_to_invest = self.balance * 0.1
            self.bought_amount.append(amount_to_invest / market.get_share_value(day))
            self.bought_at.append(market.get_share_value(day))
            self.buy(market, day, amount_to_invest)
        elif day % 30 == 0:
            # Unconditionally buy, every month after the first,
            # with self.monthly_income of the monthly income
            amount_to_invest = self.monthly_income * self.monthly_ratio_invest
            self.bought_amount.append(amount_to_invest / market.get_share_value(day))
            self.bought_at.append(market.get_share_value(day))
            self.buy(market, day, amount_to_invest)

        # Attempt to sell
        if self.num_shares > 0:
            self.sell(market, day, self.longest_average_buy_at(market.get_share_value(day)))


class DailyCostAveraging(Policy):

    def __init__(self) -> None:
        super().__init__('DailyCostAveraging')

    def post_decide(self, market: Market, day: int):
        if day == 0:
            # On the first day, buy in with 10% of the total balance
            self.buy(market, day, self.balance * 0.1)
        elif day % 30 == 0:
            # Unconditionally buy, every month after the first,
            # with self.monthly_income of the monthly income
            self.buy(market, day, self.monthly_income * self.monthly_ratio_invest)


def main():
    market = Market()

    num_runs = 100

    fig, ax = plt.subplots()
    plt.ion()
    plt.show(block=False)

    best_policies = []

    for _ in tqdm(range(num_runs)):
        # Generate market behaviour
        market.generate_market_behavior()
        ax.plot(range(market.num_days), market.market_behavior, linewidth=1.5)
        plt.draw()
        plt.pause(0.00001)

        policies = [
            MonkeyInVest(),
            DailyCostAveraging(),
            DeltaCostAveraging(),
        ]

        for pol in policies:
            for d in range(market.num_days):
                if d % DAYS_PER_MONTH == 0:
                    pol.pay_salary()

                pol.decide(market, d)

            best_policies.append(
                (pol.get_name(), pol.get_total_balance(market.get_share_value(-1)), pol.balance, pol.num_shares))

    best_policies.sort(key=lambda x: x[1], reverse=True)
    print(f'Best policy: {best_policies[0][0]}')
    print(f'Best balance: {best_policies[0][1]}')
    print('===')
    print(f'Worst policy: {best_policies[-1][0]}')
    print(f'Worst balance: {best_policies[-1][1]}')
    print('===')
    for ix, pol in enumerate(best_policies):
        print(f'{ix + 1}. {pol}')

    fig_pols, ax_pols = plt.subplots()
    x = [[p.get_name() for p in policies].index(n) for n, _, _, _ in best_policies]
    y = np.array(range(len(best_policies)))
    ax_pols.set_xticks(range(len([p.get_name() for p in policies])), labels=[p.get_name() for p in policies])
    ax_pols.set_yticks(range(1, len(y) + 1))
    ax_pols.scatter(x, y + 1)

    fig_pols_hist, ax_pols_hist = plt.subplots()
    ax_pols_hist.hist([p[1] for p in best_policies], bins=50)

    plt.show(block=True)


if __name__ == '__main__':
    main()
