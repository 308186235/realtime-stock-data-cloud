import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    All strategy implementations should inherit from this class and implement the required methods.
    """
    
    def __init__(self, parameters=None):
        """
        Initialize the strategy with parameters.
        
        Args:
            parameters (dict): Strategy parameters
        """
        self.parameters = parameters or {}
        self.name = "Base Strategy"
        self.description = "Abstract base strategy"
    
    @abstractmethod
    def generate_signals(self, data):
        """
        Generate trading signals based on market data.
        
        Args:
            data (pd.DataFrame): Historical market data
            
        Returns:
            pd.Series: Series of trading signals (1 for buy, -1 for sell, 0 for hold)
        """
        pass
    
    @abstractmethod
    def get_default_parameters(self):
        """
        Get default parameters for the strategy.
        
        Returns:
            dict: Default parameters
        """
        pass
    
    @abstractmethod
    def get_parameter_ranges(self):
        """
        Get valid ranges for strategy parameters, used for optimization.
        
        Returns:
            dict: Parameter ranges with min, max, and step values
        """
        pass 