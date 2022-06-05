import numpy as np

from period_constants import DAYS_PER_MONTH


class TimePeriodParameters:

    def __init__(self,
                 max_days,
                 bias_low,
                 bias_high,
                 volatility_avg,
                 volatility_std,
                 sin_max_period=None,
                 last_val=None):
        self.max_days = max_days
        self.bias = np.random.uniform(bias_low, bias_high)
        self.random = np.random.normal(volatility_avg, volatility_std)
        if np.random.rand() > 0.95 and max_days < DAYS_PER_MONTH and last_val:
            self.random = np.random.choice([-1, 1]) * np.random.exponential(0.3) * 0.1 * last_val
        self.sinusoidal_amplitude = np.random.normal(volatility_avg, volatility_std)
        self.sinusoidal_period = np.random.uniform(0, sin_max_period) if sin_max_period else 1
        self.sinusoidal_phase = np.random.uniform(0, 2 * np.pi)

        self.day = 0

    def probe_trend(self):
        while self.day < self.max_days:
            value = self.bias \
                    + self.random \
                    + self.sinusoidal_amplitude * np.sin(self.day / self.sinusoidal_period * 2 *
                                                                                 np.pi + self.sinusoidal_phase)
            yield value
            self.day += 1
