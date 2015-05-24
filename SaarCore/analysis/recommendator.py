class recommendator(object):
    """recommendator of stocks"""

    def __init__(self,scheme):
        self.scheme = scheme

    def get_daliy_stocks(self):
        '''recommend stocks base on user's scheme'''
        pass

    def get_stock_last_operate_date(self,stock):
        pass    

    def should_buy_remains(self,stock,day):
        '''if stock's price hit the profit limit or loss limit'''
        assert stock.state == stock_state.open_position
        if day == stock.prices.index[0]:
            return False

        buy_price = stock.prices.Close[stock.last_operate_date]
        profit = (stock.prices.Close[day] - buy_price)/buy_price 
        return profit >= self.scheme.additional_investment_condition

    def should_sell(self,stock,day):
        '''if stock's price hit the profit limit or loss limit'''
        assert stock.state != stock_state.close_position
        
        if (day - stock.buy_date).days >= self.scheme.holding_cycles:
            return True
        
        price = stock.prices.Close[day]
        buy_price = stock.prices.Close[stock.last_operate_date]
        profit = (price - buy_price ) / buy_price
        return profit >= self.scheme.profit_limit or profit <= -self.scheme.loss_limit

    def should_sell_remains(self,stock,day):
        '''if stock's price hit the additional_investment condition'''
        assert stock.state != stock_state.close_position
        
        if self.should_sell(stock,day):
            return True
        
        price = stock.prices.Close[day]
        buy_price = stock.prices.Close[stock.last_operate_date]
        loss = -(price - buy_price ) / buy_price
        return loss >= self.scheme.additional_investment_condition
