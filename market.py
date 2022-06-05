from period_constants import DAYS_PER_YEAR, DAYS_PER_MONTH, MONTHS_PER_YEAR
from time_period_parameters import TimePeriodParameters
import numpy as np

BIAS_LOW = -0.1
BIAS_HIGH = 0.2
VOLATILITY_AVG = 0.1
VOLATILITY_STD = 0.1


class Market:

    def __init__(self, num_years=10, starting_value=100) -> None:
        self.num_years = num_years
        self.num_months = self.num_years * 12
        self.num_days = self.num_years * MONTHS_PER_YEAR * DAYS_PER_MONTH
        self.starting_value = starting_value

        self.generate_market_behavior()

    def generate_market_behavior(self):
        # Each period is dominated by a (tendentially positive)
        # mix of a bias term, a random term, and a sinusoidal term

        market_behavior = np.zeros(self.num_days)
        market_behavior[-1] = self.starting_value

        day = 0
        for _ in range(self.num_years):
            yearly_parameters = TimePeriodParameters(max_days=DAYS_PER_YEAR,
                                                     bias_low=BIAS_LOW,
                                                     bias_high=BIAS_HIGH,
                                                     volatility_avg=VOLATILITY_AVG,
                                                     volatility_std=VOLATILITY_STD,
                                                     sin_max_period=DAYS_PER_YEAR / 2)
            for _ in range(MONTHS_PER_YEAR):
                monthly_parameters = TimePeriodParameters(max_days=DAYS_PER_MONTH,
                                                          bias_low=BIAS_LOW,
                                                          bias_high=BIAS_HIGH,
                                                          volatility_avg=VOLATILITY_AVG,
                                                          volatility_std=VOLATILITY_STD,
                                                          sin_max_period=DAYS_PER_MONTH / 2)
                for _ in range(DAYS_PER_MONTH):
                    daily_parameters = TimePeriodParameters(max_days=1,
                                                            bias_low=BIAS_LOW,
                                                            bias_high=0.02,
                                                            volatility_avg=VOLATILITY_AVG,
                                                            volatility_std=VOLATILITY_STD,
                                                            last_val=market_behavior[day - 1])

                    market_behavior[day] = market_behavior[day - 1] \
                                           + next(yearly_parameters.probe_trend()) \
                                           + next(monthly_parameters.probe_trend()) \
                                           + next(daily_parameters.probe_trend())

                    market_behavior[day] = max(market_behavior[day], 0)

                    day += 1

        self.market_behavior = market_behavior

    def get_share_value(self, day: int) -> float:
        return self.market_behavior[day]
